import os
import json
import psycopg2
import pandas as pd
import numpy as np
from psycopg2.extras import execute_values

# Database connection parameters
DB_NAME = 'mgdb'
DB_USER = 'postgres'
DB_PASS = '1'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Directory containing the CSV files
CSV_FOLDER = '/media/data/tracy/SRA-Search/SRA-Curated'
PROCESSED_FILES_PATH = "processed_files.json"  # File to store processed filenames
counter = 0

def load_processed_files():
    """Load processed files list from JSON."""
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, "r") as f:
            return set(json.load(f))  # Load as a set for fast lookup
    return set()

def save_processed_file(filename):
    """Save processed file to JSON."""
    processed_files.add(filename)  # Add to the set
    with open(PROCESSED_FILES_PATH, "w") as f:
        json.dump(list(processed_files), f)  # Save as a list

def generate_unique_id(filename, df):
    """Generates a unique ID by combining the numeric part of filename with row index"""
    file_id = filename.split('-')[-1].split('.')[0][5:]  # Extract numeric ID from filename
    df['unique_id'] = df.index.map(lambda i: f"{file_id}{i:05d}")
    return df

# Load processed files at the start
processed_files = load_processed_files()

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST, 
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Iterate over each CSV file in the folder
    for filename in sorted(os.listdir(CSV_FOLDER), reverse=True):
        if filename.endswith('.csv'):
            if filename in processed_files:
                print(f"Skipping {filename}, already processed.")
                continue  # Skip already processed files

            counter += 1
            file_path = os.path.join(CSV_FOLDER, filename)

            # Read CSV with pandas to infer column names
            df = pd.read_csv(file_path)
            df = generate_unique_id(filename, df)

            # Ensure all column names are lowercase for PostgreSQL compatibility
            df.columns = [col.lower() for col in df.columns]
            df['releasedate'] = df['releasedate'].astype('Int64')
            df['mbytes'] = df['mbytes'].astype('Float64')

            # Replace empty strings and NaNs with None (for PostgreSQL NULL compatibility)
            df = df.replace({np.nan: None, '': None})

            # Define final column names including unique_id
            columns = df.columns.tolist()[:-1] + ['id']  # Ensure matches DB table

            # Convert DataFrame to list of tuples for `execute_values`
            values = df.to_records(index=False).tolist()

            if values:
                # Generate INSERT SQL
                insert_sql = f"""
                INSERT INTO metadata ({', '.join(columns)})
                VALUES %s
                ON CONFLICT DO NOTHING;
                """

                # Execute batch insert
                execute_values(cursor, insert_sql, values)
                conn.commit()

                # Save this file as processed
                save_processed_file(filename)

                # Print progress every 5 files
                if counter % 5 == 0:
                    print(f"File {filename} loaded successfully.")
            else:
                print(f"Skipping {filename}, as it contains no valid data.")

except Exception as e:
    print("An error occurred:", e)
    conn.rollback()

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
