# Date: 09-12-2023
# Description: This script is an example of how to use the functions from the Functions_get_samplesMetadata_from_MGnifystudy.py script.
# Version: 1.0
# License: MIT License
# Usage: python example_main_get_samplesMetadata_from_MGnifystudy.py
# Warning: The external script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/Multiomics-Analytics-Group/Retrieve_info_MGnifyAPI/blob/main/Scripts/example_main_get_samplesMetadata_from_MGnifystudy.py
# ------------------------------------------------------------------------------------------------------------------------------------
# Import external functions
import pandas as pd
import json
from Functions_get_samplesMetadata_from_MGnifystudy import get_samples_metadata_from_MGnifystudy

# Set the study accession for the MGnify study
study_accession = "MGYS00001392"

# Retrieve the results info for the MGnify study
samples_metadata = get_samples_metadata_from_MGnifystudy(study_accession)

# Export the result of the request to a JSON file
with open(f"../Output/{study_accession}_samples_metadata.json", "w") as outfile:
    json.dump(samples_metadata, outfile)

# Convert json to pandas dataframe
samples_metadata_df = pd.json_normalize(samples_metadata["data"])

# Select the columns of interest
columns = ["id", "attributes.sample-name", "attributes.latitude", "attributes.longitude", 
           "attributes.geo-loc-name", "attributes.environment-biome", "attributes.environment-feature",
           "attributes.environment-material"]
samples_metadata_df = samples_metadata_df[columns]

# Rename columns
samples_metadata_df = samples_metadata_df.rename(columns={"attributes.sample-name": "sample_name",
                                    "attributes.latitude": "latitude",
                                    "attributes.longitude":"longitude",
                                    "attributes.geo-loc-name":"geolocation",
                                    "attributes.environment-biome":"biome",
                                    "attributes.environment-feature":"biome_feature",
                                    "attributes.environment-material":"biome_material"})
# Export the dataframe to a CSV file
samples_metadata_df.to_csv(f"../Output/{study_accession}_samples_metadata.csv", index=False)
