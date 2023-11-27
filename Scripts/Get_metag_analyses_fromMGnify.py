# ------------------------------------------------------------------------------------------------------
# Script: Get_metag_analyses_fromMGnify.py
# Author: Sebastian Ayala Ruano
# Date: 27-11-2023
# Description: This script retrieves the list of metagenomic analyses from MGnify for a given biome and 
# data type (amplicon, metagenomic, metatranscriptomic, or assembly). The attributes retrived for the studies can be 
# modified in the script. The list of analyses and studies (including analyses information) are saved as CSV files.
# The Get_metag_studies_fromMGnify.py script must be run first to obtain the list of studies for the biome.
# Version: 2.0
# License: MIT License
# Usage: python Get_metag_analyses_fromMGnify.py
# References: https://github.com/sayalaruano/Retrieve_info_MGnifyAPI/blob/main/Scripts/Get_metag_analyses_fromMGnify.py
# ------------------------------------------------------------------------------------------------------
#%%
import requests
import pandas as pd

# Define function to interact with the MGnify API
def fetch_all_analyses(url, params):
    '''Function to retrieve all MGnify analyses for a given biome from a GET request
    Input: url (str) - URL for the GET request
           params (dict) - query parameters for the GET request, e.g. biome_name, experiment_type, etc.
    Output: all_analyses_data (list) - list of dictionaries with the data from all analyses'''
    
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

        all_analyses_data = []
        page = 1

        # Iterate through all pages and append the data to the list
        while page <= total_pages:
            print(f"Retrieving data for page {page}/{total_pages}")

            params["page"] = page
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()["data"]
                all_analyses_data.extend(data)
                page += 1
            else:
                print(f"Failed to retrieve data for page {page}. Status code: {response.status_code}")
                break

        print("Data retrieval complete.")
        return all_analyses_data
    else:
        print(f"Failed to retrieve page info. Status code: {response.status_code}")
        return []  # Return an empty list if the request was not successful

#%%
# Set the URL for the GET request to retrieve all analyses
url = "https://www.ebi.ac.uk/metagenomics/api/v1/analyses"

# Set the query parameters for the GET request
params = {
    "biome_name": "root:Engineered:Wastewater", # Replace with the biome name of interest
    "lineage": "root:Engineered:Wastewater",    
    "experiment_type": "assembly,metagenomic,metatranscriptomic", # Replace with the data type of interest
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
all_analysis_data = fetch_all_analyses(url, params)
print("Request complete.")
# %%
# Extract a list of accessions from the list of analysis data to verify that all analyses were retrieved
analyses_id_list = [analysis["attributes"]["accession"] for analysis in all_analysis_data]

# Extract a list of study IDs from the list of analysis data to verify that all studies were retrieved
study_id_list = list(set([analysis["relationships"]["study"]["data"]["id"] if "study" in analysis["relationships"] else "" for analysis in all_analysis_data]))

# Extract a list of sample IDs from the list of analysis data to verify that all samples were retrieved
sample_id_list = list(set([analysis["relationships"]["sample"]["data"]["id"] if "sample" in analysis["relationships"] else "" for analysis in all_analysis_data]))
#%%
# Create a list of dictionaries with the desired columns
data_list = []
for analysis in all_analysis_data:
    analysis_id = analysis["attributes"]["accession"]
    experiment_type = analysis["attributes"]["experiment-type"]
    pipeline_version = analysis["attributes"]["pipeline-version"]
    instrument_platform = analysis["attributes"]["instrument-model"]
    study_id = analysis["relationships"]["study"]["data"]["id"] if "study" in analysis["relationships"] else ""
    sample_id = analysis["relationships"]["sample"]["data"]["id"] if "sample" in analysis["relationships"] else ""
    
    data_list.append({
        "analysis_id": analysis_id,
        "sample_id": sample_id,
        "experiment_type": experiment_type,
        "pipeline_version": pipeline_version,
        "study_id": study_id,
        "instrument_platform": instrument_platform
    })

# Create a Pandas DataFrame from the list of dictionaries
df_analyses_wwt_mgnify = pd.DataFrame(data_list)
#%%
# Import file with attributes from the wwt studies, obtained with the script Get_metag_studies_fromMGnify.py
study_data_df = pd.read_csv("../Results/Mgnify_studies_wwt.csv")

# Join the two DataFrames using the index
df_analyses_wwt_mgnify_def = df_analyses_wwt_mgnify.merge(study_data_df, on="study_id", how="left")

# Rearrange the columns
df_analyses_wwt_mgnify_def = df_analyses_wwt_mgnify_def[['analysis_id', 'sample_id', 'experiment_type', 'pipeline_version', 'instrument_platform', 
                                                         'study_id', 'bioproject', 'study_name', 'n_samples', 'centre_name', 'biomes']]
#%%
# Create a dataframe with the unique study IDs
study_ids = pd.DataFrame(df_analyses_wwt_mgnify_def["study_id"].unique(), columns=['study_id'])

# Remove NaN values
study_ids = study_ids.dropna()

# Create an empty DataFrame to store the extracted information
studies_wwt_shot_metag_assembly = pd.DataFrame(columns=['study_id', 'study_name', 'bioproject', 'n_samples', 'biomes', 'experiment_type', 'pipeline_version'])

# Iterate over the rows in df_unique_ids
for _, row in study_ids.iterrows():
    study_id = row['study_id']

    # Retrieve information for the current unique ID from the first row of df_original
    info = df_analyses_wwt_mgnify_def[df_analyses_wwt_mgnify_def['study_id'] == study_id].iloc[0][['study_name', 'bioproject', 'n_samples', 'biomes', 'experiment_type', 'pipeline_version']]

    # Create a new DataFrame with the study_id and extracted information
    study_data = pd.DataFrame({'study_id': [study_id], **info.to_dict()}, index=[0])

    # Concatenate the new DataFrame with studies_wwt_shot_metag_assembly
    studies_wwt_shot_metag_assembly = pd.concat([studies_wwt_shot_metag_assembly, study_data], ignore_index=True)

# %%
# Export the DataFrames to a CSV file
df_analyses_wwt_mgnify_def.to_csv("../Results/Mgnify_analyses_wwt_shot_metag_assembly.csv", index=False)
studies_wwt_shot_metag_assembly.to_csv("../Results/Mgnify_studies_wwt_shot_metag_assembly.csv", index=False)

print("Data export complete. CSV files saved in the 'Results' folder.")
