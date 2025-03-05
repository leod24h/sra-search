import os
import json
import psycopg2
import pandas as pd
import io

# Database connection parameters
DB_NAME = 'mgdb'
DB_USER = 'postgres'
DB_PASS = '1'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Directory containing the CSV files
CSV_FOLDER = '/media/data/tracy/SRA-Search/embeddings'
PROCESSED_FILES_PATH = "processed_files.json"  # File to store processed filenames

# Load processed files list
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
    df['id'] = df.index.map(lambda i: f"{file_id}{i:05d}")
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

            file_path = os.path.join(CSV_FOLDER, filename)

            # Read CSV with pandas to get embeddings and IDs
            df = pd.read_csv(file_path)
            df = generate_unique_id(filename, df)
            # Extract relevant columns (assumed 'id' and 'embedding')
            df = df[['id', 'embedding']]
            df['embedding'] = df['embedding'].apply(lambda x: f"[{x}]")

            # Prepare data for COPY
            # Use StringIO to write to a pseudo-file object
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, sep = '\t',header=False, index=False)
            csv_buffer.seek(0)

            # Perform the COPY operation
            cursor.copy_from(csv_buffer, 'vectors', columns=['id', 'vector'], sep='\t')

            # Commit transaction
            conn.commit()

            # Save this file as processed
            save_processed_file(filename)
            print(f"File {filename} processed successfully.")

except Exception as e:
    print("An error occurred:", e)
    conn.rollback()

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
