# ------------------------------------------------------------------------------------------------------
# Script: Functions_get_results_from_MGnifystudy.py
# Author: Sebastian Ayala Ruano
# Date: 09-12-2023
# Description: This script retrieves abundance and functional tables, as well as other results for a given MGnify study. 
# The desired results to dowonload should be defined in the main script that calls the functions of this file.
# Version: 1.0
# License: MIT License
# Usage: call the functions from external scripts. See example_main_get_results_from_MGnifystudy.py
# Warning: The script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/Multiomics-Analytics-Group/Retrieve_info_MGnifyAPI/blob/main/Scripts/example_main_get_results_from_MGnifystudy.py
# ------------------------------------------------------------------------------------------------------
import os
import requests

def get_results_info_from_MGnifystudy(study_accession):
    '''Function to retrieve information about results for a given MGnify study
    Input: study_accession (str) - MGnify study accession for the GET request, e.g. "MGYS00001392"
    Output: results_MGnify_study (json) - json file with the information of the results for the MGnify study'''
    
    base_url = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"
    endpoint = f"{base_url}/{study_accession}/downloads"

    print(f"Making GET request to: {endpoint}")
    response = requests.get(endpoint)

    if response.status_code == 200:
        results_MGnify_study = response.json()
        print("GET request successful.")

        return results_MGnify_study
    else:
        print(f"Error: {response.status_code}")
        return None

def download_and_save_MGnifystudy_results(url, file_name, download_folder):
    '''Function to download and save results for a given MGnify study
    Input: url (str) - URL for the GET request, 
           file_name (str) - results file name, e.g. taxonomic assignments
           download_folder (str) - path for the download folder
    Output: void function, it does not have a return value, but downloads and saves the desired results for the MGnify study'''

    file_path = os.path.join(download_folder, file_name)
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File '{file_name}' downloaded and saved in '{download_folder}'.")
    else:
        print(f"Failed to download file from {url}. Status code: {response.status_code}")
