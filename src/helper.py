import psycopg2
from datetime import datetime
from flask import jsonify
def get_connection():
    conn = psycopg2.connect(
        dbname="mgdb",
        user="postgres",
        password="1",
        host="localhost",
        port="5432"
    )
    return conn
def get_colnames():
    # conn = get_connection()
    # cursor = conn.cursor()
    # cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
    # columns = [row[0] for row in cursor.fetchall() if row[0] != 'vector']
    # cursor.close()
    # conn.close()
    columns =["acc", 
                "experiment", 
                "biosample", 
                "organism", 
                "bioproject",
                "sra_study", 
                "releasedate", 
                "collectiondate", 
                "center_name", 
                "country", 
                "latitude", 
                "longitude", 
                "attribute", 
                "instrument"]
    return columns

def construct_condition(condition, operator):
    if condition != "":
        condition += f" {operator} "
    return condition

def convert_date_to_timestamp(date_time_str):
    # Convert date to timestamp
    # 2025-02-28T16:00:00.000Z
    return datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()


def get_count(filters, params):
    conn = get_connection()
    cursor = conn.cursor()
    
    if filters.strip() == "1=1" or len(filters) <= 3:
        print("No filters applied")
        return 35200294 # Total number of rows in the metadata table

    sql_query = f"SELECT COUNT(*) FROM metadata WHERE {filters};"
    cursor.execute(sql_query, params)
    count = cursor.fetchall()[0][0]

    cursor.close()
    conn.close()

    return count

def advance_filter_where(filters):
    try:
        if not filters:
            return jsonify({"error": "No valid filters provided"}), 400
        
        accession_related = [
            "acc",
            "experiment",
            "biosample",
            "sra_study",
        ]

        # Build SQL query with dynamic filtering
        conditions = "1=1"
        total_filters = len(filters)
        params = []
        for idx, filter in enumerate(filters):
            field = filter.get('field')
            operator = filter.get('operator')
            value = filter.get('value')
            additional = filter.get('additional')
            
            if idx == 0:
                conditions += " AND "
                conditions += "(" * (total_filters - 1)
            else:
                conditions += f" {operator} "
            if field == 'acc':
                conditions_temp = ""
                # Split the value by comma
                values = value.split(",")
                # Iterate over the values and create conditions
                for val in values:
                    for col_name in accession_related:
                        conditions_temp = construct_condition(conditions_temp, "OR")
                        conditions_temp += f"{col_name} = %s"
                        params.append(val.strip()) # strip() to remove leading/trailing spaces
                conditions += f"({conditions_temp})"
            if field == 'organism':
                if additional:
                    print("Include all its children")
                    conditions += f"organism_id = %s or organism_id LIKE %s"
                    params.append(f"%.{value[0]}")
                    params.append(f"%.{value[0]}.%")
                else:
                    conditions += f"organism_id LIKE %s"
                    params.append(f"%.{value[0]}")
            if field == 'geo':
                conditions += f"country LIKE %s"
                params.append(f"%{value}%")
            if field == 'date':
                after_timestamp = convert_date_to_timestamp(value[0])
                before_timestamp = convert_date_to_timestamp(value[1])
                conditions += f"(releasedate >= %s AND releasedate <= %s)"
                # conditions += f"(collectiondate >= %s AND collectiondate <= %s OR releasedate >= %s AND releasedate <= %s)"
                params.append(after_timestamp)
                params.append(before_timestamp)
                # params.append(after_timestamp)
                # params.append(before_timestamp)
            if field == 'attribute':
                conditions += f"attribute LIKE %s"
                params.append(f"%{value}%")
            if idx != total_filters - 1:
                conditions += ")"
        
        print(conditions, params)
        
        return conditions, params

    except Exception as e:
        return jsonify({"error": str(e)}), 500