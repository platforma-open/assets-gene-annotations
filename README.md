# Gene Annotations Assets

This package provides gene annotations for various species, sourced from Ensembl and Ensembl Plants databases. The annotations include gene IDs, symbols, descriptions, biotypes, chromosomal locations, and additional identifiers.

## Available Species

The package includes gene annotations for the following species:

- Homo sapiens (Human)
- Mus musculus (Mouse)
- Rattus norvegicus (Rat)
- Danio rerio (Zebrafish)
- Drosophila melanogaster (Fruit fly)
- Arabidopsis thaliana (Thale cress)
- Saccharomyces cerevisiae (Yeast)
- Caenorhabditis elegans (Nematode)
- Gallus gallus (Chicken)
- Bos taurus (Cattle)
- Sus scrofa (Pig)

## Package Structure

```
assets-gene-annotations/
├── catalogue/                 # Main catalogue package
├── homo-sapiens/             # Human gene annotations
├── mus-musculus/            # Mouse gene annotations
├── rattus-norvegicus/       # Rat gene annotations
├── danio-rerio/            # Zebrafish gene annotations
├── drosophila-melanogaster/ # Fruit fly gene annotations
├── arabidopsis-thaliana/   # Thale cress gene annotations
├── saccharomyces-cerevisiae/ # Yeast gene annotations
├── caenorhabditis-elegans/  # Nematode gene annotations
├── gallus-gallus/          # Chicken gene annotations
├── bos-taurus/            # Cattle gene annotations
├── sus-scrofa/           # Pig gene annotations
└── scripts/              # Utility scripts
    ├── download-species.py  # Python script for downloading annotations
    └── download-species.sh  # Bash wrapper for the Python script
```

## Data Format

Each species package contains gene annotations in CSV format with the following columns:

- Ensembl ID
- Gene Symbol
- Description
- Gene Biotype
- Chromosome
- Start Position
- End Position
- Strand
- Entrez ID
- UniProt ID (when available)

## Usage

### Building Individual Species Packages

To build annotations for a specific species:

```bash
cd <species-directory>
npm run build
```

For example:
```bash
cd homo-sapiens
npm run build
```

### Building All Packages

To build all species packages:

```bash
npm run build
```

## Dependencies

- Python 3.x
- Required Python packages (automatically installed):
  - pandas
  - biomart

## License

UNLICENSED 