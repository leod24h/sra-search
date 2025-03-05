from flask import Flask, request, jsonify
from flask_cors import cross_origin
import psycopg2
from psycopg2 import Error
import time
import csv
import pandas as pd
from sentence_transformers import SentenceTransformer
from psycopg2.extras import DictCursor
from query import format_query, rerank, truncate_query, get_connection
from sentence_transformers import CrossEncoder
from datetime import datetime
 
embedding_model = SentenceTransformer("../all-MiniLM-L6-v2", device='cpu')
rerank_model = CrossEncoder("../jina-reranker-v1-turbo-en", trust_remote_code=True, device='cpu')

app = Flask(__name__)

# @app.route('/items/<int:item_id>', methods=['GET'])
# def get_item(item_id):
#     conn = get_connection()
#     cursor = conn.cursor()

#     sql_query = "SELECT * FROM metadata WHERE id = ANY(%s);"
#     cursor.execute(sql_query, ([item_id],))
#     results = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     if results is None:
#         return jsonify({"error": "Item not found"}), 404
#     return results


@app.route('/query/<string:text>', methods=['GET'])
@cross_origin()
def vector_query(text):

    import time
    t1 = time.time()
    text = format_query(text)
    t2 = time.time() 
    print("Time taken to format query:", t2 - t1)
    q_emb = embedding_model.encode([truncate_query(text)]).tolist()[0]

    t1 = time.time()
    print("Time taken to encode query:", t1 - t2)


    conn = get_connection()
    cursor_emb = conn.cursor(name='server_cursor', cursor_factory=DictCursor)
    cursor_get = conn.cursor(name='metadata_cursor', cursor_factory=DictCursor)

    # Query Vectors
    sql_query = "SELECT id FROM vectors ORDER BY vector <=> %s::vector LIMIT 500;"
    cursor_emb.execute(sql_query, (q_emb,))

    # Fetch ids
    out_id = cursor_emb.fetchall()
    id_list = [row[0] for row in out_id] 
    t2 = time.time()
    print("Time taken to process SQL queries (x2) ids:", t2 - t1)
    if id_list:

        # Get the corresponding ids from table
        sql_query = "SELECT * FROM metadata WHERE id = ANY(%s);"
        cursor_get.execute(sql_query, (id_list,))
        results = cursor_get.fetchall()
        
        # Rerank the first 100 to get ids
        reranked_ids = rerank(text, results, rerank_model, limit= 100)
        t1 = time.time()
        print("Time taken to rerank:", t1 - t2)

    
        output = [results[i] for i in reranked_ids] +results[100:]
        t2 = time.time()
        print("Time taken to concatenate reranked results:", t2 - t1)
        cursor_emb.close()
        cursor_get.close()
        conn.close()
        return pd.DataFrame(output).to_json(orient='records')
    else:
        cursor_emb.close()
        cursor_get.close()
        conn.close()
        return []
    

@app.route('/autocomplete_organism', methods=['GET'])
@cross_origin()
def autocomplete_organism():
    if request.method == 'GET':
        user_input = request.args.get('query', '')

    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Timing start
    start_time = time.time()

    # Connect to database
    conn = get_connection()
    cur = conn.cursor()

    # Autocomplete query
    query = """
        SELECT tax_id, scientific_name, common_name, synonym, genbank_common_name,
               LEAST(
                   levenshtein(COALESCE(scientific_name, ''), %s),
                   levenshtein(COALESCE(common_name, ''), %s),
                   levenshtein(COALESCE(genbank_common_name, ''), %s),
                   levenshtein(COALESCE(synonym, ''), %s)
               ) AS min_distance
        FROM taxonomy
        WHERE search_vector @@ plainto_tsquery(%s || ':*')
        ORDER BY min_distance
        LIMIT 10;
    """
    try:
        cur.execute(query, (user_input, user_input, user_input, user_input, user_input))
        results = cur.fetchall()
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Format results
        formatted_results = []
        for row in results:
            tax_id, sci_name, common_name, synonym, genbank_name, distance = row
            # Choose a general name: prefer common_name, then synonym, then genbank_common_name
            general_name = common_name or synonym or genbank_name or ""
            display_name = f"{sci_name} ({general_name})" if general_name else sci_name
            formatted_results.append({
                "tax_id": tax_id,
                # "scientific_name": sci_name,
                "value": display_name,
                # "distance": distance
            })

        print(f"Autocomplete query executed in {query_time:.2f} ms.")
        cur.close()
        conn.close()
        return jsonify(formatted_results)
    
    except psycopg2.Error as e:
        print(f"Query error: {e}")
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500
    
@app.route("/get_taxonomy_children_by_id", methods=["GET"])
@cross_origin()
def get_taxonomy_children_by_id():
    if request.method == 'GET':
        user_input = request.args.get('query', '')

    if not user_input:
        return jsonify({"error": "No query provided"}), 400
    
     # Timing start
    start_time = time.time()

    # Connect to database
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT children_ids
        FROM taxonomy
        WHERE tax_id = %s;
    """
    
    try:
        cur.execute(query, (user_input,))

        results = cur.fetchall()

        children_id_list = []

        for row in results:
            children_id_list = eval(row[0])
            # print(children_id_list)

        children_list = []

        if children_id_list != []:
            for i in children_id_list:
                children_list_template = {}
                cur.execute(
                    f"""
                    SELECT scientific_name, common_name, genbank_common_name, synonym
                    FROM taxonomy
                    WHERE tax_id = {i};
                    """
                )

                results = cur.fetchall()
                # print(i)
                for row in results:
                    # print(row)
                    children_list_template["organism_id"] = i
                    children_list_template["scientific_name"] = row[0]

                    if row[1] != "":
                        children_list_template["common_name"] = row[1]
                    elif row[2] != "":
                        children_list_template["common_name"] = row[2]
                    elif row[3] != "":
                        children_list_template["common_name"] = row[3]
                    else:
                        children_list_template["common_name"] = ""

                children_list.append(children_list_template)
                
        print(children_list)
        return jsonify(children_list)
    
    except psycopg2.Error as e:
        print(f"Query error: {e}")
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route("/get_world_popularity", methods=["GET"])
@cross_origin()
def get_world_popularity():
    csv_file = "./data/country_popularity.csv"

    data = []
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(
                {
                    "geo_loc_name_country_calc": row["geo_loc_name_country_calc"],
                    "count_entity": int(row["count_entity"]),
                }
            )

    return jsonify(data)

def construct_condition(condition, operator):
    if condition != "":
        condition += f" {operator} "
    return condition

def convert_date_to_timestamp(date_time_str):
    # Convert date to timestamp
    # 2025-02-28T16:00:00.000Z
    return datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()

@app.route('/query_simple_filter', methods=['GET'])
@cross_origin()
def query_simple_filter():
    """Retrieve metadata from PostgreSQL with complex filtering and pagination."""
    try:
        # Get filters from request body or query parameters (assuming JSON body for filters)
        filters = request.get_json().get('filters', []) if request.is_json else []
        
        # Remove empty filters (e.g., where value is empty or None)
        filters = [f for f in filters if f.get('value') and f['value']]
        print(filters)

        if not filters:
            return jsonify({"error": "No valid filters provided"}), 400
        
        accession_related = [
            "acc",
            "experiment",
            "biosample",
            "bioproject",
        ]

        # Build SQL query with dynamic filtering
        query = """
            SELECT 
                acc, 
                experiment, 
                biosample, 
                organism, 
                bioproject, 
                releasedate, 
                collectiondate, 
                center_name, 
                country, 
                latitude, 
                longitude, 
                attribute, 
                instrument
            FROM metadata
            WHERE 1=1"""
            
        conditions = ""
        total_filters = len(filters)
        for idx, filter in enumerate(filters):
            field = filter.get('field')
            operator = filter.get('operator')
            value = filter.get('value')
            addition = filter.get('addition')
            print(idx, field, operator, value)
            
            if idx == 0:
                conditions += " AND "
                conditions += "(" * (total_filters - 1)
            else:
                conditions += f" {operator} "
            if field == 'acc':
                conditions_temp = ""
                for col_name in accession_related:
                    conditions_temp = construct_condition(conditions_temp, "OR")
                    conditions_temp += f"{col_name} = '{value}'"
                conditions += f"({conditions_temp})"
            if field == 'organism':
                conditions += f"organism_id LIKE '%{value[0]}'"
            if field == 'geo':
                conditions += f"country LIKE '{value}'"
            if field == 'date':
                after_timestamp = convert_date_to_timestamp(value[0])
                before_timestamp = convert_date_to_timestamp(value[1])
                conditions += f"(collectiondate >= {after_timestamp} AND collectiondate <= {before_timestamp} OR releasedate >= {after_timestamp} AND releasedate <= {before_timestamp})"
            if field == 'attribute':
                conditions += f"attribute LIKE '{value}'"
            if idx != total_filters - 1:
                conditions += ")"
        
        print(conditions)
        conn = get_connection()
        cur = conn.cursor(name='metadata_cursor', cursor_factory=DictCursor)
        
        cur.execute(query + conditions + " LIMIT 500;")
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/geo_info_autocomplete', methods=['GET'])
@cross_origin()
def geo_info_autocomplete():
    if request.method == 'GET':
        user_input = request.args.get('query', '')

    if not user_input:
        return jsonify({"error": "No query provided"}), 400
    
    # Timing start
    start_time = time.time()

    # Connect to database
    conn = get_connection()
    cur = conn.cursor()

    # Autocomplete query
    query = f"""
        SELECT 
            location,
            levenshtein(COALESCE(location, ''), %s) AS distance,
            loc_lat, 
            loc_lng, 
            northeast_lat, 
            northeast_lng, 
            southwest_lat, 
            southwest_lng
        FROM geo_info
        WHERE LOWER(location) LIKE %s
        ORDER BY distance
        LIMIT 10;"""
        
    try:
        param = f"%{user_input.lower()}%"
        cur.execute(query, (user_input, param))
        results = cur.fetchall()
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Format results
        formatted_results = [row[0] for row in results]

        print(f"Autocomplete query executed in {query_time:.2f} ms.")
        cur.close()
        conn.close()
        return jsonify(formatted_results)
    
    except psycopg2.Error as e:
        print(f"Query error: {e}")
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5002, host="0.0.0.0")
            # ssl_context=("fullchain.pem", "privkey.pem"))
