# dataset extractor LOTUS

[![Release](https://img.shields.io/github/v/release/fpgmaas/dataset-extractor-lotus)](https://img.shields.io/github/v/release/fpgmaas/dataset-extractor-lotus)
[![Build status](https://img.shields.io/github/actions/workflow/status/fpgmaas/dataset-extractor-lotus/main.yml?branch=main)](https://github.com/fpgmaas/dataset-extractor-lotus/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/fpgmaas/dataset-extractor-lotus/branch/main/graph/badge.svg)](https://codecov.io/gh/fpgmaas/dataset-extractor-lotus)
[![Commit activity](https://img.shields.io/github/commit-activity/m/fpgmaas/dataset-extractor-lotus)](https://img.shields.io/github/commit-activity/m/fpgmaas/dataset-extractor-lotus)
[![License](https://img.shields.io/github/license/fpgmaas/dataset-extractor-lotus)](https://img.shields.io/github/license/fpgmaas/dataset-extractor-lotus)
[![DOI](https://zenodo.org/badge/DOI/records/7534071.svg)](https://zenodo.org/records/7534071)

Extract specific elements/rows from the LOTUS dataset.

## How to run the LOTUS extractor
This is one possible example to run the script.

```bash
# navigater to a place, where you want to put the project
cd ./path/to/folder/

# clone it from git and enter the folder
git clone git@github.com:commons-research/dataset-extractor-lotus.git
cd dataset-extractor-lotus

# install the environment with poetry
## if poetry is not already installed, follow the following steps
pip install pipx
pipx install poetry

# Install from the poetry.lock file (command should be run in the same folder as the poetry.lock file)
poetry install

# run the script in poetry and get the help page 
poetry run python dataset_extractor_lotus/main.py -h

# run the script in the interactive mode
poetry run python dataset_extractor_lotus/main.py

```

## Interactive Mode
Example how to proceed:

```bash
Start interactive mode.
? Welcome to the "toydataset extractor" for the LOTUS datasets.
            Chose your action: 
  sampling
❯ download
  exit (Ctrl+C)
```

### Download dataset

```bash
Start interactive mode.
? Welcome to the "toydataset extractor" for the LOTUS datasets.
            Chose your action: download
The datasets will be searched from the internet. One moment please...
? Please choose your dataset to download (sorted from newest to oldest): 220916_frozen_metadata.csv.gz (record: 7085063)
? Enter path to download: data/
The dataset will be downloaded to data//220916_frozen_metadata.csv.gz (record: 7085063).
Download complete: 220916_frozen_metadata.csv.gz
```

### sampling from dataset

```bash
Start interactive mode.
? Welcome to the "toydataset extractor" for the LOTUS datasets.
            Chose your action: sampling
? Enter the filepath to sample from: data/220916_frozen_metadata.csv.gz
Before type:  String
After type:  Int32
? Please choose the taxonomy level to sample from: organism_taxonomy_05order
? Choose from which member to sample (522 options): Anthoathecata
? Please enter the amount of members to sample (max. 77): 32
? Please choose the output format: full
? Enter the output file name or existing filename to append: test_sampling.csv
File test_sampling.csv does not exist. Creating new file.
```


## Documentation
- **Github repository**: <https://github.com/commons-research/dataset-extractor-lotus.git>
- **Documentation with mkdocs** <https://commons-research.github.io/dataset-extractor-lotus/>

## Feedback
Please follow this [guidelines](CONTRIBUTING.md) for reporting a bug.  
For other issues please use <https://github.com/commons-research/dataset-extractor-lotus/issues>. 


## Releasing a new version
21.03.2024: v1.1 is released (interactive mode)  
07.03.2024: v1.0 is released (basic random sampling)