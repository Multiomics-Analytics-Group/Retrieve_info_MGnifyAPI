import pandas as pd
import numpy as np
import random
import glob
import os

from mgnifyapi.utils import (
    filter_filepaths, 
    assert_path,
    create_folder
)    

def retrieve_abund_filenames(
        folder_path:str,
        selected_study:str,
        phylum_files:bool,
        exclude:list=["_LSU_"]
) -> list:
    
    ## PRECONDITIONS
    assert_path(folder_path)
    if not isinstance(selected_study, str):
        raise TypeError("The selected_study argument must be a string.")
    if not isinstance(phylum_files, bool):
        raise TypeError("The phylum argument must be a boolean.")
    if not isinstance(exclude, list):
        raise TypeError("The exclude argument must be a list.")

    ## MAIN FUNCTION
    ids = ["taxonomy", selected_study]    
    exclusions = exclude.copy()
    
    # filtering for files
    if phylum_files:
        ids.append("_phylum_")
    else:
        exclusions.append("_phylum_")

    file_list = filter_filepaths(
        fpath=folder_path, 
        identifiers=ids, 
        exclude=exclusions
    )

    return file_list


def get_mgnify_vers(
    fname:str
)->float:
    """
    This is specific to waht Ive seen so far for mgnify filenames
    Get version number from filename
    Input: fname (str) - filename
    Output: version (float) - version number
    """
    ## PRECONDITIONS
    if not isinstance(fname, str):
        raise TypeError("The fname argument must be a string.")
    
    ## MAIN FUNCTION
    version = float(
        os.path.splitext(os.path.basename(fname))[0].split("_v")[-1]
    )
    return version


def filter_abund_vers(
    file_list:list,
    keep:str|list|float="all"
)->list:
    """
    Filter abundance table files by version
    Input: file_list (list) - list of file paths
           keep (str|list|float) - versions to keep
    Output: new_file_list (list) - list of file paths after filtering
    """
    ## PRECONDITIONS
    if not isinstance(file_list, list):
        raise TypeError("The file_list argument must be a list.")
    
    ## MAIN FUNCTION
    # what versions are available?
    avail_vers = [get_mgnify_vers(file) for file in file_list]
    # verbose
    print(f"Available versions: {avail_vers}")
    
    # init list
    new_file_list = []
    # keep all versions of everything
    if keep == "all":
        return file_list
    # only keeping files of the latest version
    if keep == "latest":
        latest_ver = max(avail_vers)
        # filter
        for file in file_list:
            # getting version
            ver = get_mgnify_vers(file)
            # only if latest version
            if ver == latest_ver:
                new_file_list.append(file)
        return new_file_list
    # only keeping specific versions (multiple)
    if isinstance(keep, list):
        for file in file_list:
            ver = get_mgnify_vers(file)
            if ver in keep:
                new_file_list.append(file)
        return new_file_list
    # only keeping specific version (single)
    if isinstance(keep, float): 
        for file in file_list:
            ver = get_mgnify_vers(file)
            if ver == keep:
                new_file_list.append(file)
        return new_file_list
    else:
        raise TypeError("The keep argument must be a list of floats or a float.")


def load_abund_table(
        filename:str
    ) -> pd.DataFrame:
    """
   Load the abundance table for a specific study and taxonomic rank
    Input: folder_path (str) - path to the folder containing the abundance table
           selected_study (str) - study accession number
           phylum (bool) - True if the taxonomic rank is phylum, False otherwise
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study and taxonomic rank
    """

    ## PRECONDITIONS
    if not isinstance(filename, str):
        raise TypeError("The filename argument must be a string.")

    ## MAIN FUNCTION
    abund_table = pd.read_csv(filename, sep='\t')
    return abund_table


def check_tax_rank(
    abund_table:pd.DataFrame,
    tax_rank:str
):
   
   # TODO .. below is idk -- somehow need to skip if given tax rank is not avail (before filter_rows?)
   pass



# Function to preprocess phylum abundance table for a specific study
def preprocess_abund_table_phylum(abund_table:pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the abundance table at phylum lvel for a specific study
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study after preprocessing
    """
    # Delete rows with NAN value in the 'phylum' column
    abund_table = abund_table.dropna(subset=['phylum'])

    # Delete empty strings in the 'phylum' column
    abund_table = abund_table[abund_table['phylum'] != '']
    
    # Delete rows with unassigned phylum
    abund_table = abund_table[abund_table['phylum'] != 'Unassigned']
    abund_table = abund_table[abund_table['phylum'] != 'unclassified']

    # Delete rows that contain 'Candidatus', 'candidate', or names with unofficial names
    # (e.g. 'TA06', 'WPS-2', 'WS1', 'AC1', etc.)
    abund_table = abund_table[~abund_table['phylum'].str.contains('Candidatus')]
    abund_table = abund_table[~abund_table['phylum'].str.contains('candidate')]
    
    unoff_names_pattern1 = "^[A-Z]{2,}[0-9-]*$|.*-.*|^[A-Z]{2,}"
    unoff_names_pattern2 =  r'^[A-Za-z]+(?![\d_])$'
    abund_table = abund_table[~abund_table['phylum'].str.contains(unoff_names_pattern1, regex=True)]
    abund_table = abund_table[abund_table['phylum'].str.match(unoff_names_pattern2, na=False)]
    
    # Filter out rows where the tax_rank is all in lowercase
    abund_table = abund_table[~abund_table['phylum'].str.islower()]

    # Reset index
    abund_table = abund_table.reset_index(drop=True)

    # Check if column names have the ending '_FASTA' and remove it
    abund_table.columns = abund_table.columns.str.replace('_FASTA', '')
    
    return abund_table

# Functions to preprocess abundance table for a specific study and taxonomic rank
def preprocess_abund_table(abund_table:pd.DataFrame, tax_rank:str) -> pd.DataFrame:
    """
    Preprocess the abundance table for a specific study and taxonomic rank
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
           tax_rank (str) - taxonomic rank to preprocess
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study after preprocessing
    """
    # Determine the file format and call the respective function
    if abund_table.iloc[0, 0].startswith('sk__') or str(abund_table.iloc[0, 0]) == 'Unclassified':
        return preprocess_abund_table_superkingdom(abund_table, tax_rank)
    elif abund_table.iloc[0, 0] == 'Root':
        return preprocess_abund_table_root(abund_table, tax_rank)
    else:
        raise ValueError("Unknown file format")

# Function to preprocess file format with Root as the first column
def preprocess_abund_table_root(abund_table, tax_rank):
    """
    Preprocess the abundance table for a specific study and taxonomic rank in the file format with Root as the first column
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
           tax_rank (str) - taxonomic rank to preprocess
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study after preprocessing
    """
    # Splitting taxonomic information
    taxonomic_df = abund_table[abund_table.columns[0]].str.split(';', expand=True).drop(columns=0)

    # Remove the first row corresponding to the Root taxonomic rank
    taxonomic_df = taxonomic_df.iloc[1:, :]

    # Define the column names for this format
    taxonomic_df = taxonomic_df.rename(
        columns={
            i: tax_rank for i, tax_rank in enumerate(
                ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
            )
        },
    )

    #taxonomic_df.columns = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
    
    # Isolating abundance data
    abundance_df = abund_table.iloc[:, 1:]

    # Remove the first row corresponding to the sums of the counts in each column
    abundance_df = abundance_df.iloc[1:, :]

    # Delete additional characters (e.g. 'k__', 'p__', or '[]') from the taxonomic df
    for col in taxonomic_df.columns:  
        taxonomic_df[col] = taxonomic_df[col].apply(lambda x: x[3:] if pd.notnull(x) else x)
        taxonomic_df[col] = taxonomic_df[col].str.replace('[', '').str.replace(']', '')

    # Merge taxonomic and abundance dataframes
    merged_df = pd.concat([taxonomic_df, abundance_df], axis=1)

    # Filter out unwanted rows
    filtered_df = filter_rows(merged_df, tax_rank)

    # Aggregate data
    aggregated_abund_table = aggregate_data(filtered_df, tax_rank)

    # Rename duplicated taxa
    aggregated_abund_table = rename_duplicated_taxa(aggregated_abund_table, tax_rank)

    return aggregated_abund_table

# Function to preprocess file format with sk__ as the first column
def preprocess_abund_table_superkingdom(abund_table, tax_rank):
    """
    Preprocess the abundance table for a specific study and taxonomic rank in the file format with sk__ as the first column
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
           tax_rank (str) - taxonomic rank to preprocess
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study after preprocessing
    """
    # Split the taxonomic information into separate columns
    taxonomic_df = abund_table[abund_table.columns[0]].str.split(';', expand=True)

    # Define the column names for this format
    # Define the column names for this format
    taxonomic_df = taxonomic_df.rename(
        columns={
            i: tax_rank for i, tax_rank in enumerate(
                ['Superkingdom', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
            )
        },
    )
    #taxonomic_df.columns  = ['Superkingdom', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

    # Remove the first row corresponding to the Root taxonomic rank
    taxonomic_df = taxonomic_df.iloc[1:, :]
    
    # Isolating abundance data
    abundance_df = abund_table.iloc[:, 1:]

    # Remove the first row corresponding to the sums of the counts in each column
    abundance_df = abundance_df.iloc[1:, :]

    # Delete additional characters (e.g. 'k__', 'p__', 'sk__', or '[]') from the taxonomic df
    for col in taxonomic_df.columns:
        # Using .loc for safe modification
        taxonomic_df.loc[:, col] = taxonomic_df[col].apply(lambda x: x.split("__", 1)[-1] if pd.notnull(x) else x)
        taxonomic_df.loc[:, col] = taxonomic_df[col].str.replace('[', '').str.replace(']', '')
    
    # Merge taxonomic and abundance dataframes
    merged_df = pd.concat([taxonomic_df, abundance_df], axis=1)

    # Filter out unwanted rows
    filtered_df = filter_rows(merged_df, tax_rank)

    # Aggregate data
    aggregated_abund_table = aggregate_data(filtered_df, tax_rank)

    # Fill th empty strings with NaN values
    aggregated_abund_table = aggregated_abund_table.replace('', np.nan)

    # Check if all rows in the Kingdom column are NaN values
    if aggregated_abund_table['Kingdom'].isnull().all():
        # Remove the Kingdom column
        aggregated_abund_table = aggregated_abund_table.drop(columns='Kingdom')

    # Rename duplicated taxa
    aggregated_abund_table = rename_duplicated_taxa(aggregated_abund_table, tax_rank)

    return aggregated_abund_table

# Function to filter out unwanted rows
def filter_rows(abund_table, tax_rank):
    """
    Filter out unwanted rows from the abundance table
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
           tax_rank (str) - taxonomic rank to preprocess
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study after filtering
    """
    # Delete rows with NAN value in the tax_rank column
    abund_table = abund_table.dropna(subset=[tax_rank])

    # Delete rows with empty strings, None, or whitespace in the tax_rank column
    abund_table.loc[:, tax_rank] = abund_table[tax_rank].fillna('')  # Replace NaN with empty string
    abund_table = abund_table[~abund_table[tax_rank].apply(lambda x: not x.strip())]  # Filter out empty strings

    # Delete rows with unassigned and unclassified taxkanomic rank
    abund_table = abund_table[abund_table[tax_rank] != 'Unassigned']
    abund_table = abund_table[abund_table[tax_rank] != 'unclassified']

    # Delete rows that contain 'Candidatus', 'candidate', or names with unofficial names
    # (e.g. 'TA06', 'WPS-2', 'WS1', 'AC1', etc.)
    unoff_names_pattern1 = "^[A-Z]{2,}[0-9-]*$|.*-.*|^[A-Z]{2,}"
    unoff_names_pattern2 =  r'^[A-Za-z]+(?![\d_])$'
    abund_table = abund_table[~abund_table[tax_rank].str.contains('Candidatus')]
    abund_table = abund_table[~abund_table[tax_rank].str.contains('candidate')]
    abund_table = abund_table[~abund_table[tax_rank].str.contains('mixed')]
    abund_table = abund_table[~abund_table[tax_rank].str.contains(unoff_names_pattern1, regex=True)]
    abund_table = abund_table[abund_table[tax_rank].str.match(unoff_names_pattern2, na=False)]

    # Filter out rows where the tax_rank is all in lowercase
    abund_table = abund_table[~abund_table[tax_rank].str.islower()]

    # Replace None values with empty strings
    abund_table = abund_table.fillna('')

    # Reset index
    abund_table = abund_table.reset_index(drop=True)

    return abund_table

# Function to aggregate data
def aggregate_data(abund_table, tax_rank):
    """
    Aggregate the abundance table by grouping by the taxonomic ranks up to and including the tax_rank
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
           tax_rank (str) - taxonomic rank to preprocess
    Output: aggregated_data (DataFrame) - DataFrame with the abundance table for the study after aggregation
    """
    # Find the index of the tax_rank in the taxonomic_columns list
    tax_rank_index = abund_table.columns.tolist().index(tax_rank)

    # Group by the taxonomic ranks up to and including the tax_rank
    groupby_columns = abund_table.columns[:tax_rank_index + 1].tolist()
    aggregated_data = abund_table.groupby(groupby_columns).sum()

    return aggregated_data.reset_index()

def rename_duplicated_taxa(abund_table, tax_rank):
    """
    Rename duplicated taxa in the abundance table, prefixing the name with the first four letters of the higher taxonomic rank
    Input: abund_table (DataFrame) - DataFrame with the abundance table for the study
           tax_rank (str) - taxonomic rank to preprocess
    Output: abund_table (DataFrame) - DataFrame with the abundance table for the study after renaming duplicated taxa
    """
    # Check duplicated rows at the Genus level
    duplicated_genus = abund_table[abund_table.duplicated(subset=tax_rank, keep=False)]

    # Iterate over duplicated rows
    for index, row in duplicated_genus.iterrows():
        # Find the index of the Genus column
        genus_index = abund_table.columns.get_loc(tax_rank)

        # Get the higher taxonomic rank's name and its first four letters
        higher_tax_rank = abund_table.columns[genus_index - 1]
        higher_tax_rank_value = str(row[higher_tax_rank])[:4]

        # Rename the duplicated Genus by prefixing with the higher tax rank's first four letters
        new_genus_name = f"{higher_tax_rank_value}_{row[tax_rank]}"
        abund_table.at[index, tax_rank] = new_genus_name

    return abund_table

def drop_duplicatedsamples(abundance_df, metadata_df, phylum):
    """
    Preprocess metagenomics data by ensuring only one analysis per sample is retained in the abundance table.
    Ensures that the selected analysis ID is present in the abundance table.
    Input: metadata_df (DataFrame) - DataFrame with the metadata for the study
           abundance_df (DataFrame) - DataFrame with the abundance table for the study
           phylum (bool) - True if the taxonomic rank is phylum, False otherwise
    Output: filtered_abundance_df (DataFrame) - DataFrame with the abundance table for the study after filtering
            missing_analysis_samples (list) - list of samples that do not have any analysis IDs present in the abundance table
            dropped_analysis_ids (dict) - dictionary with the sample IDs as keys and the dropped analysis IDs as values
    """
    selected_analysis_ids = {}
    missing_analysis_samples = []
    dropped_analysis_data = []  # List to store dropped analysis data

    if phylum:
        taxonomic_columns = ['kingdom', 'phylum']
    else:
        possible_taxonomic_columns = ['Superkingdom', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
        taxonomic_columns = [col for col in possible_taxonomic_columns if col in abundance_df.columns]

    for _, row in metadata_df.iterrows():
        if pd.isna(row['assembly_run_id']):
            missing_analysis_samples.append(row['sample_id'])
            continue

        analysis_ids = row['assembly_run_id'].split(';')
        valid_analysis_ids = [id for id in analysis_ids if id in abundance_df.columns]

        if valid_analysis_ids:
            selected_id = random.choice(valid_analysis_ids)
            selected_analysis_ids[row['sample_id']] = selected_id
            # Collect the IDs that are available but not chosen
            dropped_ids = set(valid_analysis_ids) - set([selected_id])
            for dropped_id in dropped_ids:
                dropped_analysis_data.append({'sample_id': row['sample_id'], 'dropped_analysis_id': dropped_id})
        else:
            missing_analysis_samples.append(row['sample_id'])

    filtered_columns = taxonomic_columns + list(selected_analysis_ids.values())
    filtered_abundance_df = abundance_df[filtered_columns]

    # Convert the list of dropped analysis data to a DataFrame
    dropped_analysis_df = pd.DataFrame(dropped_analysis_data)

    return filtered_abundance_df, missing_analysis_samples, dropped_analysis_df