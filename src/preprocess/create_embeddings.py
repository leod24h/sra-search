import os
import glob
import pandas as pd
from sentence_transformers import SentenceTransformer
import time
# Load the model once (adjust the path as needed)
model = SentenceTransformer('../all-MiniLM-L6-v2', device='cuda')

# Define input and output folders
input_folder = "../SRA-Curated"
output_folder = "../embeddings"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Get a list of all CSV files in the input folder
csv_files = sorted(glob.glob(os.path.join(input_folder, "*.csv")))

for csv_file in csv_files:
    start = time.time()
    # Build the output file name using the original CSV name
    base_filename = "embeddings-" + os.path.basename(csv_file).split("-")[-1]
    output_csv = os.path.join(output_folder, base_filename)
    
    # Check if output file already exists; if so, skip processing
    if os.path.exists(output_csv):
        print(f"Skipping {csv_file} because {output_csv} already exists.")
        continue

    # Load CSV into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Create formatted strings for each row using desired columns.
    formatted_strings = [
        f"Organism: {row.organism} | Country: {row.country} | Attributes: {row.attribute}"
        for row in df.itertuples(index=False)
    ]
    
    # Compute embeddings (returns a numpy array of shape (num_rows, embedding_dim))
    embeddings = model.encode(formatted_strings, batch_size=3072)
    
    # Convert each embedding to a comma-separated string so it can be stored in a CSV cell.
    embeddings_str = [", ".join(map(str, emb)) for emb in embeddings]
    
    # Create a new DataFrame with the 'acc' column and the embeddings
    result_df = pd.DataFrame({
        "acc": df["acc"],
        "embedding": embeddings_str
    })

    # Save the result as a CSV
    result_df.to_csv(output_csv, index=False)
    print(f"Saved embeddings to {output_csv} in {time.time() - start:.2f} seconds.")
