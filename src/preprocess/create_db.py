import pandas as pd
import psycopg2

def map_dtype(pd_dtype):
    if pd_dtype == 'int64':
        return 'INTEGER'
    elif pd_dtype == 'float64':
        return 'DOUBLE PRECISION'
    elif 'datetime' in pd_dtype:
        return 'TIMESTAMP'
    else:
        # Default to TEXT for object types and others.
        return 'TEXT'

def create_table_from_csv(sample_csv_path, table_name, conn):
    # Read a sample of the CSV file (e.g. first 100 rows) to infer the schema.
    df = pd.read_csv(sample_csv_path, nrows=100, parse_dates=True)

    # Build the column definitions based on the CSV header and inferred dtypes.
    columns = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        sql_type = map_dtype(dtype)
        if str(col) == 'releasedate':
            sql_type = 'BIGINT'
        if str(col) == 'mbytes':
            sql_type = 'DOUBLE PRECISION'
        if str(col) == 'mbases':
            sql_type = 'DOUBLE PRECISION'
        if str(col) == 'avgspotlen':
            sql_type = 'DOUBLE PRECISION'
        # Quoting the column names in case they contain special characters.
        columns.append(f'"{col}" {sql_type}')
    columns.append(F'"id" SERIAL PRIMARY KEY')
    columns.append(F'"vec" halfvec(384)')
    # Join the column definitions into the CREATE TABLE statement.
    columns_str = ",\n    ".join(columns)
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns_str}
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    print(f"Table '{table_name}' created with the inferred schema.")


    # Define your database connection parameters.
DB_NAME = 'mgdb'
DB_USER = 'postgres'
DB_PASS = '1'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Specify the path to your sample CSV file and the desired table name.
SAMPLE_CSV = '/media/data/tracy/SRA-Search/SRA-Curated/SRA-curated-metadata-000000000000.csv'
TABLE_NAME = 'metadata'

try:
    # Connect to the PostgreSQL database.
    conn = psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST, 
        port=DB_PORT
    )
    create_table_from_csv(SAMPLE_CSV, TABLE_NAME, conn)
except Exception as e:
    print("An error occurred:", e)
finally:
    if conn:
        conn.close()