#!/usr/bin/env python

""" This python script downloads fastq file given a biome related to MGnify.
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
from utils import *
import requests
import os
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import json
from ftplib import FTP
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

if __name__ == "__main__":
    # setting the variables for FTP and Azure
    server_address = 'ftp.sra.ebi.ac.uk'
    remote_directory = '/vol1/fastq'  # Remote directory where FASTQ files are stored
    # set variables for MGnify
    biome = "root:Engineered:Wastewater"
    biome_lower = biome.replace(":", "_").lower()
    experiments = ("metagenomic","metatranscriptomic","assembly")
    output_path = '../outputs/'
    df_summary_dict = {}
    local_directory_base = '../outputs'  # Base local directory to save files
    
    #accession = 'ERR1356751'  # Sostituisci con il tuo ID di accessione
    #local_download_directory = f'../outputs/Unified_analyses/{accession}/'
    """

    # running function form utils
    print('\033[93m' + 'STARTING STEP 1: fetch_biomes_and_save'+ '\033[0m')
    fetch_biomes_and_save(output_dir= output_path)

    print('\033[93m' + 'STARTING STEP 2: get_studies_and_analyses_summary'+ '\033[0m')
    for exp in experiments:
        print(f"Processing experiment type: {exp}")
        df_summary = get_studies_and_analyses_summary(biome_name=biome,experiment_type=exp)
        df_summary_dict[exp] = df_summary  # Aggiungi il DataFrame al dizionario

        # save the CSV file
        df_summary.to_csv(os.path.join(output_path, f"{biome_lower}_{exp}_summary.csv"), index=False)
        combined_df = pd.concat(df_summary_dict.values(), axis=0)
        combined_df.to_csv(os.path.join(output_path, 'combined_dataframe.csv'), index=False)

    combined_df = pd.read_csv(os.path.join(output_path, 'combined_dataframe.csv'))
    
    print('\033[93m' + 'STARTING STEP 3: explore_dataset' + '\033[0m')
    display(combined_df.dtypes)
    explore_dataset(combined_df)
    
    print('\033[93m' + 'STARTING STEP 4: feature_engineering' + '\033[0m')
    combined_df_updated = feature_engineering(combined_df)
    display(combined_df_updated['concatenated_ids'].value_counts())

    print('\033[93m' + 'STARTING STEP 5: removing_duplicates' + '\033[0m')
    new_dataframe = removing_duplicates(combined_df_updated)
    print(new_dataframe["initials_run"].value_counts())

    print('\033[93m' + 'STARTING STEP 6: save_filtered_ids_to_file' + '\033[0m')
    save_filtered_ids_to_file(dataframe = new_dataframe,
                          filter_column = 'initials_run',
                          filter_value = 'ERR',
                          output_column = 'assembly_run_id',
                          output_path = '../outputs')
    """
    # load personal credentials for Azure connection
    credentials = load_credentials('../credentials.json')

    # download fastq files and push them in the storage account
    with open('../outputs/assembly_run_ids.txt', 'r')as file:
        accession_ids = file.read().splitlines()

    for accession in accession_ids:
        print(f"Processing {accession}...")
        download_files_and_upload_to_azure(server_address,
                                           accession,
                                           local_directory_base = '../outputs',
                                           azure_connection_string = f"DefaultEndpointsProtocol=https;AccountName={ credentials['storageAccountName']};AccountKey={credentials['storageAccountKey']};EndpointSuffix=core.windows.net",
                                           azure_container_name = 'retrievefastq'
                                           )
        print(f"Completed processing for {accession}.")