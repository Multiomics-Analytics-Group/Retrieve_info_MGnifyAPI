# ------------------------------------------------------------------------------------------------------------------------------------
# Script: example_main_get_results_from_MGnifystudy.py
# Author: Sebastian Ayala Ruano
# Date: 09-12-2023
# Description: This script is an example of how to use the functions from the Functions_get_results_from_MGnifystudy.py script.
# Version: 1.0
# License: MIT License
# Usage: python example_main_get_results_from_MGnifystudy.py
# Warning: The external script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/sayalaruano/Retrieve_info_MGnifyAPI/blob/main/Scripts/example_main_get_results_from_MGnifystudy.py
# ------------------------------------------------------------------------------------------------------------------------------------
# Import external functions
import os
from Functions_get_results_from_MGnifystudy import get_results_info_from_MGnifystudy, download_and_save_MGnifystudy_results

study_accession = "MGYS00001392"
desired_file_type = "Taxonomic assignments"  # Change this to your desired file type, check ....
download_folder = "../Output/Unified_analyses"  # Change this to your desired folder path
summary_analyses_data = get_results_info_from_MGnifystudy(study_accession)

if summary_analyses_data:
    print("Processing results for the MGnify study:")
    
    study_directory = os.path.join(download_folder, study_accession)
    try:
        os.makedirs(study_directory, exist_ok=True)
        print(f"Study directory created: {study_directory}")
    except Exception as e:
        print(f"Error creating study directory: {e}")

    for analysis in summary_analyses_data["data"]:
        alias = analysis["attributes"]["alias"]
        label = analysis["attributes"]["description"]["label"]
        file_format = analysis["attributes"]["file-format"]["name"]
        download_link = analysis["links"]["self"]

        # Check if the label contains the desired file type
        if desired_file_type.lower() in label.lower():
            file_name = f"{study_accession}_{alias}"
            download_and_save_MGnifystudy_results(download_link, file_name, study_directory)
else:
    print("Failed to retrieve results for the MGnify study.")