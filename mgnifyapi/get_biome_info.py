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
# References: https://github.com/Multiomics-Analytics-Group/Retrieve_info_MGnifyAPI/blob/main/Scripts/Functions_getInfo_MGnify_studies_analyses.py
# ------------------------------------------------------------------------------------------------------
# %%
# Import libraries
import requests
import pandas as pd
import json
import os
import time


# Define functions to interact with the MGnify API
def request_info(
        url:str, 
        params:dict,
        outfile:str|None=None,
        wait_time:int=1
    ):
    """Function to retrieve information for all MGnify studies or analyses for a given biome from a GET request
    Input: url (str) - URL for the GET request, e.g. https://www.ebi.ac.uk/metagenomics/api/v1/analyses
           params (dict) - query parameters for the GET request, e.g. biome_name
    Output: all_studies_or_analyses (list) - list of json files with the data from all studies or analyses"""

    print("Starting get request for data retrieval...")
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the total number of items in the request and
        # the total number of pages
        page_info = response.json()["meta"]["pagination"]
        total_count = page_info["count"]
        total_pages = page_info["pages"]
        print(f"Total studies or analyses to retrieve: {total_count}")
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

                # iteratively save if an output file is provided
                if outfile:
                    with open(outfile, "w") as f:
                        json.dump(all_studies_or_analyses, f)

                # add waiting time to avoid overloading the server
                time.sleep(wait_time)

            else:
                print(
                    f"Failed to retrieve data for page {page}. Status code: {response.status_code}. {response.url}"
                )
                break

        print("Data retrieval complete.")
        return all_studies_or_analyses
    else:
        print(f"Failed to retrieve page info. Status code: {response.status_code}. {response.url}")
        return []  # Return an empty list if the request was not successful


def get_studies_info(
    biome_name: str,
    outpath: str,
    url:str = "https://www.ebi.ac.uk/metagenomics/api/v1/studies",
    study_file:str="mgnify_studies.json",
) -> pd.DataFrame:
    """
    Retrieve information for all MGnify studies for a given biome.
    This function retrieves studies data from the MGnify API based on the specified biome.
    It processes the data to create a Pandas DataFrame summarizing the studies information.
    The results are also exported to a JSON file.
    Parameters:
    biome_name (str): The name of the biome of interest, e.g., "root:Engineered:Wastewater".
    outpath (str): The path to the output folder where the JSON data will be saved.
    Returns:
    pd.DataFrame: DataFrame with the summary of studies information.
    The DataFrame contains the following columns:
    - study_id: The ID of the study.
    - study_name: The name of the study.
    - n_samples: The number of samples in the study.
    - bioproject: The bioproject associated with the study.
    - centre_name: The name of the centre conducting the study.
    - biomes: The biomes associated with the study.
    """

    # Set the query parameters for the GET request
    params = {"biome_name": biome_name}

    # Retrieve all studies
    all_studies_data = request_info(
        url, 
        params,
        os.path.join(outpath, study_file)
    )
    print("Studies request complete.")

    # Export the result of the request to a JSON file
    # with open(os.path.join(outpath, "Mgnify_studies.json"), "w") as outfile:
    #     json.dump(all_studies_data, outfile)
    return all_studies_data


def studies_json_to_df(
    outpath:str,
    study_file:str="mgnify_studies.json",
) -> pd.DataFrame:

    json_file = os.path.join(outpath, study_file)
    # load json file
    with open(json_file, 'r') as file:
        all_studies_data = json.load(file)

    # Extract the desired attributes and create a DataFrame
    study_list = []
    for study in all_studies_data:
        attributes = study["attributes"]
        study_list.append(
            {
                "study_id": study["id"],
                "study_name": attributes.get("study-name"),
                "n_samples": attributes.get("samples-count"),
                "bioproject": attributes.get("bioproject"),
                "centre_name": attributes.get("centre-name"),
                "biomes": ", ".join(
                    [biome["id"] for biome in study["relationships"]["biomes"]["data"]]
                ),
            }
        )

    # Create a DataFrame from the list of dictionaries
    df_studies_mgnify = pd.DataFrame(study_list)

    return df_studies_mgnify


def get_analyses_info(
    biome_name: str,
    experiment_types: str | list,
    outpath: str,
    url = "https://www.ebi.ac.uk/metagenomics/api/v1/analyses",
    analyses_file:str="mgnify_analyses.json",
) -> pd.DataFrame:
    """
    Retrieve information for all MGnify analyses for a given biome and experiment types.
    This function retrieves analyses data from the MGnify API based on the specified biome and experiment types.
    It processes the data to create a Pandas DataFrame summarizing the analyses information.
    The results are also exported to a JSON file.
    Parameters:
    biome_name (str): The name of the biome of interest, e.g., "root:Engineered:Wastewater".
    experiment_types (str | list): The data type(s) of interest, e.g., "assembly, metagenomic, metatranscriptomic".
    outpath (str): The path to the output folder where the JSON data will be saved.
    Returns:
    pd.DataFrame: DataFrame with the summary of analyses information.
    The DataFrame contains the following columns:
    - analysis_id: The ID of the analysis.
    - sample_id: The ID of the sample.
    - assembly_run_id: The ID of the assembly run.
    - experiment_type: The type of experiment.
    - pipeline_version: The version of the pipeline used.
    - study_id: The ID of the study.
    - instrument_platform: The platform used for the instrument.
    """

    # Set the query parameters for the GET request
    params = {
        "biome_name": biome_name,  # Replace with the biome name of interest
        "lineage": biome_name,
        "experiment_type": experiment_types,  # Replace with the data type of interest
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
        "include": "downloads",
    }
    # Retrieve all analyses
    all_analysis_data = request_info(
        url, 
        params,
        os.path.join(outpath, analyses_file)
    )
    print("Analyses request complete.")

    # Export the result of the request to a JSON file
    # with open(os.path.join(outpath, "Mgnify_analyses.json"), "w") as outfile:
    #     json.dump(all_analysis_data, outfile)


def analyses_json_to_df(
    outpath:str, 
    analyses_file:str="mgnify_analyses.json",
) -> pd.DataFrame:

    json_file = os.path.join(outpath, analyses_file)
    # load json file
    with open(json_file, 'r') as file:
        all_analysis_data = json.load(file)
        
    # Create a list of dictionaries with the desired columns
    analysis_list = []
    for analysis in all_analysis_data:
        analysis_id = analysis["attributes"]["accession"]
        experiment_type = analysis["attributes"]["experiment-type"]
        pipeline_version = analysis["attributes"]["pipeline-version"]
        instrument_platform = analysis["attributes"]["instrument-model"]
        study_id = (
            analysis["relationships"]["study"]["data"]["id"]
            if "study" in analysis["relationships"]
            else ""
        )
        sample_id = (
            analysis["relationships"]["sample"]["data"]["id"]
            if "sample" in analysis["relationships"]
            else ""
        )

        if experiment_type == "assembly":
            assembly_run_id = analysis["relationships"]["assembly"]["data"]["id"]
        elif experiment_type == "metagenomic":
            assembly_run_id = analysis["relationships"]["run"]["data"]["id"]
        elif experiment_type == "metatranscriptomic":
            assembly_run_id = analysis["relationships"]["run"]["data"]["id"]

        analysis_list.append(
            {
                "analysis_id": analysis_id,
                "sample_id": sample_id,
                "assembly_run_id": assembly_run_id,
                "experiment_type": experiment_type,
                "pipeline_version": pipeline_version,
                "study_id": study_id,
                "instrument_platform": instrument_platform,
            }
        )

    # Create a Pandas DataFrame from the list of dictionaries
    df_analyses_mgnify = pd.DataFrame(analysis_list)

    return df_analyses_mgnify


def join_studies_and_analyses_dfs(
    df_studies_mgnify: pd.DataFrame,
    df_analyses_mgnify: pd.DataFrame,
    outpath:str,
    final_studies_file:str="df_studies.csv",
    final_analyses_file:str="df_analyses.csv",
)->pd.DataFrame:
    """
    Generate a summary of MGnify studies and analyses.
    This function takes two DataFrames containing studies and analyses information,
    merges them, and creates a summary DataFrame for both studies and analyses.
    Parameters:
    df_studies_mgnify (pd.DataFrame): DataFrame containing studies information.
    df_analyses_mgnify (pd.DataFrame): DataFrame containing analyses information.
    Returns:
    tuple: A tuple containing two DataFrames:
        - df_analyses_mgnify_def (pd.DataFrame): Merged DataFrame with analyses and studies information.
        - df_studies_mgnify (pd.DataFrame): DataFrame with unique study information.
    """
    # Join the two DataFrames on study_id column
    # on left to filter out studies without analyses
    df_combo = df_analyses_mgnify.merge(
        df_studies_mgnify, on="study_id", how="left"
    ).dropna(subset=['study_id'])

    # Rearrange the columns
    df_combo = df_combo[
        [
            "analysis_id",
            "sample_id",
            "assembly_run_id",
            "experiment_type",
            "pipeline_version",
            "instrument_platform",
            "study_id",
            "bioproject",
            "study_name",
            "n_samples",
            "centre_name",
            "biomes",
        ]
    ]

    # now only unique study info 
    df_s_info = df_combo[[
        "study_id",
        "study_name",
        "bioproject",
        "centre_name",
        "n_samples",
        "biomes",
        "experiment_type",
        "pipeline_version",
    ]].copy()

    df_s_info = df_s_info.drop_duplicates()

    # Export dfs to csvs
    df_combo.to_csv(os.path.join(outpath, final_analyses_file), index=False)
    df_s_info.to_csv(os.path.join(outpath, final_studies_file), index=False)

    return df_combo, df_s_info

