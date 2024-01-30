# MGnify API Data Retrieval Scripts
The repository is designed to retrieve information and results from MGnify studies corresponding to a specific biome.

---

## Table of contents
- [Description](#description) - Overview of the project's purpose and goals
- [Getting started](#getting-started) - Instructions on how to begin with this project
- [Repository structure](#repository_structure) - A layout of the repository's architecture, describing the purpose of each file or directory
- [Next steps](#next-steps) - Next challanges and improvements for the repository 
- [Authors](#authors) - List of contributors to the project
- [Acknowledgments](#acknowledgement) - Credits and thanks to those who helped with the project

## Description <a name = "description"></a>
The repository is designed to gather information and results from MGnify.
This API allows for the exploration of studies originating from various biomes around the world.
The codes provided by this repository enable us to acquire the necessary identifiers to obtain metadata and FASTQ files required for multi-omic analyses.
The term "multi-omic analysis" refers to the [repository](https://github.com/biosustain/dsp_nf-metagenomics) developed in Nextflow, which carries out preprocessing and processing of bioinformatic data.


## Getting started <a name = "getting-started"></a>
Proceeding with the steps to gather the data
0. set up a Python virtual environment and install required libraries (specified in the `Pipfile` or `requirements.txt` file).
1. `Functions_getInfo_MGnify_studies_analyses.py`: retrieves a summary of MGnify studies and analyses for a given biome and data type (amplicon, shotgun metagenomics, metatranscriptomic, or assembly). The attributes of the api requests can be modified in the script (example running 
`Scripts/example_main_get_summary_studies_and_analyses.py`).
2. `Functions_get_results_from_MGnifystudy.py`: obtains abundance and functional tables, as well as other results for a MGnify study (example running `Scripts/example_main_get_results_from_MGnifystudy.py`).
3. `Functions_get_samplesMetadata_from_MGnifystudy.py`: obtains metadata for the samples of a MGnify study (example running `Scripts/example_main_get_samplesMetadata_from_MGnifystudy.py`).
4. `get_fastq_from_list_ids.py`: obtains FASTQ files from MGnify studies.

Modify the scripts to change the biome of interest, the data types to include, the desired study, and other attributes from the get requests to the MGnify API.


Consider to use [Pipenv](https://pipenv.pypa.io/en/latest/) to create a Python virtual environment, which allows the management of python libraries and their dependencies.
You can find a detailed guide on how to use pipenv [here](https://realpython.com/pipenv-guide/).
Each Pipenv virtual environment has a `Pipfile` with the names and versions of libraries installed in the virtual environment, and a `Pipfile.lock`, a JSON file that contains versions of libraries and their dependencies.

To create a Python virtual environment with libraries and dependencies required for this project, you should clone this GitHub repository, open a terminal, move to the folder containing this repository, and run the following commands:

```bash
# Install pipenv
$ pip install pipenv

# Create the Python virtual environment 
$ pipenv install

# Activate the Python virtual environment 
$ pipenv shell
```

If you are using an Azure VM, keep in mind the following considerations:
1. Pipenv might not work as its installation path may not be included in the system's PATH.
2. The Python version might not be up-to-date for installing a Pip package.

```bash
# check where it is located
$ pip show pipenv | grep Location

# open the shell configuration file
$ nano /home/azureuser/.bashrc

# add this line at the end of the file and save the changes
$ export PATH="$PATH:/home/azureuser/.local/bin"

# reload the shell configuration file
$ source /home/azureuser/.bashrc

# verify the version which should now be recognized
$ pipenv --version
```
In case your python version is outdated, it should be updated to version 3.11

```bash
# add a PPA  
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update

# install the new version to be able to activate the pipenv environment
sudo apt install python3.11
```  

Alternatively, you can create a conda virtual environment with the required libraries using the `requirements.txt` file.
To do this, you should clone this GitHub repository, open a terminal, move to the folder containing this repository, and run the following commands:

```bash
# Create the conda virtual environment
$ conda create --name retrieve_info_MGnifyAPI python=3.11

# Activate the conda virtual environment
$ conda activate retrieve_info_MGnifyAPI

# Install pip
$ conda install pip

# Install libraries and dependencies with pip 
$ pip install -r requirements.txt
```

## Obtain raw result files for a MGnify study
The `bulk_download` option of the `mg-toolkit` Python package provides a command line interface to download raw result files for a MGnify study.
For instance, to download the raw results files for the taxonomic analysis of the study [MGYS00001392](https://www.ebi.ac.uk/metagenomics/studies/MGYS00001392) obtained with the pipeline 5 or greater, you can run the following command:

```bash
$ mg-toolkit bulk_download -a MGYS00001392 --result_group taxonomic_analysis_unite -o Output/
```

You can find more information about this package and additional options [here](https://pypi.org/project/mg-toolkit/). 

## Repository structure <a name = "repository_structure"></a>
The main files and directories of this repository are:

|File|Description|
|:-:|---|
|[Scripts/](Scripts/)|Folder with Python scripts to to get information and results from MGnify studies for a given biome and study type|
|[Output/](Results/)|Folder to save the resulting files|
|[Pipfile](Pipfile)|File with names and versions of packages installed in the virtual environment|
|[requeriments.txt](requeriments.txt)|File with names and versions of packages installed in the virtual environment|
|[Pipfile.lock](Pipfile.lock)|Json file that contains versions of packages, and dependencies required for each package|


## Next steps <a name = "next-steps"></a>
1. rewrite the python scripts using if __name__=='__main__'  
2. make the functions shorter 
3. create a new python script/function to upload FASTQ files in Azure container given a credentials file
4. create a Nextflow pipeline able to parallelise the download of FASTQ files


## Authors <a name = "authors"></a>
Contact me at [sayalaruano](https://github.com/sayalaruano) or [marcor@dtu.dk](https://github.com/marcoreverenna) for more detail or explanations.


## **Further details**
The [MGnify documentation](https://docs.mgnify.org/src/docs/api.html) provides more information about the API. Also, you can browse the API endpoints interactively [here](https://www.ebi.ac.uk/metagenomics/api/latest/).

