#!/usr/bin/env python3

from biomart import BiomartServer
import pandas as pd
import os
import sys
import argparse
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError, ConnectionError

# Main Ensembl server and Ensembl Plants server
ENSEMBL_SERVER = "http://www.ensembl.org/biomart"
PLANTS_SERVER = "http://plants.ensembl.org/biomart"

# Configure retry strategy with more aggressive settings
retry_strategy = Retry(
    total=5,  # increased number of retries
    backoff_factor=2,  # increased backoff factor
    status_forcelist=[500, 502, 503, 504, 408, 429],  # added more status codes
    allowed_methods=["GET", "POST"],  # explicitly allow methods
    respect_retry_after_header=True  # respect server's retry-after header
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

# Species to dataset mapping
species_to_dataset = {
    "homo-sapiens": ("hsapiens_gene_ensembl", ENSEMBL_SERVER),
    "mus-musculus": ("mmusculus_gene_ensembl", ENSEMBL_SERVER),
    "rattus-norvegicus": ("rnorvegicus_gene_ensembl", ENSEMBL_SERVER),
    "danio-rerio": ("drerio_gene_ensembl", ENSEMBL_SERVER),
    "drosophila-melanogaster": ("dmelanogaster_gene_ensembl", ENSEMBL_SERVER),
    "arabidopsis-thaliana": ("athaliana_eg_gene", PLANTS_SERVER),
    "saccharomyces-cerevisiae": ("scerevisiae_gene_ensembl", ENSEMBL_SERVER),
    "caenorhabditis-elegans": ("celegans_gene_ensembl", ENSEMBL_SERVER),
    "gallus-gallus": ("ggallus_gene_ensembl", ENSEMBL_SERVER),
    "bos-taurus": ("btaurus_gene_ensembl", ENSEMBL_SERVER),
    "sus-scrofa": ("sscrofa_gene_ensembl", ENSEMBL_SERVER)
}

base_attributes = [
    'ensembl_gene_id',
    'external_gene_name',
    'description',
    'gene_biotype',
    'chromosome_name',
    'start_position',
    'end_position',
    'strand',
    'entrezgene_id',
    'uniprot_gn_id'  # May not exist for all
]

output_columns = [
    "Ensembl Id", "Gene symbol", "Description", "Gene biotype",
    "Chromosome", "Start", "End", "Strand", "Entrez ID", "UniProt ID"
]

def get_capitalized_dir(species_name):
    """Convert species name to capitalized directory name."""
    # Split by hyphen, capitalize first word, keep others lowercase, join with underscore
    words = species_name.split("-")
    return "_".join([words[0].capitalize()] + [word.lower() for word in words[1:]])

def download_species_annotations(species_name):
    """Download gene annotations for a specific species."""
    if species_name not in species_to_dataset:
        print(f"❌ Error: Unknown species '{species_name}'")
        print(f"Available species: {', '.join(species_to_dataset.keys())}")
        sys.exit(1)

    dataset_name, server_url = species_to_dataset[species_name]
    safe_name = species_name.replace("-", "_")
    capitalized_dir = get_capitalized_dir(species_name)
    
    print(f"🔍 Fetching annotations for {species_name}...")

    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join("data", capitalized_dir)
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize server with custom session
        server = BiomartServer(server_url, session=session)
        
        # Add retry logic for dataset retrieval
        max_retries = 5
        retry_delay = 10  # increased initial delay
        
        for attempt in range(max_retries):
            try:
                dataset = server.datasets.get(dataset_name)
                if not dataset:
                    raise ValueError(f"Dataset for {species_name} not found on {server_url}")
                break
            except (MaxRetryError, ConnectionError) as e:
                if attempt == max_retries - 1:
                    print(f"❌ Failed to connect to {server_url} after {max_retries} attempts")
                    raise
                print(f"⚠️ Connection attempt {attempt + 1} failed: {str(e)}")
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2

        # Try full attribute list
        response = dataset.search({'attributes': base_attributes})
        lines = response.raw.data.decode('utf-8').strip().split("\n")
        data = [line.split("\t") for line in lines]

        if len(data) == 0 or len(data[0]) != len(base_attributes):
            raise ValueError("Attribute mismatch – likely due to unsupported attribute")

        df = pd.DataFrame(data, columns=output_columns)
        output_file = os.path.join(data_dir, f"{safe_name}_gene_annotations.csv")
        df.to_csv(output_file, index=False)
        print(f"✅ Saved annotations to {output_file} ({len(df)} genes)")

    except Exception as e:
        print(f"❌ Error for {species_name}: {e}")
        print(f"🔁 Retrying without 'uniprot_gn_id'...")

        try:
            reduced_attrs = [attr for attr in base_attributes if attr != 'uniprot_gn_id']
            reduced_cols = [col for col in output_columns if col != "UniProt ID"]
            response = dataset.search({'attributes': reduced_attrs})
            lines = response.raw.data.decode('utf-8').strip().split("\n")
            data = [line.split("\t") for line in lines]

            df = pd.DataFrame(data, columns=reduced_cols)
            output_file = os.path.join(data_dir, f"{safe_name}_gene_annotations.csv")
            df.to_csv(output_file, index=False)
            print(f"✅ Saved annotations (no UniProt) to {output_file} ({len(df)} genes)")

        except Exception as e2:
            print(f"❌ Failed again for {species_name}: {e2}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download gene annotations for a specific species')
    parser.add_argument('species', help='Species name (e.g., homo-sapiens, mus-musculus)')
    args = parser.parse_args()
    
    download_species_annotations(args.species)

if __name__ == "__main__":
    main()