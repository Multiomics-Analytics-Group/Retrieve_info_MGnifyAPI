#%%
import requests
import pandas as pd

url = "https://www.ebi.ac.uk/metagenomics/api/v1/analyses"

params = {
    "biome_name": "",
    "lineage": "root:Engineered:Wastewater",
    "experiment_type": "assembly,metagenomic,metatranscriptomic",
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
    "page_size": 59  # Set the page size depending on the number of analyses
}

all_analysis_data = []  # Create a list to store all analysis data

page = 1  # Start with the first page

while True:
    params["page"] = page  # Set the page parameter for the request

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()["data"]

        # Append all analysis data from the current page to the list
        all_analysis_data.extend(data)

        # Check if there are more pages
        if "next" in response.json()["links"]:
            page += 1  # Move to the next page
        else:
            break  # No more pages to retrieve

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        break

# Now, all_analysis_data contains data from all pages
# You can process this list as needed
# %%
# Extract a list of accessions from the list of analysis data to verify that all analyses were retrieved
analyses_id_list = [analysis["attributes"]["accession"] for analysis in all_analysis_data]

#%%
# Extract a list of study IDs from the list of analysis data to verify that all studies were retrieved
study_id_list = [analysis["relationships"]["study"]["data"]["id"] if "study" in analysis["relationships"] else "" for analysis in all_analysis_data]
#%%
# Extract a list of sample IDs from the list of analysis data to verify that all samples were retrieved
sample_id_list = [analysis["relationships"]["sample"]["data"]["id"] if "sample" in analysis["relationships"] else "" for analysis in all_analysis_data]

# Filter unique sample IDs using a set
unique_sample_ids = list(set(sample_id_list))
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
# Import file with study name and other attributes from the wwt studies
study_data_df = pd.read_csv("Mgnify_studies_wwt_shot_metag_assembly.csv")

# Join the two DataFrames using the index
df_analyses_wwt_mgnify_def = df_analyses_wwt_mgnify.merge(study_data_df, on="study_id", how="left")

# Rearrange the columns
df_analyses_wwt_mgnify_def = df_analyses_wwt_mgnify_def[['analysis_id', 'sample_id', 'experiment_type', 'pipeline_version', 'instrument_platform', 
                                                         'study_id', 'bioproject', 'study_name', 'n_samples', 'centre_name', 'biomes']]
#%%
# Export the DataFrame to a CSV file
df_analyses_wwt_mgnify_def.to_csv("Mgnify_analyses_wwt_shot_metag_assembly.csv", index=False)