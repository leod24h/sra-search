# 🧬 SRA Metadata Search Tool

A powerful and efficient tool for **natural language** searching and filtering **Sequence Read Archive (SRA) metadata**, enabling researchers and bioinformaticians to query large-scale genomic datasets with ease and precision. The database contains 35M+ samples taken from 583,982 studies.

---
[!Frontend](../imgs/SRA Metadata Home)
## Overview
### Key Features
- **Natural Language Searching**: Perform searches using natural language queries to retrieve the most relevant runs from all SRA metadata.
- **LLM-Powered Query Interpretation**: Utilizes state-of-the-art **large language models (LLMs)** and **embeddings** to enable advanced semantic understanding and rapid retrieval.
- **Advanced Filtering**: Supports filtering by **geographical location, organism name, study type, publication date, sequencing platform, and more**.
- **Comprehensive Data Curation**: Aggregates, cleans, and organizes metadata to enhance searchability and usability.
- **Optimized for Large-Scale Genomic Datasets**: Efficient query execution on a database containing over **35 million** SRA records.
- **User-Friendly Interface**: A simple yet powerful UI designed for researchers, allowing seamless searching without requiring **SQL knowledge or domain-specific expertise**.

---

## Cost
Cost per query 0.000243 USD. ~ 500 queries = 1 HKD

### Semantic Search (Study)
Users can search for relevant study abstracts using either full text matching or semantic search. 

> Studies with ESBL

Would return relevant studies containing the 'ESBL' keyword, and then samples containing E.Coli. 

### Semantic Search (Sample)
Instead of manually filtering records, users can input natural language queries such as:

> "Malaysian Pangolin after 2017"

Our system processes the query and:
1. **Corrects typos** and interprets **context**.
2. **Extracts key attributes**, such as:
   - **Genus name**: *Manis*
   - **Country**: *Malaysia*
   - **Time range**: *after 2017*
3. **Finds the most relevant SRA records** within these constraints.

**Example Output:**
```
![Example Output](../imgs/example.png)
```

### Advanced Search
For more **specific** searches, users can apply structured **filters**. These can be used **alone or in combination** with semantic queries.

#### Available Filters:
- **Organism Name** *(e.g., Homo sapiens, Manis javanica)*
- **Geographical Location** *(e.g., Malaysia, USA, Europe)*
- **Time Range** *(e.g., Before 2010, Between 2015-2020)*
- **Study Type** *(e.g., Transcriptome, Metagenomics, WGS)*
- **Sequencing Platform** *(e.g., Illumina, PacBio, Oxford Nanopore)*
- **Read Length** *(e.g., >150bp, 50-100bp)*
- **Accession Number** *(e.g., PRJNA123456, SRR9876543)*

---

## Algorithm Breakdown
The system employs a multi-stage process for **query interpretation, embedding-based retrieval, and ranking** to ensure accurate and fast results.

### 1️⃣ Query Formatting & Expansion
- **Model:** *Gemini-2.0-flash-lite*
- **Task:** Transforms the user’s natural language query into structured categories.
- **Enhancements:**
  - **Handles typos** (e.g., "sueqncing" → "sequencing")
  - **Translates languages** (e.g., "西班牙蝙蝠" → "Spanish bat")
  - **Extracts key metadata** (e.g., "after 2015" → `year > 2015`)
  - **Expands synonyms** (e.g., "whole genome sequencing" → "WGS")

### 2️⃣ SQL Filtering
- **Combines extracted filters from both semantic search and user-defined filters.**
- **Executes optimized queries** on a PostgreSQL database with indexed metadata fields.

### 3️⃣ Embedding-Based Retrieval
- **Model:** *SentenceTransformers (BERT-based)*
- **Storage Format:** *Float16 embeddings for efficiency*
- **Search Mechanism:** Approximate Nearest Neighbor (ANN) retrieval with **pgvector**.

### 4️⃣ Optimized ANN Search with `pgvector`
- **Index Type:** IVFFLAT
- **Query Speed:** < 0.2 seconds per query on a **35M+ entry** dataset.
- **Benefits:** Fast, scalable search with minimal computational overhead.

### 5️⃣ Reranking with JinaAI
- **Purpose:** Re-ranks initial ANN-retrieved records to prioritize those that best match the **raw user query**.
- **Method:** Uses transformer-based **cross-encoder models** for **context-aware ranking**.

---

## Authors
Tracy Wong @ tracywong@d24h.hk
- Data curation, Front end & UI Development, PostgreSQL database, flask development

Leo Mok @ leom@d24h.hk
- Backend & LLM integration, PostgreSQL and pgvector setup, algorithm development

{Carlos}

## Development 
Source code is provided for 

### Software
- PostgreSQL 16<
- pgvector 0.8.0<
- Python 3.9
#### Python Packages
- flask 3.1.0
- psycopg2 2.9.10
- sentence-transformers 3.4.1
- pandas 2.2.3
- torch 2.6.0
- numpy 2.0.2

## References & Resources
- [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [JinaAI](https://github.com/jina-ai)
- [SentenceTransformers](https://www.sbert.net)

