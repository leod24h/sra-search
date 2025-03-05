import os
import json
import psycopg2
import pandas as pd
import numpy as np
import time
from psycopg2.extras import execute_values
from multiprocessing import Pool, cpu_count

# Database connection parameters
DB_NAME = 'mgdb'
DB_USER = 'postgres'
DB_PASS = '1'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Directory containing the CSV files
DATA_FOLDER = '/media/data/tracy/SRA-Search/SRA-Curated'
EMBEDDING_FOLDER = '/media/data/tracy/SRA-Search/embeddings'
PROCESSED_FILES_PATH = "processed_files.json"  # File to store processed filenames

def load_processed_files():
    """Load processed files list from JSON."""
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, "r") as f:
            return set(json.load(f))  # Load as a set for fast lookup
    return set()

def save_processed_file(filename, processed_files):
    """Save processed file to JSON."""
    processed_files.add(filename)
    with open(PROCESSED_FILES_PATH, "w") as f:
        json.dump(list(processed_files), f)  # Save as a list

def generate_unique_id(filename, df):
    """Generates a unique ID by combining the numeric part of filename with row index"""
    file_id = filename.split('-')[-1].split('.')[0][5:]  # Extract numeric ID from filename
    df['unique_id'] = df.index.map(lambda i: f"{file_id}{i:05d}")
    return df

def process_and_insert(args):
    """Process a single file and insert into PostgreSQL in parallel"""
    embedding_filename, data_filename, processed_files = args

    if data_filename in processed_files:
        print(f"Skipping {data_filename}, already processed.")
        return None

    embedding_path = os.path.join(EMBEDDING_FOLDER, embedding_filename)
    data_path = os.path.join(DATA_FOLDER, data_filename)

    try:
        # Read CSV
        df = pd.read_csv(data_path)
        df_emb = pd.read_csv(embedding_path)

        # Merge embeddings
        df['vec'] = df_emb['embedding'].apply(lambda x: f"[{x}]")
        df = generate_unique_id(data_filename, df)

        # Ensure column names are lowercase
        df.columns = [col.lower() for col in df.columns]
        df['releasedate'] = df['releasedate'].astype('Int64')
        df['mbytes'] = df['mbytes'].astype('Float64')

        # Replace NaNs with None
        df = df.replace({np.nan: None, '': None})

        # Convert DataFrame to list of tuples
        values = df.to_records(index=False).tolist()
        columns = df.columns.tolist()[:-1] + ['id']  # Ensure matches DB table

        if not values:
            print(f"Skipping {data_filename}, as it contains no valid data.")
            return None

        # Insert into PostgreSQL
        insert_to_db(data_filename, columns, values)

        return data_filename  # Return processed filename if successful

    except Exception as e:
        print(f"Error processing {data_filename}: {e}")
        return None

def insert_to_db(data_filename, columns, values):
    """Insert data into PostgreSQL using batch inserts."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST, 
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Generate INSERT SQL
        insert_sql = f"""
        INSERT INTO metadata ({', '.join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING;
        """

        execute_values(cursor, insert_sql, values)
        conn.commit()
        print(f"{data_filename} inserted successfully.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database insertion error: {e}")

if __name__ == "__main__":
    start_time = time.time()

    # Load processed files
    processed_files = load_processed_files()

    # Get file lists
    embedding_list = sorted(os.listdir(EMBEDDING_FOLDER), reverse=True)
    data_list = sorted(os.listdir(DATA_FOLDER), reverse=True)

    # Prepare file pairs
    file_pairs = [(embedding_list[i], data_list[i], processed_files) for i in range(len(embedding_list))]

    # Use multiprocessing to process files in parallel
    num_workers = max(cpu_count() // 2, 4)  # Use half the cores, at least 4 workers
    with Pool(processes=num_workers) as pool:
        results = pool.map(process_and_insert, file_pairs)

    # Filter out None results
    processed_files = {res for res in results if res is not None}

    # Save processed files
    for filename in processed_files:
        save_processed_file(filename, processed_files)

    print(f"Processing completed in {time.time() - start_time:.2f} seconds.")
