import os
import time
import psycopg2
import pandas as pd
import numpy as np
from psycopg2.extras import execute_values
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Database connection parameters
DB_NAME = 'mgdb'
DB_USER = 'postgres'
DB_PASS = '1'
DB_HOST = 'localhost'
DB_PORT = '5432'
BATCH_SIZE = 4096  # Tune batch size if needed
NUM_WORKERS = min(cpu_count(), 4)  # Use up to 4 parallel processes

def process_batch(batch_data):
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

        # Create a temporary table
        cursor.execute("""
        CREATE TEMP TABLE temp_update AS
        TABLE metadata WITH NO DATA;
        """)

        # Insert batch into the temp table
        execute_values(cursor, """
        INSERT INTO temp_update (acc, sra_study)
        VALUES %s
        """, batch_data, template="(%s, %s)")

        # Efficient update using JOIN
        cursor.execute("""
        UPDATE metadata
        SET sra_study = temp_update.sra_study
        FROM temp_update
        WHERE metadata.acc = temp_update.acc;
        """)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Batch update error: {e}")

def update_db():
    """Loads data and processes updates in parallel."""
    csv_path = "/media/data/tracy/SRA-Search/acc2sra_study.csv"
    df = pd.read_csv(csv_path)

    num_batches = (df.shape[0] + BATCH_SIZE - 1) // BATCH_SIZE

    for i in tqdm(range(0, df.shape[0], BATCH_SIZE), total=num_batches, desc="Processing batches"):
        batch = df.iloc[i:i+BATCH_SIZE][['acc', 'sra_study']].values.tolist()
        process_batch(batch)

if __name__ == "__main__":
    start_time = time.time()
    update_db()
    print(f"Processing completed in {time.time() - start_time:.2f} seconds.")
