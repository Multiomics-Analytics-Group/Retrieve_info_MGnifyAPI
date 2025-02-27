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
from mgnifyapi.utils import create_folder


def get_study_result_info(
    study_accession: str,
    download_folder: str,
    base_url: str = "https://www.ebi.ac.uk/metagenomics/api/v1/studies",
):
    """
    :param study_accession: MGnify study accession for the GET request, e.g., "MGYS00001392".
    :type study_accession: str
    :param download_folder: Path to the folder where the results will be downloaded.
    :type download_folder: str
    :param base_url: Base URL for the MGnify API. Defaults to "https://www.ebi.ac.uk/metagenomics/api/v1/studies".
    :type base_url: str, optional

    :return: JSON response containing the information of the results for the MGnify study if the request is successful, None if the request fails.
    :rtype: dict or None

    :raises ValueError: If `study_accession` or `base_url` is not a string.
    """

    ## PRECONDITIONS
    if not isinstance(study_accession, str):
        raise ValueError("study_accession should be a string.")
    if not isinstance(base_url, str):
        raise ValueError("base_url should be a string.")
    # create download folders if it doesn't already exist
    create_folder(download_folder)
    study_directory = os.path.join(download_folder, study_accession)
    create_folder(study_directory)

    ## MAIN FUNCTIONALITY
    # Prep
    # Combine url and accession
    endpoint = f"{base_url}/{study_accession}/downloads"
    # filepath for saving the info
    request_file_path = os.path.join(
        study_directory, f"{study_accession}_results_info.json"
    )

    # Make the GET request
    print(f"Making GET request to: {endpoint}")
    response = requests.get(endpoint)

    # Check if the request was successful
    if response.status_code == 200:
        print("GET request successful.")
        # Retrieve the results of the request
        results_MGnify_study = response.json()
        # save to a JSON file in the study directory
        with open(request_file_path, "w") as outfile:
            json.dump(results_MGnify_study, outfile)
        print(f"Result info for '{study_accession}' downloaded to {request_file_path}")
        # Return the results
        return results_MGnify_study
    else:
        print(f"Error: {response.status_code} from {endpoint}")
        return None


def download_study_results(url: str, file_name: str, download_folder: str):
    """
    Function to download and save results for a given MGnify study.

    :param url: URL for the GET request.
    :type url: str
    :param file_name: Results file name, e.g., taxonomic assignments.
    :type file_name: str
    :param download_folder: Path for the download folder.
    :type download_folder: str

    :raises ValueError: If `url` or `file_name` is not a string.

    :return: None. This function does not return a value, but downloads and saves the desired results for the MGnify study.
    :rtype: None
    """

    ## PRECONDITIONS
    if not isinstance(url, str):
        raise ValueError("url should be a string.")
    if not isinstance(file_name, str):
        raise ValueError("file_name should be a string.")
    # create download folder if it doesn't already exist
    create_folder(download_folder)

    ## MAIN FUNCTIONALITY
    # Define the file path
    file_path = os.path.join(download_folder, file_name)
    # Make the GET request
    response = requests.get(url)
    if response.status_code == 200:
        # Save the respones
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File '{file_name}' downloaded and saved in '{download_folder}'.")
    else:
        print(
            f"Failed to download file from {url}. Status code: {response.status_code}"
        )


# Putting it all together
def process_study_results(
    study_accession: str,
    download_folder: str,
    base_url: str = "https://www.ebi.ac.uk/metagenomics/api/v1/studies",
):
    """
    Processes the results of a given MGnify study by downloading the relevant files.
    This function takes a study accession, a download folder, and an optional base URL to fetch the study results.
    It creates the necessary directories, retrieves the study results, and downloads the files associated with the study.
    :param study_accession: The accession number of the study to process.
    :type study_accession: str
    :param download_folder: The path to the folder where the study results will be downloaded.
    :type download_folder: str
    :param base_url: The base URL for the MGnify API (default is "https://www.ebi.ac.uk/metagenomics/api/v1/studies").
    :type base_url: str
    :raises ValueError: If `study_accession` or `base_url` are not strings.
    """
    ## PRECONDITIONS
    if not isinstance(study_accession, str):
        raise ValueError("study_accession should be a string.")
    if not isinstance(base_url, str):
        raise ValueError("base_url should be a string.")
    # create download folders if it doesn't already exist
    create_folder(download_folder)
    study_directory = os.path.join(download_folder, study_accession)
    create_folder(study_directory)

    ## MAIN FUNCTIONALITY
    # Get the study results info
    summary_results_study = get_study_result_info(
        study_accession, download_folder, base_url
    )

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
        download_study_results(download_link, file_name, study_directory)
