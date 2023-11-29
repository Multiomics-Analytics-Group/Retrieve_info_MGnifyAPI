#%%
import os
import requests

def get_summary_analyses(study_accession):
    base_url = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"
    endpoint = f"{base_url}/{study_accession}/downloads"

    print(f"Making GET request to: {endpoint}")
    response = requests.get(endpoint)

    if response.status_code == 200:
        data = response.json()
        print("GET request successful.")
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def create_study_directory(study_accession, download_folder):
    study_directory = os.path.join(download_folder, study_accession)
    try:
        os.makedirs(study_directory, exist_ok=True)
        print(f"Study directory created: {study_directory}")
    except Exception as e:
        print(f"Error creating study directory: {e}")
    return study_directory

def download_and_save_file(url, file_name, download_folder):
    file_path = os.path.join(download_folder, file_name)
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File '{file_name}' downloaded and saved in '{download_folder}'.")
    else:
        print(f"Failed to download file from {url}. Status code: {response.status_code}")

#%%
# Example usage
study_accession = "MGYS00001392"
desired_file_type = "Taxonomic assignments"  # Change this to your desired file type
download_folder = "../Output/Unified_analyses"  # Change this to your desired folder path
summary_analyses_data = get_summary_analyses(study_accession)

#%%
if summary_analyses_data:
    print("Processing summary analyses data:")
    study_directory = create_study_directory(study_accession, download_folder)

    for analysis in summary_analyses_data["data"]:
        alias = analysis["attributes"]["alias"]
        label = analysis["attributes"]["description"]["label"]
        file_format = analysis["attributes"]["file-format"]["name"]
        download_link = analysis["links"]["self"]

        # Check if the label contains the desired file type
        if desired_file_type.lower() in label.lower():
            file_name = f"{study_accession}_{alias}"
            download_and_save_file(download_link, file_name, study_directory)
else:
    print("Failed to retrieve summary analyses data.")
# %%
