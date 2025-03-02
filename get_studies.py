"""
------------------------------------------------------------------------------------------------------
Description: This script retrieves Mgnify data and metadadta for a given biome and
    data type (amplicon, shotgun metagenomics, metatranscriptomic, or assembly). 
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

from mgnifyapi.retrieve_metadata import (
    get_studies_info,
    get_analyses_info,
    studies_json_to_df,
    analyses_json_to_df,
    join_studies_and_analyses_dfs,
    get_sample_info,
    sample_json_to_df,
    join_analyses_and_sample_dfs
)
from mgnifyapi.download_studies import (
    process_study_results,
)

import os
import logging
import json
import pandas as pd


def check_progress(
    outpath:str,
    study_file:str="mgnify_studies.json",
    analyses_file:str="mgnify_analyses.json",
    sample_file:str="mgnify_samples.json",
    final_studies_file:str="df_studies.csv",
    final_analyses_file:str="df_analyses.csv",
):
    """
    TODO snakemake or something would be better than this
    """
    # check if files exist
    if (
        (os.path.exists(os.path.join(outpath, final_studies_file))) &\
        (os.path.exists(os.path.join(outpath, final_analyses_file)))
    ):
        completed = "merged_metadata_tables"
    elif os.path.exists(os.path.join(outpath, sample_file)):
        completed = "downloaded_sample_metadata"
    elif os.path.exists(os.path.join(outpath, analyses_file)):
        completed = "downloaded_analyses_metadata"
    elif os.path.exists(os.path.join(outpath, study_file)):
        completed = "downloaded_study_metadata"
    else:
        # no steps have been completed so start at beginning
        completed = None
    return completed


def check_analyses_progress(
    outpath:str,
    experiment_types:list, 
    analyses_file:str="mgnify_analyses.json",
    logger: logging.Logger|None = None, 
):

    if logger:
        verbose = logger.info
    else:
        verbose = print

    # convert to list if string
    if isinstance(experiment_types, str):
        experiment_types = [experiment_types]

    verbose(f"Checking progress of analyses for {experiment_types}")
    # if filename doesn't exist still to download
    exp_types_to_do = []
    for exp_type in experiment_types:
        fname = os.path.join(outpath, f"{exp_type}_{analyses_file}")
        if os.path.exists(fname):
            verbose(f"File {fname} exists. Skipping download of {exp_type} analyses info.")
        else:
            verbose(f"File {fname} does not exist. To download {exp_type} analyses info still.")
            exp_types_to_do.append(exp_type)

    return exp_types_to_do
    

if __name__ == "__main__":
    ## GET ARGS
    # init
    args = get_args(
        prog_name="get-mgnify-studies",
        others=dict(description="get studies from mgnify"),
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
    # Check previous progress
    logger.info(f"Progress check based on files in {outpath}")
    progress = check_progress(
        outpath=outpath,
        study_file=study_file,
        analyses_file=analyses_file,
        final_studies_file=final_studies_file,
        final_analyses_file=final_analyses_file,
    )
    logger.info(f"Progress is: {progress}")

    # Step one: download study info
    if progress is None: # then start from beginning
        logger.info("Initiating Step One: Downloading study metadata")
        df_studies_mgnify = get_studies_info(
            biome_name=biome_name,
            outpath=outpath,
            url=study_url,
            study_file=study_file
        )
        # update progress
        progress = "downloaded_study_metadata"

    # Step two: download analyses info
    if progress == "downloaded_study_metadata":
        logger.info("Step Two: Downloading analyses metadata")

        # check progress of analyses
        exp_types_to_do = check_analyses_progress(
            outpath=outpath,
            experiment_types=experiment_types,
            analyses_file=analyses_file,
            logger=logger
        )
        # download one or more experiment types iteratively, saving to individual json files
        for exp_type in exp_types_to_do:
            logger.info(
                f"Downloading {exp_type} analyses info to {os.path.join(outpath, f'{exp_type}_{analyses_file}')}"
            )
            get_analyses_info(
                biome_name=biome_name,
                experiment_types=exp_type,
                outpath=outpath,
                url=analyses_url,
                analyses_file=f"{exp_type}_{analyses_file}",
            )

        # read in analyses json(s) and save to one csv 
        logger.info(f"Reading in analyses json(s) and saving to {os.path.join(outpath, analyses_file)}")
        all_analyses_info = []
        for exp_type in experiment_types:
            fname = os.path.join(outpath, f"{exp_type}_{analyses_file}")
            logger.info(f"Reading in {fname}")
            with open(fname, "r") as infile:
                all_analyses_info += json.load(infile)
        # save to one json
        with open(os.path.join(outpath, analyses_file), "w") as outfile:
            json.dump(all_analyses_info, outfile)

        # update progress
        progress = "downloaded_analyses_metadata"


    # Step three: downloading metadata
    if progress == "downloaded_analyses_metadata":
        logger.info("Step Three: Downloading sample metadata")
        # load analyses json
        df_analyses_mgnify = analyses_json_to_df(outpath, analyses_file)
        study_ids = df_analyses_mgnify["study_id"].unique().tolist()
        # get sample metadata for all studyids
        sample_meta = get_sample_info(
            study_ids,
            outpath,
            sample_file=sample_file,
            base_url=study_url
        )

        # update progress
        progress = "downloaded_sample_metadata"


    # Step four: join all metadata
    if progress == "downloaded_sample_metadata":
        logger.info("Step Three: Joining study, analyses, sample metadata")
        # load jsons
        logger.info(f"Loading {os.path.join(outpath, study_file)}")
        df_studies_mgnify = studies_json_to_df(outpath, study_file)
        logger.info(f"Loading {os.path.join(outpath, analyses_file)}")
        df_analyses_mgnify = analyses_json_to_df(outpath, analyses_file)
        logger.info(f"Loading {os.path.join(outpath, sample_file)}")
        df_samples_mgnify = sample_json_to_df(outpath, sample_file)

        # join study and analyses dfs
        logger.info(f"Joining study and analyses dfs and saving to {os.path.join(outpath, final_studies_file)} and {os.path.join(outpath, final_analyses_file)}")
        df_mgnify = join_studies_and_analyses_dfs(
            df_studies_mgnify,
            df_analyses_mgnify,
            outpath,
            final_studies_file,
            final_analyses_file
        )

        # join analyses and sample dfs
        logger.info(f"Joining analyses and sample dfs and saving to {os.path.join(outpath, final_analyses_file)}")
        df_fin_analyses = join_analyses_and_sample_dfs(
            df_analyses_mgnify,
            df_samples_mgnify,
            outpath,
            final_analyses_file
        )

        # update progress
        progress = "merged_metadata_tables"

    # Step four: Downloading data
    if progress == "merged_metadata_tables":
        logger.info("Step Four: Downloading study data")

        # reading in relevant studies 
        df_studies = pd.read_csv(os.path.join(outpath, final_studies_file))
        study_list = df_studies["study_id"].unique().tolist()
        logger.info(f"Downloading data for # studies: {len(study_list)}")

        # check if study id in existing folders
        existing_folders = []
        studies_to_download = []
        for study_id in study_list:
            if os.path.isdir(os.path.join(outpath, down_fold, study_id)):
                existing_folders.append(study_id)
            else: 
                studies_to_download.append(study_id)
        logger.info(f"Skipping {len(existing_folders)} studies: {existing_folders}")
        logger.info(f"Downloading data for {len(studies_to_download)} studies: {studies_to_download}")
        # downlaoding data
        for study_id in studies_to_download:
            logger.info(f"Downloading data for study {study_id}")
            process_study_results(
                study_id,
                os.path.join(outpath, down_fold),
                base_url=study_url
            )

        # update progress
        progress = "downloaded_data"

    # Step five: 
    if progress == "downloaded_data":

        logger.info(
            f"""
            Process complete. 
            Info and data from biome {biome_name} for experiments {experiment_types} 
            has been downloaded and saved to {outpath}.
            """
        )

else:
    print("Imported. Script not ran.")
