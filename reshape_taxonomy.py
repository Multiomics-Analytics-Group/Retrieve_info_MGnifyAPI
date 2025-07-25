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

from mgnifyapi.tidy_taxonomy import (
    retrieve_abund_filenames,
    get_mgnify_vers,
    filter_abund_vers,
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
    outpath = config["output"]["path"]
    down_fold = config["output"]["download data folder"]
    process_fold = config["output"]["preprocessing folder"]
    biome_name = config['search params']["biome name"]
    study_url = config["urls"]["study info"]
    analyses_url = config["urls"]["analyses info"]
    experiment_types = config['search params']["experiment types"]
    mgnify_vers = config['preprocessing']['mgnify versions']
    tax_rank = config['preprocessing']['tax aggregate']
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
        if os.path.isdir(os.path.join(outpath, down_fold, study_id)):
            existing_folders.append(study_id)
        else: 
            not_existing_folders.append(study_id)
    logger.info(f"These studies were not downloaded: {not_existing_folders}")
    logger.info(f"Tidying these studies: {existing_folders}")

    # create folder if it doesn't exist
    create_folder(os.path.join(outpath,process_fold))


    for study_id in existing_folders:
        logger.info(f"Preprocessing data for study {study_id}")

        # Load sample metadata 
        # filter df_metadata for study_id's samples
        study_metadata = df_metadata[df_metadata["study_id"]==study_id]
        logger.info(f"Metadata for study {study_id} has # samples: {study_metadata.shape[0]}")


        ## Starting with phylum files :)
        # Load abundance tables
        phylum_abundance_files = retrieve_abund_filenames(
            folder_path=os.path.join(outpath, down_fold, study_id), 
            selected_study=study_id, 
            mgnify_vers=mgnify_vers,
            phylum_files=True
        )
        logger.info(f"Available files: {phylum_abundance_files}")

        # loop because maybe more than one vers
        for file in phylum_abundance_files:

            logger.info(f"Loading abundance table from {file}")
            abund_table_phylum = load_abund_table(file)

            logger.info(f"Preprocessing abundance tables for {file}")
            df_reshaped_phylum = preprocess_abund_table_phylum(abund_table_phylum)

            if df_reshaped_phylum is not None:
                # drop duplicated samples
                logger.info(f"Dropping duplicated samples for file {file}")
                df_tidy_phylum, missing_samp_phyl, dropped_ana_phyl = drop_duplicatedsamples(
                    df_reshaped_phylum, 
                    study_metadata, 
                    phylum=True
                )

                # export the abundance tables as csv files
                # save to study folder
                logger.info(f"Saving processed data in {os.path.join(outpath, 'processed_abundance_tables')}")
                # export the abundance tables as csv files
                df_tidy_phylum.to_csv(
                    os.path.join(outpath,process_fold,
                        f"{study_id}_phylum_taxonomy_abundances_clean.csv"), 
                )

                # export the missing samples as csv file
                with open(
                    os.path.join(outpath,process_fold,
                        f"{study_id}_missing_samples_phylum.txt"), "w") as output:
                    output.write(str(missing_samp_phyl))
            else:
                logger.info(f"Phylum abundance table not cleaned for study {study_id}")

        ## Now for genus files :)
        # Load abundance tables
        abundance_files = retrieve_abund_filenames(
            folder_path=os.path.join(outpath, down_fold, study_id), 
            selected_study=study_id, 
            mgnify_vers=mgnify_vers
        )
        logger.info(f"Available files: {abundance_files}")

        # loop because maybe more than one vers
        for file in abundance_files:

            logger.info(f"Loading abundance table from {file}")
            abund_table = load_abund_table(file)

            logger.info(f"Preprocessing abundance tables for {file}")
            df_reshaped = preprocess_abund_table(
                abund_table, 
                tax_rank=tax_rank
            )

            if df_reshaped is not None:
                #for troubleshooting
                df_reshaped.to_csv(
                    os.path.join(outpath,process_fold,
                        f"{study_id}_{tax_rank}_taxonomy_abundances.csv"), 
                )
                # # drop duplicated samples
                # logger.info(f"Dropping duplicated samples for file {file}")
                # df_tidy, missing_samp, dropped_ana = drop_duplicatedsamples(
                #     df_reshaped_phylum, 
                #     study_metadata, 
                #     phylum=False
                # )

                # # export the abundance tables as csv files
                # # save to study folder
                # logger.info(f"Saving processed data in {os.path.join(outpath, 'processed_abundance_tables')}")
                # # export the abundance tables as csv files
                # df_tidy.to_csv(
                #     os.path.join(outpath,process_fold,
                #         f"{study_id}_{tax_rank}_taxonomy_abundances_clean.csv"), 
                # )

                # # export the missing samples as csv file
                # with open(
                #     os.path.join(outpath,process_fold,
                #         f"{study_id}_{tax_rank}_missing_samples.txt"), "w") as output:
                #     output.write(str(missing_samp))
            else:
                logger.info(f"Abundance table not cleaned for study {study_id}")

else:
    print("Imported. Script not ran.")
