"""
------------------------------------------------------------------------------------------------------
Description: Preprocessing the downloaded study data 
Version: 2.0
License: MIT License
Usage: python get_studies.py --config config.yaml
Warning1: The script relies on the MGnify API, which could have high traffic. 
    If the script fails, re-run later.
Warning2: If the script exits due to Warning1 or manually, remove incomplete outputs 
    to avoid errors in subsequent runs.
------------------------------------------------------------------------------------------------------
"""
# Import libraries
from mgnifyapi.utils import (
    config_loader,
    get_args,
    get_logger,
    assert_nonempty_keys,
    assert_nonempty_vals,
)

from mgnifyapi.preprocessing import (
    load_abund_table, 
    preprocess_abund_table_phylum, 
    preprocess_abund_table, 
    drop_duplicatedsamples
)

import os
import logging
import json
import pandas as pd
 

if __name__ == "__main__":
    ## GET ARGS
    # init
    args = get_args(
        prog_name="preprocess-mgnify-studies",
        others=dict(description="preprocessing"),
    )
    config_filepath = args.config


    ## START LOG FILE
    logger = get_logger()
    logger.info(f"Arguments: {args}")

    ## LOAD CONFIG PARAMETERS
    logger.info(f"Path to config file: {config_filepath}")
    # load config params
    logger.info("Loading config params ... ")
    config = config_loader(config_filepath)
    assert_nonempty_keys(config)
    assert_nonempty_vals(config)
    outpath = config["output path"]
    biome_name = config['search params']["biome name"]
    study_url = config["urls"]["study info"]
    analyses_url = config["urls"]["analyses info"]
    experiment_types = config['search params']["experiment types"]
    if isinstance(experiment_types, str):
        experiment_types = [experiment_types]    
    logger.info(f"Configuration: {config}")

    ## DEFAULT FILE NAMES
    study_file="mgnify_studies.json"
    analyses_file="mgnify_analyses.json"
    sample_file="mgnify_samples.json"
    final_studies_file="df_studies.csv"
    final_analyses_file="df_analyses.csv"

    ## MAIN FUNCTION
    # reading in relevant studies and metadata
    logger.info(
        f"Reading in relevant studies and metadata from {os.path.join(outpath, final_analyses_file)}"
    )
    df_metadata = pd.read_csv(os.path.join(outpath, final_analyses_file))
    study_list = df_metadata["study_id"].unique().tolist()
    logger.info(f"Tidying data for # studies: {len(study_list)}")

    # preprocess data for each study if folder exists
    # which study folders exist/were downloaded?
    existing_folders = []
    not_existing_folders = []
    for study_id in study_list:
        if os.path.isdir(os.path.join(outpath, study_id)):
            existing_folders.append(study_id)
        else: 
            not_existing_folders.append(study_id)
    logger.info(f"These studies were not downloaded: {not_existing_folders}")
    logger.info(f"Tidying these studies: {existing_folders}")


    for study_id in existing_folders:
        logger.info(f"Preprocessing data for study {study_id}")

        # HERE 
        # filter df_metadata for study_id's samples


        # Load abundance tables
        abund_table_phylum = load_abund_table(
            os.path.join(outpath, study_id), study_id, phylum=True
        )
        abund_table = load_abund_table(
            os.path.join(outpath, study_id), study_id, phylum=False
        )

        # Preprocess abundance tables
        abund_table_phylum = preprocess_abund_table_phylum(abund_table_phylum)
        abund_table_genus = preprocess_abund_table(abund_table, tax_rank="Genus")

        # Load sample metadata




else:
    print("Imported. Script not ran.")
