# MgnifyAPI

#### MGnify API Data Retrieval Scripts
The repository is designed to retrieve information and results from MGnify studies corresponding to a specific biome.

---

## Table of contents
- [Description](#Description) - Overview of the project's purpose and goals
- [Installation](#installation) - Installing the env
- [Getting started](#getting-started) - Instructions on how to begin with this project
- [Repository structure](#repository-structure) - A layout of the repository's architecture, describing the purpose of each file or directory
- [Next steps](#next-steps) - Next challanges and improvements for the repository 
- [Authors](#authors) - List of contributors to the project

## Description
- The repository is designed to gather information and results from MGnify.
- This API allows for the exploration of studies originating from various biomes around the world.
- The codes provided by this repository enable us to acquire the necessary identifiers to obtain metadata and FASTQ files required for multi-omic analyses.
- The term "multi-omic analysis" refers to the [repository](https://github.com/biosustain/dsp_nf-metagenomics) developed in Nextflow, which carries out preprocessing and processing of bioinformatic data.

## Installation
1. Requires [poetry](https://python-poetry.org/docs/#installation) e.g.,
    ```bash 
    curl -sSL https://install.python-poetry.org | python3 -
    ```
2. Clone the repository
3. Navigate a terminal to the root of the local repository
4. The below command will take care of creating a virtual env, installing dependencies and setting up the project.
    ```bash
    poetry install --only main
    ```
5. (optional) To activate the environment shell you can 
    ```bash
    # get the command to run, then copy it nnd run it  
    poetry env activate

    # e.g. 
    source <path-to-venv>/bin/activate
    ```

## Getting started
### Retrieving data from Mgnify
1. Create a configuration (yaml) file. 

    example _**config.yaml**_
    ```yaml
    search params:
        biome name : 'root:Engineered:Biogas plant'  # Specify the biome to search for studies
        experiment types: ["metagenomic", "metatranscriptomic", "assembly"]  # List of experiment types to include

    output: 
        path: "/Users/someone/mgnify_data/biogas"    # Output directory for results and metadata
        download data folder: "downloads"            # Subfolder for downloaded study data

    urls:
        study info: "https://www.ebi.ac.uk/metagenomics/api/v1/studies"      # API endpoint for study metadata
        analyses info: "https://www.ebi.ac.uk/metagenomics/api/v1/analyses"  # API endpoint for analyses metadata
    ```

2. The following CLI will retrieve the study metadata and analysis data from Mgnify for the configured biome.
   ```bash
   mgnifyapi-get-studies -c <path-to-config.yaml>
   ``` 
   OR if you didn't activate the env (step 5 in [installation](#installation))
   ```bash
   poetry run mgnifyapi-get-studies -c <path-to-config.yaml>
   ```
> [!IMPORTANT]
> A log file is generated every run to <repo-root>/logs

That's it :)


#TODO 4. `get_fastq_from_list_ids.py`: obtains FASTQ files from MGnify studies.

> [!TIP]
> Obtain raw result files for a MGnify study
> The `bulk_download` option of the `mg-toolkit` Python package provides a CLI to download raw result files for a MGnify study. For instance, to download the raw results files for the taxonomic analysis of the study [MGYS00001392](https://www.ebi.ac.uk/metagenomics/studies/MGYS00001392) obtained with the pipeline 5 or greater, you can run the following command:
> `mg-toolkit bulk_download -a MGYS00001392 --result_group taxonomic_analysis_unite -o Output/`
> You can find more information about this package and additional options [here](https://pypi.org/project/mg-toolkit/). 

### Preprocessing data 
#TODO work in progress

## Next steps
<del>1. rewrite the python scripts using if __name__=='__main__'</del>  
<del>2. make the functions shorter</del>
3. create a new python script/function to upload FASTQ files in Azure container given a credentials file
4. create a Nextflow pipeline able to parallelise the download of FASTQ files

## Repository structure
#TODO

## Authors <a name = "authors"></a>
Contact me at [sayalaruano](https://github.com/sayalaruano) or [marcor@dtu.dk](https://github.com/marcoreverenna) or angel :) for more detail or explanations.


## **Further details**
The [MGnify documentation](https://docs.mgnify.org/src/docs/api.html) provides more information about the API. Also, you can browse the API endpoints interactively [here](https://www.ebi.ac.uk/metagenomics/api/latest/).

