import sqlite3
import pandas as pd
import networkx as nx
from community import community_louvain

print("Connecting to database...")
conn = sqlite3.connect("bayou_doe.db")

# Load shared match edges
print("Loading shared match network...")
edges = pd.read_sql_query("""
SELECT match_id_a, match_id_b, shared_strength
FROM shared_matches
""", conn)

print(f"Edges loaded: {len(edges)}")

# Build graph
print("Building graph...")
G = nx.Graph()

for _, row in edges.iterrows():
    weight = float(row["shared_strength"])
    G.add_edge(row["match_id_a"], row["match_id_b"], weight=weight)


print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# Run Louvain clustering
print("Running Louvain community detection...")
partition = community_louvain.best_partition(G, weight='weight')

cluster_df = pd.DataFrame(list(partition.items()), columns=["match_id", "cluster_id"])

# Calculate cluster sizes
sizes = cluster_df.groupby("cluster_id").size().reset_index(name="cluster_size")
cluster_df = cluster_df.merge(sizes, on="cluster_id")

print("\nCluster summary:")
print(cluster_df["cluster_id"].value_counts().head())

# Save back to SQLite
print("\nWriting clusters to database...")
cluster_df.to_sql("match_clusters", conn, if_exists="replace", index=False)

conn.close()
print("\nDONE. Clusters saved to SQLite as: match_clusters")
