#!/usr/bin/env python

""" This python script downloads fastq file given an ACCESSION related to MGnify.
 __  __ 
|  \/  | 
| \  / | ___  _ __   __ _ 
| |\/| |/ _ \| '_ \ / _` |
| |  | | (_) | | | | (_| |
|_|  |_|\___/|_| |_|\__,_|

__authors__ = Marco Reverenna
__copyright__ = Copyright 2024-2025
__reserach-group__ = Multi-omics network analysis
__date__ = 02 Feb 2024
__maintainer__ = Marco Reverenna
__email__ = marcor@dtu.dk
__status__ = Dev
"""

# import libraries
import requests
import os
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import json
from ftplib import FTP
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def fetch_biomes_and_save(output_dir):
    """
    Fetches the list of biomes from the MGnify API and saves it to a text file in the specified output directory.
    The function makes a GET request to the MGnify API's biomes endpoint, extracts the biome IDs from the response,
    and writes them to a file named 'mgnify_biomes_list.txt' within the given output directory.

    Args:
        output_dir (str): The directory path where the biomes list file will be saved. The directory must exist.

    Note:
        This function requires the 'requests' library for making HTTP requests and 'os' library for file path operations.
    """
    url = "https://www.ebi.ac.uk/metagenomics/api/v1/biomes"
    response = requests.get(url)
    if response.status_code == 200:
        biomes_data = response.json()
        biomes_list = [biome['id'] for biome in biomes_data['data']]
        
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write the biome IDs to a file
        with open(os.path.join(output_dir, "mgnify_biomes_list.txt"), 'w') as file:
            for biome_name in biomes_list:
                file.write(f"{biome_name}\n")
                
        print("Biomes list saved successfully.")
        
    else:
        print("Failed to retrieve biomes. Status code:", response.status_code)



def get_studies_and_analyses_summary(biome_name, experiment_type, output_dir = '../outputs'):
    """
    Fetches and summarizes studies and analyses data from the MGnify API based on the specified biome name
    and experiment type. It saves the raw data as JSON and returns a merged DataFrame summary.

    This function queries the MGnify API for studies and analyses related to a specific biome and experiment type.
    The results are saved in separate JSON files within the specified output directory and then processed to
    create and return a comprehensive DataFrame summary.

    Args:
        biome_name (str): The name of the biome to filter studies and analyses.
        experiment_type (str): The type of experiment to filter analyses.
        output_dir (str, optional): The directory path where the JSON files will be saved. Defaults to '../outputs'.

    Returns:
        pd.DataFrame: A DataFrame summarizing the studies and analyses, including key details like study ID,
                      study name, number of samples, and related analysis information.
    """

    # API URLs for fetching studies and analyses data
    urls = {"studies": "https://www.ebi.ac.uk/metagenomics/api/v1/studies", "analyses": "https://www.ebi.ac.uk/metagenomics/api/v1/analyses"}

    # common parameters for API requests
    common_params = {"biome_name": biome_name}
    all_data = {"studies": [], "analyses": []}

    # connection request
    for key, url in urls.items():
        if key == "studies" and all_data["studies"]:
            continue

        params = common_params.copy()
        if key == "analyses":
            params.update({
                "lineage": biome_name,
                "experiment_type": experiment_type
            })

        page = 1
        
        while True:
            try:
                print(f"Retrieving data for page {page}...")
                params["page"] = page
                response = requests.get(url, params=params)
                response.raise_for_status()  # errors codes HTTP
                
                data = response.json()["data"]
                page_info = response.json()["meta"]["pagination"]
                all_data[key].extend(data)
                print(f"Page {page} retrieved successfully. Total pages: {page_info['pages']}")

                if page >= page_info["pages"]:
                    break
                page += 1
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
                break
            except Exception as err:
                print(f"An error occurred: {err}")
                break
        
        # save json files
        if key == "studies":
            output_file_path = os.path.join(output_dir, "mgnify_studies.json")
        else:
            output_file_path = os.path.join(output_dir, f"mgnify_analyses_{experiment_type}.json")
        
        with open(output_file_path, "w") as outfile:
            json.dump(all_data[key], outfile)
        print(f"{key.capitalize()} data for {experiment_type} saved to {output_file_path}")


    # building dataframes
    studies_columns = ['study_id', 'study_name', 'n_samples', 'bioproject', 'centre_name', 'biomes']
    studies_data = []
    for item in all_data['studies']:
        studies_data.append({
            'study_id': item['id'],
            'study_name': item['attributes'].get('study-name', ''),
            'n_samples': item['attributes'].get('samples-count', 0),
            'bioproject': item['attributes'].get('bioproject', ''),
            'centre_name': item['attributes'].get('centre-name', ''),
            'biomes': ", ".join([biome['id'] for biome in item['relationships']['biomes']['data']])
            })
    df_studies = pd.DataFrame(studies_data, columns=studies_columns)

    analyses_columns = ['analysis_id', 'experiment_type', 'pipeline_version', 'instrument_platform', 'study_id', 'sample_id', 'assembly_run_id']
    analyses_data = []
    for item in all_data['analyses']:
        analyses_data.append({
            'analysis_id': item['id'],
            'experiment_type': item['attributes'].get('experiment-type', ''),
            'pipeline_version': item['attributes'].get('pipeline-version', ''),
            'instrument_platform': item['attributes'].get('instrument-model', ''),
            'study_id': item['relationships']['study']['data'].get('id', '') if item['relationships'].get('study') else '',
            'sample_id': item['relationships']['sample']['data'].get('id', '') if item['relationships'].get('sample') else '',
            'assembly_run_id': item['relationships'].get('assembly', {}).get('data', {}).get('id', '') if item['attributes'].get('experiment-type') == 'assembly' else item['relationships'].get('run', {}).get('data', {}).get('id', '')
            })
    df_analyses = pd.DataFrame(analyses_data, columns=analyses_columns)

    # merging dataframe and return it
    df_summary = pd.merge(df_analyses, df_studies, on='study_id', how='left')
    
    return df_summary



def explore_dataset(dataset):
    """
    Explores the given dataset by printing out statistics and information related to its composition.
    This includes the total number of unique studies, the distribution of unique assembly run IDs per study,
    the presence of missing values across variables, and the median number of samples per biome.

    Args:
        dataset (pd.DataFrame): The dataset to be explored. It must contain the columns 'study_id',
                                'assembly_run_id', 'biomes', and 'n_samples' among others.

    Note:
        The function assumes 'combined_df' is the dataset passed through the 'dataset' argument for some print statements.
        Replace 'combined_df' with 'dataset' in the actual implementation if 'combined_df' is a typo.
    """

    print("\nTotal number of unique studies")
    print(dataset['study_id'].nunique())
    print('\033[92m' + "-" * 25 + '\033[0m')

    print("\nNumber of unique assembly_run_id per study_id")
    print(dataset.groupby('study_id')['assembly_run_id'].nunique())
    print('\033[92m' + "-" * 25 + '\033[0m')

    # missing data
    print("\nMissing values per variable")
    print(dataset.isnull().sum())
    any_missing_data = dataset.isnull().values.any()
    print(f"Are there any missing data in the dataframe? {'yes' if any_missing_data else 'no'}")
    print('\033[92m' + "-" * 25 + '\033[0m')

    print("\nNumber of samples per biome (median)")
    print(dataset.groupby('biomes')['n_samples'].median().reset_index())
    print('\033[92m' + "-" * 25 + '\033[0m')

    experiment_type_counts = dataset["experiment_type"].value_counts()
    biomes_counts = dataset["biomes"].value_counts()
    print('\033[92m' + "-" * 25 + '\033[0m')
    
    print("\nDistribuzione di experiment_type:")
    print(experiment_type_counts)

    print("\nDistribuzione di biomes:")
    print(biomes_counts)
    print('\033[92m' + "-" * 25 + '\033[0m')



def feature_engineering(dataframe):
    """
    Performs feature engineering on the provided dataframe. It includes mapping pipeline versions
    to a simplified numerical scale, extracting initials from the 'assembly_run_id', and concatenating
    multiple identifiers into a single 'concatenated_ids' column.
    
    The function does the following transformations:
    - Maps 'pipeline_version' to 'pipeline_mapped' using a predefined version mapping for simplification.
    - Extracts the first three characters from 'assembly_run_id' and stores them in 'initials_run'.
    - Concatenates 'study_id', 'sample_id', 'assembly_run_id', and 'bioproject' into a new 'concatenated_ids' column.

    Args:
        dataframe (pd.DataFrame): The input dataframe to process. It must contain the columns 'pipeline_version',
                                  'assembly_run_id', 'study_id', 'sample_id', and 'bioproject'.

    Returns:
        pd.DataFrame: The dataframe with added features based on the original data.
    """

    version_mapping = {1.0: 1, 2.0: 2, 3.0: 3, 4.0: 4, 4.1: 5, 5.0: 6}
    dataframe['pipeline_mapped'] = dataframe['pipeline_version'].map(version_mapping)

    # extract the first three characters
    dataframe['initials_run'] = dataframe['assembly_run_id'].str[:3]

    dataframe['concatenated_ids'] = dataframe['study_id'] + '_' + dataframe['sample_id'] + '_' + dataframe['assembly_run_id'] + '_' + dataframe['bioproject']

    return dataframe



def removing_duplicates(dataframe):
    """
    Removes duplicate rows from the dataframe based on the 'concatenated_ids' column.
    Among duplicates, it retains only the row with the highest value in the 'pipeline_mapped' column.
    
    This function first counts the occurrences of each unique 'concatenated_ids' value to identify duplicates.
    For each set of duplicates, it sorts them by 'pipeline_mapped' in descending order and keeps the top one,
    effectively removing duplicates with lower 'pipeline_mapped' values. Rows without duplicates are preserved as is.

    Args:
        dataframe (pd.DataFrame): The dataframe to process. It must contain the columns 'concatenated_ids' and 'pipeline_mapped'.

    Returns:
        pd.DataFrame: A dataframe with duplicates removed based on the above criteria.
    """

    counts = dataframe['concatenated_ids'].value_counts()
    duplicates = (counts > 1).sum()

    print(f"Number of duplicates in the dataset: {duplicates}")

    filtered_df = pd.DataFrame()

    # Process each ID with more than one occurrence to identify and keep only the desired row
    for id, count in counts[counts > 1].items():
        # Select rows matching the current duplicate ID
        dup_rows = dataframe[dataframe['concatenated_ids'] == id]
        # Sort these rows by 'pipeline_mapped' in descending order and select the top one
        highest_pipeline_mapped_row = dup_rows.sort_values(by='pipeline_mapped', ascending=False).head(1)
        # Append the selected row to the filtered DataFrame
        filtered_df = pd.concat([filtered_df, highest_pipeline_mapped_row], ignore_index=True)
    
    # Identify and include rows that are not duplicates
    non_duplicate_ids = counts[counts == 1].index
    non_duplicate_rows = dataframe[dataframe['concatenated_ids'].isin(non_duplicate_ids)]
    filtered_df = pd.concat([filtered_df, non_duplicate_rows], ignore_index=True)

    # Return the DataFrame with duplicates removed
    return filtered_df

def load_credentials(file_path = '~/Retrieve_info_MGnifyAPI/credentials.json'):
    """Load the credentials for connecting with Azure

    Args:
        file_path (file_json): file which contains your credentials to Azure account

    Returns:
        str: Account name and key to access to your account
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_filtered_ids_to_file(dataframe, output_column, filter_column, filter_value, output_path):
    """
    Filters a DataFrame for rows where filter_column equals filter_value,
    extracts values from output_column of those rows, and saves them to a file.

    Parameters:
    - dataframe: pd.DataFrame, the DataFrame to filter.
    - filter_column: str, the name of the column to apply the filter on.
    - filter_value: str, the value to filter rows by in the filter_column.
    - output_column: str, the name of the column from which to extract values.
    - output_file_path: str, the path to the file where the output will be saved.

    Returns:
    - None, but saves a file at output_file_path with one value per line from the output_column.
    """

    filtered_df = dataframe[dataframe[filter_column] == filter_value]

    output_values = filtered_df[output_column].tolist()

    with open(os.path.join(output_path, 'assembly_run_ids.txt' ), 'w') as file:
        for value in output_values:
            file.write(f"{value}\n")

    print(f"Saved {output_column} to {output_path}")

def download_files_and_upload_to_azure(server_address, accession, local_directory_base, azure_connection_string, azure_container_name):
    """ This function downloads fastq files given a txt file which contains the IDs, and uploads them to Azure Blob Storage.

    Args:
        server (str): server address (first part of the path)
        input_ids_file (file_txt): file which contains a list of IDs obtained from an ACCESSION
        remote_directory (str): path of the folder where are stored the fastq files
        local_directory (str): path to your local directory which contains script and data
        azure_connection_string (str): Azure Storage account connection string
        azure_container_name (str): Name of the Azure Blob Storage container
    """
    found = False
    ftp = FTP(server_address)
    ftp.login()  # Non sono richieste credenziali per questo server

    # Crea il client di servizio blob di Azure con la stringa di connessione
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    container_client = blob_service_client.get_container_client(azure_container_name)

    # Estrae le prime tre lettere e i primi tre numeri dall'ID dell'accessione per formare ID_start
    ID_start = accession[:6]
    base_path = f'/vol1/fastq/{ID_start}/'

    try:
        # Prova prima nella directory principale dell'accessione
        path = f"{base_path}{accession}/"
        try:
            ftp.cwd(path)
            files = ftp.nlst()
            if files:
                found = True
        except Exception as e:
            # Se non trova file nella directory principale, cerca nelle subfolders
            for i in range(1, 1000):
                subfolder = f"{i:03}"
                path = f"{base_path}{subfolder}/{accession}/"
                try:
                    ftp.cwd(path)
                    files = ftp.nlst()
                    if files:
                        found = True
                        break
                except Exception as e:
                    continue

        # Se i file sono stati trovati, scaricali e caricali su Azure
        if found:
            for file in files:
                local_file_path = os.path.join(local_directory_base, file)
                with open(local_file_path, 'wb') as local_file:
                    ftp.retrbinary('RETR ' + file, local_file.write)

                # Carica il file su Azure Blob Storage
                blob_client = container_client.get_blob_client(blob=os.path.join(accession, file))
                with open(local_file_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                
                # Rimuovi il file locale dopo il caricamento, se desiderato
                os.remove(local_file_path)

            print(f"Files for {accession} downloaded and uploaded to Azure.")
        else:
            print("Files not found in any location.")
    finally:
        ftp.quit()
        