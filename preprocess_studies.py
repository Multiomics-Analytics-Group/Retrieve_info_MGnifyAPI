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
    create_folder
)

from mgnifyapi.preprocessing import (
    load_abund_table, 
    preprocess_abund_table_phylum, 
    preprocess_abund_table, 
    drop_duplicatedsamples
)

import os
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

    # create folder if it doesn't exist
    create_folder(os.path.join(outpath, "processed_abundance_tables"))

    for study_id in existing_folders:
        logger.info(f"Preprocessing data for study {study_id}")

        # Load sample metadata 
        # filter df_metadata for study_id's samples
        study_metadata = df_metadata[df_metadata["study_id"]==study_id]
        logger.info(f"Metadata for study {study_id} has # samples: {study_metadata.shape[0]}")

        # Load abundance tables
        logger.info(f"Loading abundance tables for study {study_id}")
        abund_table_phylum = load_abund_table(
            os.path.join(outpath, study_id), study_id, phylum=True
        )
        abund_table = load_abund_table(
            os.path.join(outpath, study_id), study_id, phylum=False
        )

        # saving for troubleshooting
        abund_table_phylum.to_csv(
            os.path.join(outpath, "processed_abundance_tables",
                f"{study_id}_phylum_taxonomy_abundances.csv"), 
            index=False
        )
        abund_table.to_csv(
            os.path.join(outpath, "processed_abundance_tables",
                f"{study_id}_genus_taxonomy_abundances.csv"), 
            index=False
        )

        # Preprocess abundance tables
        logger.info(f"Preprocessing abundance tables for study {study_id}")
        abund_table_phylum = preprocess_abund_table_phylum(abund_table_phylum)
        abund_table_genus = preprocess_abund_table(abund_table, tax_rank="Genus")

        # drop duplicated samples
        logger.info(f"Dropping duplicated samples for study {study_id}")
        abund_table_phylum, missing_samp_phyl, dropped_ana_phyl = drop_duplicatedsamples(
            abund_table_phylum, 
            study_metadata, 
            phylum=True
        )
        abund_table_genus, missing_samp_genus, dropped_ana_genus = drop_duplicatedsamples(
            abund_table_genus, 
            study_metadata, 
            phylum=False
        )

        # save to study folder
        logger.info(f"Saving processed data in {os.path.join(outpath, 'processed_abundance_tables')}")
        # export the abundance tables as csv files
        abund_table_phylum.to_csv(
            os.path.join(outpath, "processed_abundance_tables",
                f"{study_id}_phylum_taxonomy_abundances_clean.csv"), 
            index=False
        )
        abund_table_genus.to_csv(
            os.path.join(outpath, "processed_abundance_tables",
                f"{study_id}_genus_taxonomy_abundances_clean.csv"), 
            index=False
        )

        # export the missing samples as csv file
        with open(
            os.path.join(outpath, "processed_abundance_tables",
                f"{study_id}_missing_samples.txt"), "w") as output:
            output.write(str(missing_samp_phyl))

else:
    print("Imported. Script not ran.")
