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
    params = {}

    print(f"Making GET request to: {endpoint}")
    response = requests.get(endpoint, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the total number of items in the request and 
        # the total number of pages
        page_info = response.json()["meta"]["pagination"]
        total_count = page_info["count"]
        total_pages = page_info["pages"]
        print(f"Total studies to retrieve: {total_count}")
        print(f"Total pages: {total_pages}")

        all_samples = []
        page = 1

        # Iterate through all pages and append the data to the list
        while page <= total_pages:
            print(f"Retrieving data for page {page}/{total_pages}")

            params["page"] = page
            response = requests.get(endpoint, params=params)

            if response.status_code == 200:
                data = response.json()["data"]
                all_samples.extend(data)
                page += 1
            else:
                print(f"Failed to retrieve data for page {page}. Status code: {response.status_code}")
                break

        print("GET request successful. Data retrieval complete.")
        return all_samples
    else:
        print(f"Failed to retrieve page info. Status code: {response.status_code}")
        return []  # Return an empty list if the request was not successful