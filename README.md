# MGnify API Data Retrieval Scripts
Scripts to get information from MGnify studies and analyses for a given biome using its API.

## **How to use the scripts?**
1. Set up a Python virtual environment and install required libraries (specified in the `Pipfile` or `requirements.txt` file).
2. Run `Get_metag_studies_fromMGnify.py` to fetch a list of metagenomic studies for a given biome, without information about the data types (amplicon, shotgun metagenomics, metatranscriptomic, or assembly).
3. Execute `Get_metag_analyses_fromMGnify.py` to retrieve a list of metagenomic analyses from all studies in the desired biome, with data type information. The script also generates a file that filters studies based on their data type.

Modify the scripts to change the biome of interest, the data types to include, and other attributes from the get requests to the MGnify API.

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

## **Structure of the repository**
The main files and directories of this repository are:

|File|Description|
|:-:|---|
|[Scripts/](Scripts/)|Folder with Python scripts to retrive lists of metagenomic studies and anaylises from MGnify for a given biome|
|[Results/](Results/)|Folder to save the resulting CSV files|
|[Pipfile](Pipfile)|File with names and versions of packages installed in the virtual environment|
|[requeriments.txt](requeriments.txt)|File with names and versions of packages installed in the virtual environment|
|[Pipfile.lock](Pipfile.lock)|Json file that contains versions of packages, and dependencies required for each package|

## **Further details**
The [MGnify documentation](https://docs.mgnify.org/src/docs/api.html) provides more information about the API. Also, you can browse the API endpoints interactively [here](https://www.ebi.ac.uk/metagenomics/api/latest/).

