import sqlite3
import pandas as pd

print("Connecting to database...")
conn = sqlite3.connect("bayou_doe.db")

# Load clustered matches with strength
matches = pd.read_sql_query("""
SELECT
    mc.match_id,
    mc.cluster_id,
    mc.cluster_size,
    m.cm_total,
    m.tree_confidence
FROM match_clusters mc
JOIN matches m ON m.match_id = mc.match_id
""", conn)

# Load surname + geo signals
surnames = pd.read_sql_query("""
SELECT cluster_id, last_name, surname_count
FROM v_surnames_by_cluster
""", conn)

geo = pd.read_sql_query("""
SELECT cluster_id, state, parish_or_county, people_count
FROM v_geo_by_cluster
WHERE state = 'LA'
""", conn)

print("Data loaded.")

# ---------------------------
# Candidate scoring logic
# ---------------------------

# Simulated candidate pool based on cluster ancestry mix
candidates = []

for cid in matches["cluster_id"].unique():
    cluster_df = matches[matches["cluster_id"] == cid]

    avg_cm = cluster_df["cm_total"].mean()
    avg_conf = cluster_df["tree_confidence"].mean()
    size = cluster_df["cluster_size"].iloc[0]

    surname_strength = surnames[surnames["cluster_id"] == cid]["surname_count"].sum()
    geo_strength = geo[geo["cluster_id"] == cid]["people_count"].sum()

    score = (
        avg_cm * 0.35 +
        avg_conf * 100 * 0.20 +
        size * 0.15 +
        surname_strength * 0.15 +
        geo_strength * 0.15
    )

    candidates.append({
        "cluster_id": cid,
        "avg_cm": round(avg_cm, 2),
        "tree_conf_avg": round(avg_conf, 3),
        "cluster_size": size,
        "surname_signal": surname_strength,
        "geo_signal": geo_strength,
        "candidate_score": round(score, 2)
    })

candidates_df = pd.DataFrame(candidates)
candidates_df = candidates_df.sort_values(by="candidate_score", ascending=False)

print("\nCandidate ranking:")
print(candidates_df)

# Save outputs
candidates_df.to_sql("candidate_rankings", conn, if_exists="replace", index=False)
candidates_df.to_csv("forensic_genetic_genealogy/data/processed/ranked_candidate_pool.csv", index=False)

conn.close()

print("\nDONE.")
print("Saved to SQLite table: candidate_rankings")
print("Saved CSV: data/processed/ranked_candidate_pool.csv")
