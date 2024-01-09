import pandas as pd
import glob
import os

def load_abund_table(folder_path, selected_study, phylum):
    # Broad pattern to initially match files
    broad_pattern = f"{selected_study}*taxonomy*.tsv"
    file_list = glob.glob(os.path.join(folder_path, broad_pattern))

    if phylum:
        # Filtering for phylum taxonomy files
        filtered_files = [f for f in file_list if 'phylum_taxonomy' in f]
    else:
        # Filtering out unwanted files (those with '_phylum_' and '_LSU_')
        filtered_files = [f for f in file_list if '_phylum_' not in f and '_LSU_' not in f]

    # Check if the filtered list is not empty
    if filtered_files:
        filename = filtered_files[0]  # Selecting the first matching file
    else:
        print(f"No files found for the study '{selected_study}' in folder '{folder_path}'.")
        return None

    # Load abundance table for the study
    abund_table = pd.read_csv(filename, sep='\t')
    
    return abund_table

# Function to preprocess phylum abundance table for a specific study
def preprocess_abund_table_phylum(abund_table):
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
    
    return abund_table

# Functions to preprocess abundance table for a specific study and taxonomic rank
def preprocess_abund_table(abund_table, tax_rank):
    # Determine the file format and call the respective function
    if abund_table.iloc[0, 0].startswith('sk__') or str(abund_table.iloc[0, 0]) == 'Unclassified':
        return preprocess_abund_table_superkingdom(abund_table, tax_rank)
    elif abund_table.iloc[0, 0] == 'Root':
        return preprocess_abund_table_root(abund_table, tax_rank)
    else:
        raise ValueError("Unknown file format")

# Function to preprocess file format with Root as the first column
def preprocess_abund_table_root(abund_table, tax_rank):
    # Splitting taxonomic information
    taxonomic_df = abund_table[abund_table.columns[0]].str.split(';', expand=True).drop(columns=0)

    # Remove the first row corresponding to the Root taxonomic rank
    taxonomic_df = taxonomic_df.iloc[1:, :]

    # Define the column names for this format
    taxonomic_df.columns = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
    
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

    return aggregated_abund_table

# Function to preprocess file format with sk__ as the first column
def preprocess_abund_table_superkingdom(abund_table, tax_rank):
    # Split the taxonomic information into separate columns
    taxonomic_df = abund_table[abund_table.columns[0]].str.split(';', expand=True)

    # Define the column names for this format
    taxonomic_df.columns  = ['Superkingdom', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

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

    return aggregated_abund_table

# Function to filter out unwanted rows
def filter_rows(abund_table, tax_rank):
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
    # Find the index of the tax_rank in the taxonomic_columns list
    tax_rank_index = abund_table.columns.tolist().index(tax_rank)

    # Group by the taxonomic ranks up to and including the tax_rank
    groupby_columns = abund_table.columns[:tax_rank_index + 1].tolist()
    aggregated_data = abund_table.groupby(groupby_columns).sum()

    return aggregated_data.reset_index()