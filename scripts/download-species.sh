#!/bin/bash

# Exit on error
set -e

# Get the species name from the first argument
species_name=$1

# Check if species name is provided
if [ -z "$species_name" ]; then
    echo "Error: Species name is required"
    echo "Usage: $0 <species-name>"
    exit 1
fi

# Run the Python script
echo "Downloading annotations for $species_name..."
python ../scripts/download-species.py "$species_name" 