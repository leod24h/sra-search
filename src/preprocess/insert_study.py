import os
import time
import psycopg2
import pandas as pd
import numpy as np
from psycopg2.extras import execute_values
from tqdm import tqdm
from sentence_transformers import SentenceTransformer 

# Database connection parameters
DB_NAME = 'mgdb'
DB_USER = 'postgres'
DB_PASS = '1'
DB_HOST = 'localhost'
DB_PORT = '5432'
BATCH_SIZE = 4096  # Tune batch size if needed

model = SentenceTransformer('/media/data/tracy/SRA-Search/all-MiniLM-L6-v2', device='cuda')

def ensure_table_exists():
    """Ensures that the study_abstract table exists in PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST, 
            port=DB_PORT
        )
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS study_abstract (
            sra_study TEXT PRIMARY KEY,
            study_title TEXT,
            study_abstract TEXT,
            center_project_name TEXT,
            study_type TEXT,
            
            text TEXT,
            vec halfvec(384)
        );
        """

        cursor.execute(create_table_sql)
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error ensuring table exists: {e}")
def process_batch(values,columns):
    """Processes a batch of updates efficiently using a temporary table."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST, 
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Set maintenance parameters
        cursor.execute("SET maintenance_work_mem = '100GB';")
        cursor.execute("SET max_parallel_maintenance_workers = 100;")
        cursor.execute("SET max_parallel_workers_per_gather = 100;")
        # Generate INSERT SQL
        insert_sql = f"""
        INSERT INTO study_abstract ({', '.join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING;
        """

        execute_values(cursor, insert_sql, values)
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Batch update error: {e}")

def update_db():
    """Loads data and processes updates in parallel."""
    csv_path = "../../study.csv"
    df = pd.read_csv(csv_path)

    ensure_table_exists()

    num_batches = (df.shape[0] + BATCH_SIZE - 1) // BATCH_SIZE
    df['study_abstract'].fillna('')
    df['study_title'].fillna('')
    for i in tqdm(range(0, df.shape[0], BATCH_SIZE), total=num_batches, desc="Processing batches"):


        batch = df.iloc[i:i+BATCH_SIZE][["sra_study","study_title","study_abstract", "center_project_name","study_type"]]
        batch_str  = "Title: " + batch['study_title'] + '.   Abstract: ' + batch['study_abstract'].str.slice(0, 1000)
        embeddings = model.encode(batch_str.tolist(), batch_size=BATCH_SIZE)
        embeddings_str = [f"[{', '.join(map(str, emb))}]" for emb in embeddings]

        batch['vec'] = embeddings_str
        values = batch.to_records(index=False).tolist()
        columns = batch.columns.tolist() # Ensure matches DB table
        process_batch(values,columns)
        print(f"Processed batch {(i+1)//BATCH_SIZE}/{num_batches}")

if __name__ == "__main__":
    start_time = time.time()
    update_db()
    print(f"Processing completed in {time.time() - start_time:.2f} seconds.")
