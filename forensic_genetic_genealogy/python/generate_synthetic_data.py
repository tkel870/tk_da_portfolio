"""
Synthetic FGG Dataset Generator (Bayou Doe - Louisiana, fictional)

Creates CSVs in forensic_genetic_genealogy/data/raw:
- places.csv
- matches.csv
- shared_matches.csv
- persons.csv
- relationships.csv
- match_tree_links.csv
"""

from __future__ import annotations
import os, random
import pandas as pd

try:
    import numpy as np
except ImportError:
    np = None

SEED = 870
random.seed(SEED)
if np is not None:
    np.random.seed(SEED)

KIT_ID = "BAYOU_DOE_01"

LA_PLACES = [
    ("LA_ORLEANS_NO", "New Orleans", "Orleans Parish", "LA", "USA", 29.9511, -90.0715),
    ("LA_EBR_BTR", "Baton Rouge", "East Baton Rouge Parish", "LA", "USA", 30.4515, -91.1871),
    ("LA_LAFAYETTE", "Lafayette", "Lafayette Parish", "LA", "USA", 30.2241, -92.0198),
    ("LA_CALCASIEU", "Lake Charles", "Calcasieu Parish", "LA", "USA", 30.2266, -93.2174),
    ("LA_OUACHITA", "Monroe", "Ouachita Parish", "LA", "USA", 32.5093, -92.1193),
    ("LA_RAPIDES", "Alexandria", "Rapides Parish", "LA", "USA", 31.3113, -92.4451),
    ("LA_ST_TAMMANY", "Covington", "St. Tammany Parish", "LA", "USA", 30.4755, -90.1009),
    ("LA_TERREBONNE", "Houma", "Terrebonne Parish", "LA", "USA", 29.5958, -90.7195),
]

NEARBY_PLACES = [
    ("MS_HARRISON", "Gulfport", "Harrison County", "MS", "USA", 30.3674, -89.0928),
    ("MS_HINDS", "Jackson", "Hinds County", "MS", "USA", 32.2988, -90.1848),
    ("TX_HARRIS", "Houston", "Harris County", "TX", "USA", 29.7604, -95.3698),
    ("TX_JEFFERSON", "Beaumont", "Jefferson County", "TX", "USA", 30.0802, -94.1266),
    ("AR_PULASKI", "Little Rock", "Pulaski County", "AR", "USA", 34.7465, -92.2896),
]

PLACE_POOL = LA_PLACES + NEARBY_PLACES

LAST_NAMES = [
    "Landry", "Boudreaux", "Hebert", "Guidry", "Thibodeaux", "Fontenot",
    "Gautreaux", "Babin", "Broussard", "Doucet", "Comeaux", "Trahan",
    "Richard", "LeBlanc", "Bell", "Johnson", "Williams", "Brown", "Miller",
]
FIRST_NAMES_F = ["Marie","Ella","Rose","Clara","Louise","Josephine","Ruby","Pearl","Hazel","Evelyn"]
FIRST_NAMES_M = ["Joseph","Henry","Walter","James","John","Pierre","Louis","Arthur","George","Thomas"]

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def relationship_range_from_cm(cm: float):
    if cm >= 200: return (2, 3)
    if cm >= 100: return (3, 4)
    if cm >= 60:  return (3, 5)
    if cm >= 30:  return (4, 6)
    if cm >= 15:  return (5, 7)
    return (6, 8)

def sample_cm(cluster_strength: float) -> float:
    r = random.random()
    if r < 0.08: base = random.uniform(120, 260)
    elif r < 0.30: base = random.uniform(45, 120)
    else: base = random.uniform(8, 55)
    lift = 1.0 + (cluster_strength * 0.15)
    return round(base * lift, 1)

def sample_segments(cm: float) -> int:
    return int(clamp(round(cm / 12 + random.uniform(0, 4)), 1, 40))

def sample_longest(cm: float) -> float:
    frac = random.uniform(0.20, 0.55)
    return round(clamp(cm * frac, 5, 120), 1)

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def make_places():
    return pd.DataFrame(PLACE_POOL, columns=["place_id","place_name","parish_or_county","state","country","lat","lon"])

def generate_matches(n_matches=260, n_clusters=4):
    clusters = [{"cluster_id": f"C{i+1}", "cluster_strength": random.uniform(0.55, 0.95)} for i in range(n_clusters)]
    rows = []
    for i in range(n_matches):
        match_id = f"M{i+1:04d}"
        c = random.choices(clusters, weights=[1.0, 0.9, 0.8, 0.7][:n_clusters], k=1)[0]
        cm = sample_cm(c["cluster_strength"])
        lo, hi = relationship_range_from_cm(cm)
        tree_size = int(clamp(round(random.gauss(120, 90)), 0, 600))
        tree_conf = round(clamp(random.uniform(0.35, 0.95) * (0.7 + (tree_size / 1200)), 0.25, 0.98), 2)
        mph = random.choices(["maternal","paternal","unknown"], weights=[0.12,0.12,0.76], k=1)[0]
        rows.append({
            "match_id": match_id,
            "kit_id": KIT_ID,
            "cm_total": cm,
            "segments": sample_segments(cm),
            "longest_segment": sample_longest(cm),
            "predicted_range_low": lo,
            "predicted_range_high": hi,
            "maternal_paternal_hint": mph,
            "tree_size": tree_size,
            "tree_confidence": tree_conf,
            "notes": f"synthetic cluster={c['cluster_id']}"
        })
    df = pd.DataFrame(rows)
    df.loc[df["cm_total"].nlargest(3).index, "notes"] += " | anchor"
    return df

def generate_shared_matches(matches_df: pd.DataFrame):
    match_ids = matches_df["match_id"].tolist()
    cluster_map = {r["match_id"]: r["notes"].split("cluster=")[-1].split("|")[0].strip() for _, r in matches_df.iterrows()}

    edges = {}
    target_edges = int(len(match_ids) * 7.5)
    attempts = target_edges * 12

    for _ in range(attempts):
        a, b = random.sample(match_ids, 2)
        if a > b: a, b = b, a
        if (a, b) in edges: continue

        same = cluster_map[a] == cluster_map[b]
        p = 0.16 if same else 0.02

        cm_a = float(matches_df.loc[matches_df["match_id"] == a, "cm_total"].iloc[0])
        cm_b = float(matches_df.loc[matches_df["match_id"] == b, "cm_total"].iloc[0])
        boost = clamp((cm_a + cm_b) / 600.0, 0.0, 0.55)
        p = clamp(p + boost * (0.12 if same else 0.04), 0, 0.45)

        if random.random() <= p:
            base = random.uniform(0.35, 0.95) if same else random.uniform(0.20, 0.55)
            sim = 1.0 - (abs(cm_a - cm_b) / max(cm_a, cm_b, 1.0))
            strength = clamp(base * (0.75 + 0.25 * sim), 0, 1)

            edges[(a, b)] = {
                "match_id_a": a,
                "match_id_b": b,
                "shared_strength": round(strength, 3),
                "shared_cm_est": round(clamp(random.uniform(10, 80) * strength, 0, 120), 1),
                "shared_segments_est": int(clamp(round(random.uniform(1, 10) * strength), 0, 20)),
            }
        if len(edges) >= target_edges: break

    return pd.DataFrame(list(edges.values()))

def generate_persons_relationships_links(matches_df: pd.DataFrame):
    persons, rels, links = [], [], []
    person_counter = 1

    la_ids = [p[0] for p in LA_PLACES]
    near_ids = [p[0] for p in NEARBY_PLACES]

    cluster_surnames = {
        "C1": ["Landry","Hebert","Guidry","Thibodeaux","Boudreaux"],
        "C2": ["Fontenot","Broussard","Doucet","Trahan","Comeaux"],
        "C3": ["LeBlanc","Richard","Gautreaux","Babin","Broussard"],
        "C4": ["Bell","Johnson","Williams","Brown","Miller"],
    }

    for _, m in matches_df.iterrows():
        if random.random() < 0.12 or int(m["tree_size"]) == 0:
            continue

        match_id = m["match_id"]
        cluster = m["notes"].split("cluster=")[-1].split("|")[0].strip()
        surname_pool = cluster_surnames.get(cluster, LAST_NAMES)

        n_people = random.randint(2, 8)
        created = []

        for _i in range(n_people):
            pid = f"P{person_counter:06d}"
            person_counter += 1

            sex = random.choice(["F", "M"])
            fn = random.choice(FIRST_NAMES_F if sex == "F" else FIRST_NAMES_M)
            ln = random.choice(surname_pool if random.random() < 0.70 else LAST_NAMES)

            birth_year = int(clamp(round(random.gauss(1910, 25)), 1860, 1965))
            death_year = int(clamp(birth_year + random.randint(30, 90), birth_year + 1, 2025))

            place_birth = random.choices([random.choice(la_ids), random.choice(near_ids)], weights=[0.78, 0.22], k=1)[0]
            place_death = random.choices([place_birth, random.choice(la_ids), random.choice(near_ids)], weights=[0.55, 0.30, 0.15], k=1)[0]

            persons.append({
                "person_id": pid,
                "first_name": fn,
                "last_name": ln,
                "birth_year": birth_year,
                "death_year": death_year,
                "sex": sex,
                "birth_place": "",
                "death_place": "",
                "place_id_birth": place_birth,
                "place_id_death": place_death,
            })

            links.append({
                "match_id": match_id,
                "person_id": pid,
                "confidence_level": round(clamp(random.uniform(0.45, 0.95) * float(m["tree_confidence"]), 0.2, 0.98), 2)
            })

            created.append(pid)

        if len(created) >= 3:
            rels.append({"child_person_id": created[0], "parent_person_id": created[1], "relationship_type": "biological"})
            if len(created) >= 4 and random.random() < 0.65:
                rels.append({"child_person_id": created[2], "parent_person_id": created[3], "relationship_type": "biological"})

    return (
        pd.DataFrame(persons).drop_duplicates(subset=["person_id"]),
        pd.DataFrame(rels),
        pd.DataFrame(links),
    )

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(root, "data", "raw")
    ensure_dir(raw_dir)

    places_df = make_places()
    matches_df = generate_matches()
    shared_df = generate_shared_matches(matches_df)
    persons_df, rels_df, links_df = generate_persons_relationships_links(matches_df)

    places_df.to_csv(os.path.join(raw_dir, "places.csv"), index=False)
    matches_df.to_csv(os.path.join(raw_dir, "matches.csv"), index=False)
    shared_df.to_csv(os.path.join(raw_dir, "shared_matches.csv"), index=False)
    persons_df.to_csv(os.path.join(raw_dir, "persons.csv"), index=False)
    rels_df.to_csv(os.path.join(raw_dir, "relationships.csv"), index=False)
    links_df.to_csv(os.path.join(raw_dir, "match_tree_links.csv"), index=False)

    print("✅ Generated CSVs in forensic_genetic_genealogy/data/raw/")
    print("matches:", len(matches_df))
    print("shared edges:", len(shared_df))
    print("persons:", len(persons_df))
    print("relationships:", len(rels_df))
    print("match_tree_links:", len(links_df))

if __name__ == "__main__":
    main()
