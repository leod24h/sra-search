import requests
import pandas as pd
import psycopg2
from datetime import datetime

def get_connection():
    conn = psycopg2.connect(
        dbname="mgdb",
        user="postgres",
        password="1",
        host="localhost",
        port="5432"
    )
    return conn


def format_query(query):
    url = "https://openrouter.ai/api/v1/chat/completions"
    with open("../api_key.txt", "r") as file:
        api_key = file.read().strip()  # Remove any whitespace or newline

    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your real API key
        "Content-Type": "application/json"
    }

    prompt = f"""
    System:

    You are a **Text Processing Assistant** specializing in **structured data extraction** from natural language queries. Your goal is to transform user queries into a predefined structured format.

    **Objective:** Analyze natural language queries and extract key information to create a structured output according to the specifications below. You will identify organisms, associated genus names, countries, time ranges, and negative constraints.

    **Output Format:**

    Your output *must* adhere to this precise format:

    `Organism: <organism_name> | Genus: <genus_names> | Country: <country_name> | Time: <unix_timestamp_range> | Exclude: <negative_constraint>`

    **Details for each field:**

    *   **Organism:** Extract the primary organism described in the query.
    *   **Genus:**
        *   **Specific Organisms:** If the query specifies a particular organism (e.g., "frogs"), provide *at least three* relevant genus names.
        *   **Generic Organisms:** If the query uses a generic term (e.g., "animals", "birds"), provide *at least five* relevant genus names.
    *   **Country:** Extract the country mentioned in the query. Leave this field empty if no country mentioned.
    *   **Time:** Represent the time range (if any) using two Unix timestamps formatted as `start_timestamp, end_timestamp`.  Leave this field empty if no time is specified (Example Time Stamps - `1678886400, 1679059200`)
    *   **Location:** Transform the country into longitude and latitude. Separate the two values with a comma. Leave this field empty if no country mentioned.
    *   **Exclude:** Identify and extract negative statements. Words like "not", "but not", "without", and "except" indicate exclusions. Extract the subject of the negative constraint. Leave this field empty if no negative constraint exists.

    **Rules to Follow:**
    1. Always use `|` and `:` as delimiters.
    2. No extra text, explanations, or formatting variations. 
    3. If the input is Chinese, first translate it to English, and then process the query. The output has to be in **English**.

    **Examples:**

    *   Query: "frogs not from france"
        Output: "Organism: frogs | Genus: Lithobates, Phyllobates | Country: | Time: | Location: 46.2276, 2.2137 | Exclude: France "

    *   Query: "australian sea animals"
        Output: "Organism: animals | Genus: Carcharodon, Balaenopteridae, pinnipeds, Dugong, Galeocerdo, Megaptera | Country: Australia | Time: | Location: 25.2744, 133.7751 | Exclude: "

    *   Query: "American birds"
        Output: "Organism: birds | Genus: Corvus, Passer, Parus, Turdus, Accipiter | Country: United States | Time: 1456358935, 1551053335 | Location: 38.7946, 106.5348 | Exclude: "

    **Now Process This Query**:
    Query: '{query}'
    """

    payload = {
        "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
        "messages": [
            {
                "role": "user",
                "content": prompt.strip()
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)

        result = response.json()
        output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "No response found")

        print("Response:", output_text)
        return output_text

    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return None
    
def truncate_query(query):
    return ''.join(query.split('|')[:3])

def rerank(query, results, rerank_model, limit=100):
    # returns the reranked ids (id of the output, not database)
    try:
        df = pd.DataFrame(results[:limit])
        temp = "Organism: " + df[3].astype(str) +', Country: ' + df[8].astype(str) + ', Attributes: ' +df[11].astype(str)[:300]
    except (KeyError, IndexError):
        return []
    response = rerank_model.rank(query, temp.tolist(), return_documents=True, top_k= df.shape[0])#df.shape[0])
    reranked_id = [entry['corpus_id'] for entry in response]
    
    return reranked_id
from collections import defaultdict

def create_filter_dict(text):
    text = text.split("|")

    def safe_split(index):
        try:
            t1, t2 = text[index].split(":")[1].split(",")
            return t1,t2
        except (IndexError, ValueError):
            return "", ""

    t1, t2 = safe_split(3)
    l1, l2 = safe_split(4)
    try:
        country_str = text[2].split(":")[1].strip()
    except (IndexError, ValueError):
        country_str = ""
    output_dict = {
        "country": country_str.lower(),
        "time": [t1.strip(), t2.strip()],
        "location": [l1.strip(), l2.strip()]
    }
    return output_dict

def create_SQL_query(text):
    filter_dict = create_filter_dict(text)
    where_conditions = []
    for key, value in filter_dict.items():
        # if key == "country":
        #     if len(value) > 2:
        #         where_conditions.append(f"country = '{value}'")
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
    cols = ", ".join(get_colnames())
    # Output SQL query
    output_str =f"SELECT {cols} FROM metadata WHERE {where_clause} ORDER BY vec <=> %s::vector LIMIT 500;"
    return output_str

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
