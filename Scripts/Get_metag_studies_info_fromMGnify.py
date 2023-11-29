# ------------------------------------------------------------------------------------------------------
# Script: Get_metag_studies_info_fromMGnify.py
# Author: Sebastian Ayala Ruano
# Date: 25-11-2023
# Description: This script retrieves the list of metagenomic studies from MGnify for a given biome. 
# The attributes retrived for the studies can be modified in the script. 
# The list of studies is saved as a CSV file.
# Version: 2.0
# License: MIT License
# Usage: python Get_metag_studies_info_fromMGnify.py
# References: https://github.com/sayalaruano/Retrieve_info_MGnifyAPI/blob/main/Scripts/Get_metag_studies_info_fromMGnify.py
# ------------------------------------------------------------------------------------------------------
#%%
# Import libraries
import requests
import pandas as pd
import json

# Define function to interact with the MGnify API
def fetch_all_studies(url, params):
    '''Function to retrieve all MGnify studies for a given biome from a GET request
    Input: url (str) - URL for the GET request
           params (dict) - query parameters for the GET request, e.g. biome_name
    Output: all_studies_data (list) - list of dictionaries with the data from all studies'''
    
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

        all_studies_data = []
        page = 1

        # Iterate through all pages and append the data to the list
        while page <= total_pages:
            print(f"Retrieving data for page {page}/{total_pages}")

            params["page"] = page
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()["data"]
                all_studies_data.extend(data)
                page += 1
            else:
                print(f"Failed to retrieve data for page {page}. Status code: {response.status_code}")
                break

        print("Data retrieval complete.")
        return all_studies_data
    else:
        print(f"Failed to retrieve page info. Status code: {response.status_code}")
        return []  # Return an empty list if the request was not successful
#%%
# Set the URL for the GET request to retrieve all studies
url = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"

# Set the query parameters for the GET request
params = {
    'biome_name': 'root:Engineered:Wastewater',  # Replace with the biome name of interest
}

# Retrieve all studies
all_studies_data = fetch_all_studies(url, params)
print("Request complete.")

# Export the result of the request to a JSON file
with open("../Output/Mgnify_studies_wwt.json", "w") as outfile:
    json.dump(all_studies_data, outfile)
#%%
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
df_studies_wwt_mgnify = pd.DataFrame(study_list)
#%%
# Export the DataFrame to a CSV file
df_studies_wwt_mgnify.to_csv('../Output/Mgnify_studies_wwt.csv', index=False)

print("Data export complete. CSV file saved in the 'Output' folder.")