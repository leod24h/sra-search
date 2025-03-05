from flask import Flask, request, jsonify
from flask_cors import cross_origin
import psycopg2
from psycopg2 import Error
import time
import csv
import pandas as pd
from sentence_transformers import SentenceTransformer
from psycopg2.extras import DictCursor
from query import *
from sentence_transformers import CrossEncoder
from datetime import datetime
import json
 
embedding_model = SentenceTransformer("../all-MiniLM-L6-v2", device='cuda')
rerank_model = CrossEncoder("../jina-reranker-v1-turbo-en", trust_remote_code=True, device='cuda')

app = Flask(__name__)



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

    # Query Vectors
    sql_query = create_SQL_query(text)
    # sql_query = "SELECT id FROM metadata_all ORDER BY vector <=> %s::vector LIMIT 500;"
    cursor_emb.execute(sql_query, (q_emb,))

    # Fetch ids
    results = cursor_emb.fetchall()
    t2 = time.time()
    print("Time taken to process SQL queries (x2) ids:", t2 - t1)    
    # Rerank the first 100 to get ids
    reranked_ids = rerank(text, results, rerank_model, limit= 100)
    t1 = time.time()
    print("Time taken to rerank:", t1 - t2)


    output = [results[i] for i in reranked_ids] +results[100:]
    t2 = time.time()
    print("Time taken to concatenate reranked results:", t2 - t1)
    cursor_emb.close()
    conn.close()
    return jsonify(output)

    

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

@app.route('/query_with_filter', methods=['GET'])
@cross_origin()
def query_filter():
    try:
        text = request.args.get('query', '').strip()
        filters = request.args.get('filters', None)
        if filters:
            filters = json.loads(filters)  # Parse the filters as JSON
        else:
            filters = []
        if not text:
            text = ""
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    if len(text) > 1:
        # Format Query
        text = format_query(text)
        q_emb = embedding_model.encode([truncate_query(text)]).tolist()[0]
        conn = get_connection()
        cursor_emb = conn.cursor(name='server_cursor', cursor_factory=DictCursor)
        if filters:
            where_clause, params = advance_filter_where(filters)
            params.append(q_emb)
        else:
            # Query Vectors
            filter_dict = create_filter_dict(text)
            # sql_query = "SELECT id FROM metadata_all ORDER BY vector <=> %s::vector LIMIT 50;"

            where_conditions = []
            for key, value in filter_dict.items():
                if key == "time": 
                    if len(value[0]) >3 and len(value[1]) > 3:
                        where_conditions.append(f"releasedate >= {value[0]} AND releasedate <= {value[1]}")
                    elif len(value[0]) > 3:
                        where_conditions.append(f"releasedate >= {value[0]}")
                    elif len(value[1]) > 3:
                        where_conditions.append(f"releasedate <= {value[1]}") 
                # elif key == "location":
                #     where_conditions.append(f"latitude >= {value[0]} AND latitude <= {value[1]}")
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            where_clause = "1=1"
            params = (q_emb,)
        where_clause = "1=1"
        cols = ", ".join(get_colnames())

        # Output SQL query
        sql_query =f"SELECT {cols} FROM metadata WHERE {where_clause} ORDER BY vec <=> %s::vector LIMIT 500;"
        print(sql_query)

        cursor_emb.execute(sql_query, params)
        results = cursor_emb.fetchall()

        # Count number of matches
        count = get_count(where_clause, params)
        print("Count:", count)
        # Fetch ids
        if len(results)>1:
            # Rerank the first 100 to get ids
            reranked_ids = rerank(text, results, rerank_model, limit= 100)

            output = [results[i] for i in reranked_ids] #+results[100:]
            cursor_emb.close()
            conn.close()
            
            output.append(count)
            
            return jsonify(output)
        else:
            print("No results found")
            return jsonify({}),200
    elif filters:
        where_clause, params = advance_filter_where(filters)

        cols = ", ".join(get_colnames())
        sql_query = f"SELECT {cols} FROM metadata WHERE {where_clause} LIMIT 100;"
        conn = get_connection()
        cursor_emb = conn.cursor(name='server_cursor', cursor_factory=DictCursor)

        cursor_emb.execute(sql_query, params)
        results = cursor_emb.fetchall()
        
        count = get_count(where_clause, params)
        print("Count:", count)
        
        cursor_emb.close()
        conn.close()
        
        results.append(count)
        
        return jsonify(results)
    else:
        return jsonify({}), 200

def advance_filter_where(filters):
    try:
        if not filters:
            return jsonify({"error": "No valid filters provided"}), 400
        
        accession_related = [
            "acc",
            "experiment",
            "biosample",
            "bioproject",
        ]

        # Build SQL query with dynamic filtering
        conditions = "1=1"
        total_filters = len(filters)
        params = []
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
                    conditions_temp += f"{col_name} = %s"
                    params.append(value)
                conditions += f"({conditions_temp})"
            if field == 'organism':
                if addition:
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
                conditions += f"(collectiondate >= %s AND collectiondate <= %s OR releasedate >= %s AND releasedate <= %s)"
                params.append(after_timestamp)
                params.append(before_timestamp)
                params.append(after_timestamp)
                params.append(before_timestamp)
            if field == 'attribute':
                conditions += f"attribute LIKE %s"
                params.append(f"%{value}%")
            if idx != total_filters - 1:
                conditions += ")"
        
        print(conditions)
        
        return conditions, params

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
            # ssl_context=("fullchain.pem", "privkey.pem"))
