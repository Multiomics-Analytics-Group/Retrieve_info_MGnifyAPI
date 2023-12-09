# ------------------------------------------------------------------------------------------------------------------------------------
# Script: example_main_get_results_from_MGnifystudy.py
# Author: Sebastian Ayala Ruano
# Date: 09-12-2023
# Description: This script is an example of how to use the functions from the Functions_get_results_from_MGnifystudy.py script.
# It downloads all results available for a MGnify study. 
# Check the https://www.ebi.ac.uk/metagenomics/api/v1/studies/study_accession/downloads endpoint for the available file types.
# Version: 1.0
# License: MIT License
# Usage: python example_main_get_results_from_MGnifystudy.py
# Warning: The external script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/Multiomics-Analytics-Group/Retrieve_info_MGnifyAPI/blob/main/Scripts/example_main_get_results_from_MGnifystudy.py
# ------------------------------------------------------------------------------------------------------------------------------------
# Import external functions
import os
import json
from Functions_get_results_from_MGnifystudy import get_results_info_from_MGnifystudy, download_and_save_MGnifystudy_results

# Set the study accession for the MGnify study
study_accession = "MGYS00001392"

# Change this variable to your desired folder path
download_folder = "../Output/Unified_analyses" 

# Retrieve the results info for the MGnify study
summary_results_study = get_results_info_from_MGnifystudy(study_accession)

if summary_results_study:
    # Create a folder for the study
    study_directory = os.path.join(download_folder, study_accession)
    try:
        os.makedirs(study_directory, exist_ok=True)
        print(f"Study directory created: {study_directory}")
    except Exception as e:
        print(f"Error creating study directory: {e}")

    # Iterate through the results and download the desired file type
    print("Processing results for the MGnify study:")
    for result in summary_results_study["data"]:
        # Set the variables for the result to download
        alias = result["attributes"]["alias"]
        label = result["attributes"]["description"]["label"]
        file_format = result["attributes"]["file-format"]["name"]
        download_link = result["links"]["self"]

        # Define the file name and download it
        file_name = f"{study_accession}_{alias}"
        download_and_save_MGnifystudy_results(download_link, file_name, study_directory)
    
    # Export the result of the original request to a JSON file and save it in the study directory
    request_file_name = f"{study_accession}_results_info.json"
    request_file_path = os.path.join(study_directory, request_file_name)
    with open(request_file_path, "w") as outfile:
        json.dump(summary_results_study, outfile)
else:
    print("Failed to retrieve results for the MGnify study.")