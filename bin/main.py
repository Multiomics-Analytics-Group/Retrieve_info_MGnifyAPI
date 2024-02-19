#!/usr/bin/env python

""" This python script downloads fastq file given an ACCESSION related to MGnify.
 __  __              
|  \/  |                   
| \  / | ___  _ __   __ _ 
| |\/| |/ _ \| '_ \ / _` | 
| |  | | (_) | | | | (_| | 
|_|  |_|\___/|_| |_|\__,_|

__authors__ = M.Reverenna, S.A.Ruano
__copyright__ = Copyright 2024-2025
__date__ = 02 Feb 2024
__maintainer__ = Marco Reverenna
__email__ = marcor@dtu.dk, sebastian[]@dtu.dk
__status__ = Dev
"""

import os
import json
import requests
import pandas as pd
from ftplib import FTP


def fetch_studies_or_analyses_info(url, params):
    
    output_folder = "../outputs"
    os.makedirs(output_folder, exist_ok=True)

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Failed to initiate data retrieval. Status code: {response.status_code}")
        return []

    page_info = response.json()["meta"]["pagination"]
    total_count = page_info["count"]
    total_pages = page_info["pages"]

    print(f"Total items to retrieve: {total_count}")
    print(f"Total pages: {total_pages}")

    all_data = []

    for page in range(1, total_pages + 1):
        print(f"Retrieving data for page {page}/{total_pages}")
        params["page"] = page
        page_response = requests.get(url, params=params)

        if page_response.status_code != 200:
            print(f"Failed to retrieve data for page {page}. Status code: {page_response.status_code}")
            break

        data = page_response.json()["data"]
        all_data.extend(data)

    print("Data retrieval complete.")
    
    output_file_path = os.path.join(output_folder, "mgnify_studies.json")
    with open(output_file_path, "w") as outfile:
        json.dump(all_data, outfile)

    return all_data


def fetch_and_process_studies(biome_name):
    params = {'biome_name': biome_name}
    all_studies_data = fetch_studies_or_analyses_info(url, params)
    
    with open("../outputs/mgnify_studies.json", "w") as outfile:
        json.dump(all_studies_data, outfile)
    
    study_list = [{
        "study_id": study["id"],
        "study_name": study["attributes"].get("study-name"),
        "n_samples": study["attributes"].get("samples-count"),
        "bioproject": study["attributes"].get("bioproject"),
        "centre_name": study["attributes"].get("centre-name"),
        "biomes": ", ".join(biome["id"] for biome in study["relationships"].get("biomes", {}).get("data", []))
    } for study in all_studies_data]
    
    df_study = pd.DataFrame(study_list)
    df_study.to_csv(os.path.join("../outputs", "mgnify_studies.csv"), index=False)

    return df_study.head(5)


def fetch_and_process_analyses(biome_name, experiment_type):
    params = {
        "biome_name": biome_name,
        "lineage": biome_name,
        "experiment_type": experiment_type,
        "species": "",
        "sample_accession": "","pipeline_version": "","accession": "","instrument_platform": "","instrument_model": "",
        "metadata_key": "","metadata_value_gte": "","metadata_value_lte": "","metadata_value": "","study_accession": "","include": "downloads"
    }
    all_analysis_data = fetch_studies_or_analyses_info(url, params)
    
    with open("../outputs/mgnify_analyses.json", "w") as outfile:
        json.dump(all_analysis_data, outfile)
    
    analysis_list = [{
        "analysis_id": analysis["attributes"]["accession"],
        "sample_id": analysis["relationships"]["sample"]["data"]["id"] if "sample" in analysis["relationships"] else "",
        "assembly_run_id": analysis["relationships"].get("assembly" if experiment_type == "assembly" else "run", {}).get("data", {}).get("id", ""),
        "experiment_type": analysis["attributes"]["experiment-type"],
        "pipeline_version": analysis["attributes"]["pipeline-version"],
        "study_id": analysis["relationships"]["study"]["data"]["id"] if "study" in analysis["relationships"] else "",
        "instrument_platform": analysis["attributes"]["instrument-model"]
    } for analysis in all_analysis_data]
    
    df_analysis = pd.DataFrame(analysis_list)
    df_analysis.to_csv(os.path.join("../outputs", "mgnify_analysis.csv"), index=False)

    return df_analysis.head(5)


def save_unique_study_ids(csv_file_path = '../outputs/mgnify_analysis.csv', txt_file_path = f'unique_mgys_studies_ids.txt'):
    df = pd.read_csv(csv_file_path)
    unique_study_ids = pd.Series(df['study_id'].unique())
    unique_study_ids.to_csv(txt_file_path, index=False, header=False)


def get_results_info_from_MGnifystudy(study_accession):
    try:
        response = requests.get(f"https://www.ebi.ac.uk/metagenomics/api/v1/studies/{study_accession}/downloads")
        response.raise_for_status()  
        return response.json()
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None


def download_and_save_MGnifystudy_results(url, file_name, download_folder):
    file_path = os.path.join(download_folder, file_name)
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File '{file_name}' downloaded and saved in '{download_folder}'.")
    except requests.RequestException as e:
        print(f"Error during downloading from {url}: {e}")


def get_samples_metadata_from_MGnifystudy(study_accession):
    all_samples = []
    page = 1

    while True:
        print(f"Retrieving data for page {page}...")
        response = requests.get(f"https://www.ebi.ac.uk/metagenomics/api/v1/studies/{study_accession}/samples", params={"page": page})
        if response.status_code == 200:
            data = response.json()["data"]
            all_samples.extend(data)
            page_info = response.json()["meta"]["pagination"]
            if page >= page_info["pages"]:
                break
            page += 1
        else:
            print(f"Failed to retrieve data for page {page}. Status code: {response.status_code}")
            break

    if all_samples:
        print(f"GET request successful. Retrieved metadata for {len(all_samples)} samples.")
    else:
        print("No data retrieved.")
    
    return all_samples


def extract_column_names(input_file, output_name, output_directory):
    full_output_path = os.path.join(output_directory, output_name)

    with open(input_file, 'r') as file:
        column_names = file.readline().strip().split('\t')[1:]
        with open(full_output_path, 'w') as id_file:
            id_file.write('\n'.join(column_names))
    print(f"File created in {output_directory}")



def download_files_from_list(server, input_ids_file, remote_directory, local_directory):
    try:
        ftp = FTP(server)
        ftp.login()

        with open(input_ids_file, 'r') as id_file:
            ids = id_file.readlines()

            for id_name in ids:
                id_name = id_name.strip()
                folder_name = id_name[:6]

                remote_path = f"{remote_directory}/{folder_name}/{id_name}/"
                local_path = f"{local_directory}/{folder_name}/{id_name}/"

                os.makedirs(local_path, exist_ok=True)

                ftp.cwd(remote_path)

                files_to_download = ftp.nlst()

                for file in files_to_download:
                    with open(os.path.join(local_path, file), 'wb') as local_file:
                        ftp.retrbinary('RETR ' + file, local_file.write)
                    print(f"File {file} successfully downloaded in {local_path}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ftp.quit()



if __name__ == "__main__":
    
    study_accession = "MGYS00001392"
    erp_id = 'ERP011345'
    params = {"biome_name": "root:Engineered:Wastewater"}
    biome_name = "root:Engineered:Wastewater"
    experiment_type = "metagenomic"
    save_unique_study_ids()

    url = "https://www.ebi.ac.uk/metagenomics/api/v1/analyses"
    endpoint = f"https://www.ebi.ac.uk/metagenomics/api/v1/studies/{study_accession}/downloads"
    server_address = 'ftp.sra.ebi.ac.uk'

    download_folder = "./MGnify_results"
    tsv_path = f'../Output/Unified_analyses/{study_accession}/{study_accession}_{erp_id}_taxonomy_abundances_v3.0.tsv'
    local_download_directory = f'../Output/Unified_analyses/{study_accession}/'

    # retrieve info
    print("*** FIRST STEP: retrieve info started ***")
    #studies_or_analyses = fetch_studies_or_analyses_info(url, params)
    #print(f"Fetched {len(studies_or_analyses)} items.")
    # dovrebbe creare il file json dentro la cartella Output
    
    #fetch_and_process_studies(biome_name)
    #fetch_and_process_analyses(biome_name, experiment_type)
    
    os.makedirs(download_folder, exist_ok=True)

    save_unique_study_ids(csv_file_path = '../outputs/mgnify_analysis.csv', txt_file_path = '../outputs/unique_mgys_studies_ids.txt')

    # retrieve study results
    print("*** SECOND STEP: retrieve studies started ***")

    """
    results_info = get_results_info_from_MGnifystudy(study_accession)
    
    if results_info and 'data' in results_info:
        first_result = results_info['data'][0]
        file_url = first_result['attributes']['url']
        file_name = file_url.split('/')[-1]  # extract the name file from URL
        download_folder = "./downloads"
        
        os.makedirs(download_folder, exist_ok=True)
        
        download_and_save_MGnifystudy_results(file_url, file_name, download_folder)
    else:
        print("No results to download.")
    
    # retrieve samples
    print("*** THIRD STEP: retrieve samples started ***")
    
    samples_metadata = get_samples_metadata_from_MGnifystudy(study_accession)
    print(samples_metadata[:5] if samples_metadata else "No metadata found.")

    # retrieve fastq files
    print("*** FOURTH STEP: retrieve fastq files started ***")
    
    path = os.path.join('../Output/', "IDs")
    if not os.path.exists(path):
        os.makedirs(path)

    extract_column_names(input_file= tsv_path, output_name = f'ERR_IDs_from_{study_accession}.txt', output_directory = path)
    download_files_from_list(server_address, f'../Output/IDs/ERR_IDs_from_{study_accession}.txt', '/vol1/fastq/', local_download_directory)
    """