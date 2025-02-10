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
# References: https://github.com/Multiomics-Analytics-Group/Retrieve_info_MGnifyAPI/blob/main/Scripts/Functions_get_results_from_MGnifystudy.py
# ------------------------------------------------------------------------------------------------------
import os
import requests
import json

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


# Putting it all together
def process_study_results(
        summary_results_study: requests.Response.json,
        download_folder: str,
        study_accession: str
    ):

    # Create a folder for the study
    study_directory = os.path.join(download_folder, study_accession)
    try:
        os.makedirs(study_directory, exist_ok=True)
        print(f"Study directory created: {study_directory}")
    except Exception as e:
        print(f"Error creating study directory: {e}")

    # Export the result of the original request to a JSON file and save it in the study directory
    request_file_path = os.path.join(
        study_directory, 
        f"{study_accession}_results_info.json"
    )
    with open(request_file_path, "w") as outfile:
        json.dump(summary_results_study, outfile)    

    # Iterate through the results and download the desired file type
    print("Processing results for the MGnify study:")
    for result in summary_results_study["data"]:
        # Set the variables for the result to download
        alias = result["attributes"]["alias"]
        # label = result["attributes"]["description"]["label"]
        # file_format = result["attributes"]["file-format"]["name"]
        download_link = result["links"]["self"]

        # Define the file name and download it
        file_name = f"{study_accession}_{alias}"
        download_and_save_MGnifystudy_results(download_link, file_name, study_directory)
    
