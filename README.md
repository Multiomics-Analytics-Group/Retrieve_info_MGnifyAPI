# MGnify API Data Retrieval Scripts
Scripts to get information and results from MGnify studies for a given biome and study type using its API.

## **How to use the scripts?**
1. Set up a Python virtual environment and install required libraries (specified in the `Pipfile` or `requirements.txt` file).
2. Use the functions from `Scripts/Functions_getInfo_MGnify_studies_analyses.py` to retrieve a summary of MGnify studies anad analyses for a given biome and data type (amplicon, shotgun metagenomics, metatranscriptomic, or assembly). The attributes of the api requests can be modified in the script. See an example of how to use these functions in the `Scripts/example_main_get_summary_studies_and_analyses.py` file.
3. Use the functions from `Scripts/Functions_get_results_from_MGnifystudy.py` to obtain abundance and functional tables, as well as other results for a MGnify study. See an example of how to use these functions in the `Scripts/example_main_get_results_from_MGnifystudy.py` file.

Modify the scripts to change the biome of interest, the data types to include, the desired study, and other attributes from the get requests to the MGnify API.

## **How to set up the environment to run the code?**
I used [Pipenv](https://pipenv.pypa.io/en/latest/) to create a Python virtual environment, which allows the management of python libraries and their dependencies. Each Pipenv virtual environment has a `Pipfile` with the names and versions of libraries installed in the virtual environment, and a `Pipfile.lock`, a JSON file that contains versions of libraries and their dependencies.

To create a Python virtual environment with libraries and dependencies required for this project, you should clone this GitHub repository, open a terminal, move to the folder containing this repository, and run the following commands:

```bash
# Install pipenv
$ pip install pipenv

# Create the Python virtual environment 
$ pipenv install

# Activate the Python virtual environment 
$ pipenv shell
```

You can find a detailed guide on how to use pipenv [here](https://realpython.com/pipenv-guide/).

Alternatively, you can create a conda virtual environment with the required libraries using the `requirements.txt` file. To do this, you should clone this GitHub repository, open a terminal, move to the folder containing this repository, and run the following commands:

```bash
# Create the conda virtual environment
$ conda env create --name retrieve_info_MGnifyAPI --file requirements.txt

# Activate the conda virtual environment
$ conda activate retrieve_info_MGnifyAPI
```

## **Obtain raw result files for a MGnify study**
The `bulk_download` option of the `mg-toolkit Python package` provides a command line interface to download raw result files for a MGnify study. For instance, to download the raw results files for the taxonomic analysis of the study [MGYS00001392](https://www.ebi.ac.uk/metagenomics/studies/MGYS00001392) obtained with the pipeline 5 or greater, you can run the following command:

```bash
$ mg-toolkit bulk_download -a MGYS00001392 --result_group taxonomic_analysis_unite -o Output/
```

You can find more information about this package and additional options [here](https://pypi.org/project/mg-toolkit/). 

## **Structure of the repository**
The main files and directories of this repository are:

|File|Description|
|:-:|---|
|[Scripts/](Scripts/)|Folder with Python scripts to to get information and results from MGnify studies for a given biome and study type|
|[Output/](Results/)|Folder to save the resulting files|
|[Pipfile](Pipfile)|File with names and versions of packages installed in the virtual environment|
|[requeriments.txt](requeriments.txt)|File with names and versions of packages installed in the virtual environment|
|[Pipfile.lock](Pipfile.lock)|Json file that contains versions of packages, and dependencies required for each package|

## **Further details**
The [MGnify documentation](https://docs.mgnify.org/src/docs/api.html) provides more information about the API. Also, you can browse the API endpoints interactively [here](https://www.ebi.ac.uk/metagenomics/api/latest/).

