import requests
import pandas as pd
import psycopg2
from datetime import datetime
from helper import *
import os
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from abstract import *

with open("../api_key.txt", "r") as f:
    for line in f:
        if "="  in line: 
            key, value = line.strip().split("=",1)  
            key = value  


deployment = 'gpt-4.1-nano'
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://new-mgdb-resource.cognitiveservices.azure.com/",
    api_key=key,
)

def get_prompt(query):
    prompt = f"""
    System:

    You are a **Text Processing Assistant** specializing in **structured data extraction** from natural language queries. Your goal is to transform user queries into a predefined structured format.

    **Objective:** Analyze natural language queries and extract key information to create a structured output according to the specifications below. You will identify organisms, associated genus names, countries, time ranges, and negative constraints.

    **Output Format:**

    Your output *must* adhere to this precise format:

    `Organism: <organism_name> | Genus: <genus_names> | Attributes: <attribute> | Country: <country_name>  | Time: <unix_timestamp_range> | Location: <longitude, latitude> | Exclude: <negative_constraint>`

    **Details for each field:**
    * **Organism:** Extract the primary organism described in the query.
    * **Genus:**
        * **Specific Organisms:** If the query specifies a particular organism (e.g., "frogs"), provide *at least three* relevant genus names. 
        * **Generic Organisms:** If the query uses a generic term (e.g., "animals", "tree animals"), provide *at least five* relevant genus names given the *context* (e.g. Forest, tree, ocean).
    * **Country:** Extract the country mentioned in the query. Leave this field empty if no country mentioned.
    * **Attributes:** Other relevant information that does not fit in the categories, such as color, size, blood, or any other. Also repeat the organism name here.
    * **Time:** Represent the time range (if any) using two Unix timestamps formatted as `start_timestamp, end_timestamp`. Leave this field empty if no time is specified (Example Time Stamps - `1678886400, 1679059200`).
    * **Location:** Transform the country into longitude and latitude. Separate the two values with a comma. Leave this field empty if no country mentioned.
    * **Exclude:** Identify and extract negative statements. Words like "not", "but not", "without", and "except" indicate exclusions. Extract the subject of the negative constraint. Leave this field empty if no negative constraint exists.

    **Rules to Follow:**
    1. Always use `|` and `:` as delimiters.
    2. No extra text, explanations, or formatting variations.
    3. If the input is Chinese, first translate it to English, and then process the query. The output has to be in **English**.

    
    **Examples:**
    * Query: "frogs not from France"
      Output: "Organism: frogs | Genus: Lithobates, Phyllobates | Attributes: frog | Country: | Time: | Location: 46.2276, 2.2137 |  Exclude: France"
    * Query: "australian sea animals"
      Output: "Organism: animals | Genus: Carcharodon, Balaenopteridae, pinnipeds, Dugong, Megaptera | Attributes: | Country: Australia | Time: | Location: 25.2744, 133.7751 | Exclude: "
    * Query: "Please find me American tree birds after 2017"
      Output: "Organism: birds | Genus: Corvus, Passer, Parus, Turdus, Accipiter | Attributes: tree birds | Country: United States  | Time: 1456358935, 1551053335 | Location: 38.7946, 106.5348 | Exclude: "
    * Query: "Hey, can you find me the blood of blue creatures?"
      Output: "Organism: organism | Genus: Cyanocitta, Dendrobates, Glaucus, Paracanthurus, Passerina | Attributes: blood, blue | Country:  | Time: | Location: | Exclude: "



    **Now Process This Query**:
    Query: '{query}'
    """
    return prompt


def format_query_gpt(query):
    """
    Formats the query and sends it to Azure OpenAI for structured data extraction.
    """
 
    prompt = get_prompt(query)
    # Call Azure OpenAI API
    response = client.chat.completions.create(
        model=deployment,  # Uses deployment name instead of model
        messages=[{"role": "user", "content": prompt.strip()}],
        max_tokens=120,  # Reduced max_tokens to make the output shorter
        temperature=0,
    )

    # Extract the response text
    output_text = response.choices[0].message.content.strip()
    return output_text

def format_query_abstract(query):
    """
    Formats the query and sends it to Azure OpenAI for structured data extraction.
    """
 
    prompt = get_prompt_abstract(query)
    # Call Azure OpenAI API
    response = client.chat.completions.create(
        model=deployment,  # Uses deployment name instead of model
        messages=[{"role": "user", "content": prompt.strip()}],
        max_tokens=120,  # Reduced max_tokens to make the output shorter
        temperature=0,
    )

    # Extract the response text
    output_text = response.choices[0].message.content.strip()
    return output_text


def format_query(query):
    url = "https://openrouter.ai/api/v1/chat/completions"
    with open("../api_key.txt", "r") as file:
        api_key = file.read().strip()  # Remove any whitespace or newline

    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your real API key
        "Content-Type": "application/json"
    }

    prompt = get_prompt(query)

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

def create_filter_dict(text):
    text = text.split("|")

    def safe_split(index):
        try:
            t1, t2 = text[index].split(":")[1].split(",")
            return t1,t2
        except (IndexError, ValueError):
            return "", ""

    t1, t2 = safe_split(4)
    l1, l2 = safe_split(5)
    try:
        country_str = text[3].split(":")[1].strip()
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
