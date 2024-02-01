#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This python script downloads fastq file given an ACCESSION related to MGnify.

__author__ = Marco Reverenna
__copyright__ = Copyright 2024-2025
__date__ = 14 Dec 2023
__maintainer__ = Marco Reverenna
__email__ = marcor@dtu.dk
__status__ = Dev
"""

import os
import json
from ftplib import FTP
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
# ftplib allows to transfer files between your computer and a server


def extract_column_names(input_file, output_name, output_directory):
    """ This function creates a txt file with the IDs of a specific ACCESSION of MGnify.

    Args:
        input_file (_tsv_): file which contains the IDs of the ACCENSION
        output_name (_txt_): file name which contains all the IDs
        output_directory (str): directory to store the output file
    """

    full_output_path = os.path.join(output_directory, output_name)

    with open(input_file, 'r') as file:
        column_names = file.readline().strip().split('\t')[1:]
        # exclude the first column considering from the second and so on
        with open(full_output_path, 'w') as id_file:
            id_file.write('\n'.join(column_names))
            # writes all the columns on txt file
    print(f"File created in {output_directory}")

def download_files_from_list(server, input_ids_file, remote_directory, local_directory):
    """ This function downloads fatsq file given a txt file wich contains the IDs.

    Args:
        server (_str_): server address (first part of the path)
        input_ids_file (_file_txt_): file which contains a list of IDs obtained from an ACCESSION
        remote_directory (_str_): path of the folder where are stored the fastq files
        local_directory (_str_): path to your local directory which contains script and data
    """

    try:
        ftp = FTP(server)
        ftp.login()
        # this time is not necessary any access keys otherwise you need to specify it
        # in that case please have a look to the module ftplib

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
                        # wb = write - binary 
                        ftp.retrbinary('RETR ' + file, local_file.write)
                        # retrbinary = download files in binary format (retrieve binary)
                    print(f"File {file} successfully downloaded in {local_path}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ftp.quit()


    def load_credentials(file_path = '~/Retrieve_info_MGnifyAPI/credentials.json'):
        # considerare il path assoluto in modo tale da correre lo script python da qualsiasi posizione
        """Load the credentials for connecting with Azure

        Args:
            file_path ('str'): _description_

        Returns:
            _type_: _description_
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

def download_files_push_store(server, input_ids_file, remote_directory, local_directory, azure_connection_string, azure_container_name):
    """ This function downloads fastq files given a txt file which contains the IDs, and uploads them to Azure Blob Storage.

    Args:
        server (str): server address (first part of the path)
        input_ids_file (file_txt): file which contains a list of IDs obtained from an ACCESSION
        remote_directory (str): path of the folder where are stored the fastq files
        local_directory (str): path to your local directory which contains script and data
        azure_connection_string (str): Azure Storage account connection string
        azure_container_name (str): Name of the Azure Blob Storage container
    """

    failed_files = []
    try:
        ftp = FTP(server)
        ftp.login()
        blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
        container_client = blob_service_client.get_container_client(azure_container_name)

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
                    local_file_path = os.path.join(local_path, file)
                    with open(local_file_path, 'wb') as local_file:
                        ftp.retrbinary('RETR ' + file, local_file.write)

                    # upload files to Azure Blob Storage
                    try:
                        blob_client = container_client.get_blob_client(blob=os.path.join(folder_name, id_name, file))
                        with open(local_file_path, "rb") as data:
                            blob_client.upload_blob(data)
                        print(f"File {file} successfully uploaded to Azure Storage in {os.path.join(folder_name, id_name)}")
                    except Exception as e:
                        print(f"Failed to upload {file}: {e}")
                        failed_files.append(file)

                    # os.remove(local_file_path) # delete the local file after upload


    except Exception as e:
        print(f"Error: {e}")
    finally:
        ftp.quit()

        # write failed files to a log file
        if failed_files:
            with open("failed_uploads.log", "w") as log_file:
                for file in failed_files:
                    log_file.write(f"{file}\n")

# download_files_push_store('server_address', 'ids_file.txt', '/remote/dir/', '/local/dir/', 'azure_connection_string', 'mycontainer')

if __name__ == "__main__":
    # example of server address = ftp://ftp.sra.ebi.ac.uk/vol1/fastq/ERR977/ERR977413/ERR977413_1.fastq.gz

    """
    si potrebbe creare una tupla
    quello di cui ho bisogno e' il lista di accessioni
    """

    """
    e' probabilmente una buona idea to rimuovere ERP e lasciare solo l'accession.
    Verificare se per una accessione ci sono piu erp_id altrimenti rimuovere.
    """

    server_address = 'ftp.sra.ebi.ac.uk'
    accession = 'MGYS00001392'
    erp_id = 'ERP011345'
    tsv_path = f'../Output/Unified_analyses/{accession}/{accession}_{erp_id}_taxonomy_abundances_v3.0.tsv'
    local_download_directory = f'../Output/Unified_analyses/{accession}/'

    # create a new folder for IDs
    path = os.path.join('../Output/', "IDs")
    if not os.path.exists(path):
        os.makedirs(path)

    # get a list of ERR ids for downloading fastq files
    extract_column_names(tsv_path,
                         f'ERR_IDs_from_{accession}.txt',
                         path
                         )
    # download fastq in local
    #download_files_from_list(server_address,
    #                         f'../Output/IDs/ERR_IDs_from_{accession}.txt',
    #                         '/vol1/fastq/',
    #                         local_download_directory
    #                         )

    # load personal credentials for Azure connection
    credentials = load_credentials('../credentials.json')

    # download fastq files and push them in the storage account
    download_files_push_store(server_address,
                              '/Retrieve_info_MGnifyAPI/Output/IDs/ERR_IDs_from_{accession}.txt',
                              '/vol1/fastq/',
                              local_download_directory,
                              azure_connection_string = f"DefaultEndpointsProtocol=https;AccountName={ credentials['account_name']};AccountKey={credentials['account_key']};EndpointSuffix=core.windows.net",
                              # DefaultEndpointsProtocol=https;AccountName=your_account_name;AccountKey=your_account_key;EndpointSuffix=core.windows.net

                              azure_container_name = 'retrievefastq'
                              )
