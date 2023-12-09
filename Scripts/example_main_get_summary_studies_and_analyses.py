# ------------------------------------------------------------------------------------------------------------------------------------
# Script: example_main_get_summary_studies_and_analyses.py
# Author: Sebastian Ayala Ruano
# Date: 09-12-2023
# Description: This script is an example of how to use the functions from the Functions_getInfo_MGnify_studies_analyses.py script.
# Version: 1.0
# License: MIT License
# Usage: python example_main_get_summary_studies_and_analyses.py
# Warning: The external script relies on the MGnify API, which could have high traffic. If the script fails, try again later.
# References: https://github.com/sayalaruano/Retrieve_info_MGnifyAPI/blob/main/Scripts/example_main_get_summary_studies_and_analyses.py
# ------------------------------------------------------------------------------------------------------------------------------------
# Import external function
from Functions_getInfo_MGnify_studies_analyses import get_studies_and_analyses_summary

# Define parameters for the MGnify API request
biome_name = 'root:Engineered:Wastewater'
experiment_type = "assembly,metagenomic,metatranscriptomic"

# Call the function with the desired biome name and styudy types
df_analyses_wwt_mgnify_def, studies_wwt_shot_metag_assembly = get_studies_and_analyses_summary(biome_name, experiment_type)

# Export the DataFrames to a CSV file
df_analyses_wwt_mgnify_def.to_csv("../Output/Mgnify_analyses_wwt_shot_metag_assembly.csv", index=False)
studies_wwt_shot_metag_assembly.to_csv("../Output/Mgnify_studies_wwt_shot_metag_assembly.csv", index=False)

print("Data export complete. CSV files saved in the 'Output' folder.")