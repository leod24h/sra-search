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
from helper import *
from sentence_transformers import CrossEncoder
from datetime import datetime
import json
from pgvector.psycopg2 import HalfVector, register_vector
import os


embedding_model = SentenceTransformer("../all-MiniLM-L6-v2", device='cuda')
rerank_model = CrossEncoder("../jina-reranker-v1-turbo-en", trust_remote_code=True, device='cuda')

app = Flask(__name__)


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
        t1 = time.time()
        text = format_query_gpt(text)
        t2 = time.time()
        print("Time taken to format query:", t2 - t1)

        # Encode Query
        q_emb = embedding_model.encode([truncate_query(text)]).tolist()[0]
        t3 = time.time()
        print("Time taken to encode query:", t3 - t2)
        print("Query:", text)
        conn = get_connection()
        cursor_emb = conn.cursor(name='server_cursor', cursor_factory=DictCursor)


        # Load pgvector
        register_vector(conn)

        if filters:
            where_clause, params = advance_filter_where(filters)
            params.append(HalfVector(q_emb))
        else:
            # Query Vectors
            filter_dict = create_filter_dict(text)
            params = []
            where_conditions = []
            for key, value in filter_dict.items():
                if key == "time": 
                    if len(value[0]) >3 and len(value[1]) > 3:
                        where_conditions.append(f"releasedate >= {value[0]} AND releasedate <= {value[1]}")
                    elif len(value[0]) > 3:
                        where_conditions.append(f"releasedate >= {value[0]}")
                    elif len(value[1]) > 3:
                        where_conditions.append(f"releasedate <= {value[1]}") 
                elif key == "country":
                    if len(value)>2:
                        where_conditions.append(f"LOWER(country) LIKE %s")
                        params.append(f"%{value}%")

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            params.append(HalfVector(q_emb))
        cols = ", ".join(get_colnames())


        ## SET NPROBES
        cursor_set = conn.cursor()
        cursor_set.execute("SET ivfflat.probes = 200;")
        cursor_set.close()


        # Count
        count = get_count(where_clause, params[:-1])
        print("Count:", count) 
        t35 = time.time()
        print("Time taken to count:", t35 - t3)
        
        if count > 10:
            sql_query =f"SELECT {cols} FROM metadata WHERE {where_clause} ORDER BY vec <=> %s::halfvec LIMIT 200;"
        else:
            sql_query =f"SELECT {cols} FROM metadata ORDER BY vec <=> %s::halfvec LIMIT 200;"
        print(sql_query)

        cursor_emb.execute(sql_query, params)
        results = cursor_emb.fetchall()
        t4 = time.time()
        print("Time taken to query:", t4 - t35)
        # Count number of matches

        # Fetch ids
        if len(results)>1:
            # Rerank the first 100 to get ids
            reranked_ids = rerank(text, results, rerank_model, limit= 200)

            output = [results[i] for i in reranked_ids][:100] #+results[100:]
            cursor_emb.close()
            conn.close()
            
            print("Time taken to rerank:", time.time() - t4)
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


@app.route('/fetch_study', methods=['GET'])
@cross_origin()
def fetch_study():
    try:
        study_acc = request.args.get('query', '').strip()
        
        # Connect to database
        conn = get_connection()
        cur = conn.cursor()
        
        query = """
            SELECT study_title, study_abstract
            FROM study
            WHERE sra_study = %s;
        """
        
        cur.execute(query, (study_acc,))
        
        results = cur.fetchall()
        cur.close()
        
        return jsonify(results)
        
    except:
        return jsonify({}), 200
    

@app.route('/query_abstract', methods=['GET'])
@cross_origin()
def query_abstract():
    
    text = request.args.get('query', '').strip()
    text = format_query_abstract(text)
    
    ft = request.args.get('ft', '').strip()
    print(ft)
    ft = True if ft == "true" else False
    
    print("Query:", text)
    print("FT:", ft)
    
    conn = get_connection()

    cursor = conn.cursor(name='server_cursor', cursor_factory=DictCursor)
    if ft:
        sql_query = """
            SELECT sra_study, study_title, study_abstract, center_project_name, study_type
            FROM study_abstract WHERE to_tsvector('english', study_title) @@ plainto_tsquery(%s) 
            LIMIT 100;
        """    

        cursor.execute(sql_query, (text,))
    else:
        query_vector = embedding_model.encode([text]).tolist()[0]
        sql_query = """
            SELECT sra_study, study_title, study_abstract, center_project_name, study_type
            FROM study_abstract
            ORDER BY vec <=> %s::halfvec
            LIMIT 100;
        """
        cursor.execute(sql_query, (query_vector,))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route('/fetch_sample', methods=['GET'])
@cross_origin()
def fetch_sample():
    sra_study_id = request.args.get('query', '').strip() # sra_study
    
    print("SRA Study ID:", sra_study_id)
    
    conn = get_connection()
    cursor = conn.cursor(name='server_cursor', cursor_factory=DictCursor)
    
    cols = ", ".join(get_colnames())
    
    sql_query = f"SELECT {cols} FROM metadata WHERE sra_study = %s LIMIT 10;"
    cursor.execute(sql_query, (sra_study_id,))
    
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

@app.route('/fetch_sample_from_multiple_study', methods=['GET'])
@cross_origin()
def fetch_sample_from_multiple_study():
    # Retrieve and clean the query parameter
    sra_study_id = request.args.get('query', '').strip()
    sra_study_ids = sra_study_id.split(",")
    sra_study_ids = [s.strip() for s in sra_study_ids]

    print("SRA Study ID:", sra_study_ids)

    # Database connection
    conn = get_connection()
    cursor = conn.cursor(name='server_cursor', cursor_factory=DictCursor)

    # Columns to fetch
    cols = ", ".join(get_colnames())

    # Create a formatted list of sra_study_ids for use in the query
    placeholders = ', '.join(['%s'] * len(sra_study_ids))

    # SQL query with Common Table Expression (CTE) to limit results per group
    sql_query = f"""
        WITH ranked_metadata AS (
            SELECT 
                {cols}, 
                sra_study,
                ROW_NUMBER() OVER (PARTITION BY sra_study ORDER BY id) AS row_num
            FROM 
                metadata
            WHERE 
                sra_study IN ({placeholders})
        )
        SELECT * FROM ranked_metadata WHERE row_num <= 10;
    """
    
    # Execute the query
    cursor.execute(sql_query, tuple(sra_study_ids))
    results = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    # Return the results as JSON
    return jsonify(results)
    
if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
            # ssl_context=("fullchain.pem", "privkey.pem"))
