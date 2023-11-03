#%%
import requests
import pandas as pd

# Define the URL for the GET request
url = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"

# Define the query parameters
params = {
    'biome_name': 'root:Engineered:Wastewater',
    "page_size": 8  # Set the page size depending on the number of studies
}

all_studies_data = []  # Create a list to store all analysis data

page = 1  # Start with the first page

while True:
    params["page"] = page  # Set the page parameter for the request

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()["data"]

        # Append all analysis data from the current page to the list
        all_studies_data.extend(data)

        # Check if there are more pages
        if "next" in response.json()["links"]:
            page += 1  # Move to the next page
        else:
            break  # No more pages to retrieve

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        break

#%%
# Extract a list of study IDs from the list of analysis data to verify that all studies were retrieved
study_ids = [study['attributes']['accession'] for study in all_studies_data]

#%%
# Extract the desired columns and create a DataFrame
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
df_studies_wwt_mgnify.to_csv('Mgnify_studies_wwt.csv', index=False)
