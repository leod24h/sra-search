import psycopg2
import numpy as np

# Generate a random 384-dimensional query vector
def generate_vector(dim=384):
    vec = np.random.rand(dim).round(6)
    return "[" + ",".join(map(str, vec)) + "]"

# --- Database connection settings ---


# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="mgdb",
    user="xuebing",
    password="1",
    host="localhost",
    port="5432"
)
conn.autocommit = True
cursor = conn.cursor()

# Set number of IVF lists to probe
cursor.execute("SET ivfflat.probes = %s;", (40,))
cursor.execute("SET track_io_timing = on;")
# cursor.execute("SELECT pg_prewarm('metadata_vec_idx',  mode := 'prefetch');")
# Prepare query
query_vector = generate_vector()
limit = 10
sql_explain = """
EXPLAIN (ANALYSE, VERBOSE, BUFFERS)
    SELECT * FROM metadata
    WHERE 1=1
    ORDER BY vec <=> %s::halfvec
    LIMIT %s;
"""

# Run EXPLAIN ANALYZE
cursor.execute(sql_explain, (query_vector, limit))
plan_rows = cursor.fetchall()

print("🔍 Query Plan (EXPLAIN ANALYZE):")
for row in plan_rows:
    print(row[0])

# # --- Actual execution (optional, after checking plan) ---
# sql_actual = """
#     SELECT * FROM metadata
#     WHERE 1=1
#     ORDER BY vec <=> %s::halfvec
#     LIMIT %s;
# """

# cursor.execute(sql_actual, (query_vector, limit))
# rows = cursor.fetchall()

# print(f"\nTop {limit} similar vectors:")
# for row in rows:
#     print(f"ID: {row[0]}")

# Clean up
cursor.close()
conn.close()