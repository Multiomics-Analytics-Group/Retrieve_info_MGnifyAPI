# ------------------------------------------------------------------------------------------------------
# Script: Functions_get_samplesMetadata_from_MGnifystudy.py
# Author: Sebastian Ayala Ruano
# Date: 09-12-2023
# Description: This script retrieves metadata for all samples in a given MGnify study.
# Version: 1.0
# License: MIT License
# Usage: call the functions from external scripts. See example_main_get_samplesMetadata_from_MGnifystudy.py
# Warning: The script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/Multiomics-Analytics-Group/Retrieve_info_MGnifyAPI/blob/main/Scripts/Functions_get_samplesMetadata_from_MGnifystudy.py
# ------------------------------------------------------------------------------------------------------
import requests

def get_samples_metadata_from_MGnifystudy(study_accession):
    '''Function to retrieve metadata for all samples in a given MGnify study
    Input: study_accession (str) - MGnify study accession for the GET request, e.g. "MGYS00001392"
    Output: results_MGnify_study (json) - json file with the information of the samples metadata for the MGnify study'''
    
    base_url = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"
    endpoint = f"{base_url}/{study_accession}/samples"

    print(f"Making GET request to: {endpoint}")
    response = requests.get(endpoint)

    if response.status_code == 200:
        samples_metadata_MGnifystudy = response.json()
        print("GET request successful.")

        return samples_metadata_MGnifystudy
    else:
        print(f"Error: {response.status_code}")
        return None