# ------------------------------------------------------------------------------------------------------
# Script: Functions_getInfo_MGnify_studies_analyses.py
# Author: Sebastian Ayala Ruano
# Date: 09-12-2023
# Description: This script retrieves a summary of MGnify studies and analyses for a given biome and 
# data type (amplicon, shotgun metagenomics, metatranscriptomic, or assembly). The attributes of the api requests can be 
# modified in the script. The fetch_studies_or_analyses_info returns a list of json files with information from all studies 
# or analyses for a given biome and data type. The get_studies_and_analyses_summary returns two dataframes, one with the
# summary of analyses info and another with the summary of studies info. 
# Version: 1.0
# License: MIT License
# Usage: call the functions from external scripts. See example_main.py
# Warning: The script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/sayalaruano/Retrieve_info_MGnifyAPI/blob/main/Scripts/Functions_getInfo_MGnify_studies_analyses.py
# ------------------------------------------------------------------------------------------------------
#%%
# Import libraries
import requests
import pandas as pd
import json

# Define functions to interact with the MGnify API
def fetch_studies_or_analyses_info(url, params):
    '''Function to retrieve information for all MGnify studies or analyses for a given biome from a GET request
    Input: url (str) - URL for the GET request, e.g. https://www.ebi.ac.uk/metagenomics/api/v1/analyses
           params (dict) - query parameters for the GET request, e.g. biome_name
    Output: all_studies_or_analyses (list) - list of json files with the data from all studies or analyses'''
    
    print("Starting get request for data retrieval...")
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the total number of items in the request and 
        # the total number of pages
        page_info = response.json()["meta"]["pagination"]
        total_count = page_info["count"]
        total_pages = page_info["pages"]
        print(f"Total studies to retrieve: {total_count}")
        print(f"Total pages: {total_pages}")

        all_studies_or_analyses = []
        page = 1

        # Iterate through all pages and append the data to the list
        while page <= total_pages:
            print(f"Retrieving data for page {page}/{total_pages}")

            params["page"] = page
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()["data"]
                all_studies_or_analyses.extend(data)
                page += 1
            else:
                print(f"Failed to retrieve data for page {page}. Status code: {response.status_code}")
                break

        print("Data retrieval complete.")
        return all_studies_or_analyses
    else:
        print(f"Failed to retrieve page info. Status code: {response.status_code}")
        return []  # Return an empty list if the request was not successful
    
def get_studies_and_analyses_summary(biome_name, experiment_type):
    '''Function to obtain a summary of MGnify studies and analyses info for a given biome and data type
    Input: biome_name (str) - name of the biome of interest, e.g. "root:Engineered:Wastewater"
           experiment_type (str) - data type of interest, e.g. "assembly, metagenomic, metatranscriptomic"
    Output: df_analyses_mgnify_def (DataFrame) - DataFrame with the summary of analyses info
            df_studies_mgnify (DataFrame) - DataFrame with the summary of studies info'''    
    
    # Set the URL for the GET request to retrieve all studies
    url = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"

    # Set the query parameters for the GET request
    params = {'biome_name': biome_name}

    # Retrieve all studies
    all_studies_data = fetch_studies_or_analyses_info(url, params)
    print("Studies request complete.")

    # Export the result of the request to a JSON file
    with open("../Output/Mgnify_studies.json", "w") as outfile:
        json.dump(all_studies_data, outfile)

    # Extract the desired attributes and create a DataFrame
    study_list = []
    for study in all_studies_data:
        attributes = study["attributes"]
        study_list.append({
            "study_id": study["id"],
            "study_name": attributes.get("study-name"),
            "n_samples": attributes.get("samples-count"),
            "bioproject": attributes.get("bioproject"),
            "centre_name": attributes.get("centre-name"),
            "biomes": ", ".join([biome["id"] for biome in study["relationships"]["biomes"]["data"]]),
        })

    # Create a DataFrame from the list of dictionaries
    df_studies_mgnify = pd.DataFrame(study_list)

        # Set the URL for the GET request to retrieve all analyses
    url = "https://www.ebi.ac.uk/metagenomics/api/v1/analyses"

    # Set the query parameters for the GET request
    params = {
        "biome_name": biome_name, # Replace with the biome name of interest
        "lineage": biome_name,    
        "experiment_type": experiment_type, # Replace with the data type of interest
        "species": "",
        "sample_accession": "",
        "pipeline_version": "",
        "accession": "",
        "instrument_platform": "",
        "instrument_model": "",
        "metadata_key": "",
        "metadata_value_gte": "",
        "metadata_value_lte": "",
        "metadata_value": "",
        "study_accession": "",
        "include": "downloads"
    }
    # Retrieve all analyses
    all_analysis_data = fetch_studies_or_analyses_info(url, params)
    print("Analyses request complete.")

    # Export the result of the request to a JSON file
    with open("../Output/Mgnify_analyses.json", "w") as outfile:
        json.dump(all_analysis_data, outfile)

    # Create a list of dictionaries with the desired columns
    analysis_list = []
    for analysis in all_analysis_data:
        analysis_id = analysis["attributes"]["accession"]
        experiment_type = analysis["attributes"]["experiment-type"]
        pipeline_version = analysis["attributes"]["pipeline-version"]
        instrument_platform = analysis["attributes"]["instrument-model"]
        study_id = analysis["relationships"]["study"]["data"]["id"] if "study" in analysis["relationships"] else ""
        sample_id = analysis["relationships"]["sample"]["data"]["id"] if "sample" in analysis["relationships"] else ""
        
        analysis_list.append({
            "analysis_id": analysis_id,
            "sample_id": sample_id,
            "experiment_type": experiment_type,
            "pipeline_version": pipeline_version,
            "study_id": study_id,
            "instrument_platform": instrument_platform
        })

    # Create a Pandas DataFrame from the list of dictionaries
    df_analyses_mgnify = pd.DataFrame(analysis_list)

    # Join the two DataFrames using the index
    df_analyses_mgnify_def = df_analyses_mgnify.merge(df_studies_mgnify, on="study_id", how="left")

    # Rearrange the columns
    df_analyses_mgnify_def = df_analyses_mgnify_def[['analysis_id', 'sample_id', 'experiment_type', 'pipeline_version', 'instrument_platform', 
                                                            'study_id', 'bioproject', 'study_name', 'n_samples', 'centre_name', 'biomes']]

    # Create a dataframe with the unique study IDs
    study_ids = pd.DataFrame(df_analyses_mgnify_def["study_id"].unique(), columns=['study_id'])

    # Remove NaN values
    study_ids = study_ids.dropna()

    # Create an empty DataFrame to store the extracted information
    df_studies_mgnify = pd.DataFrame(columns=['study_id', 'study_name', 'bioproject', 'centre_name', 'n_samples', 'biomes', 'experiment_type', 'pipeline_version'])

    # Iterate over the rows in df_unique_ids
    for _, row in study_ids.iterrows():
        study_id = row['study_id']

        # Retrieve information for the current unique ID from the first row of df_original
        info = df_analyses_mgnify_def[df_analyses_mgnify_def['study_id'] == study_id].iloc[0][['study_name', 'bioproject', 'centre_name', 'n_samples', 'biomes', 'experiment_type', 'pipeline_version']]

        # Create a new DataFrame with the study_id and extracted information
        study_data = pd.DataFrame({'study_id': [study_id], **info.to_dict()}, index=[0])

        # Concatenate the new DataFrame with df_studies_mgnify
        df_studies_mgnify = pd.concat([df_studies_mgnify, study_data], ignore_index=True)

    return (df_analyses_mgnify_def, df_studies_mgnify)
