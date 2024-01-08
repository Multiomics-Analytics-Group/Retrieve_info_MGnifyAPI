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

# Function to preprocess abundance table for a specific study and taxonomic rank
def preprocess_abund_table(abund_table, tax_rank):
    # Split the taxonomic information into separate columns, and drop the first column, 
    # which contains just the Root word (not a taxonomic rank)
    taxonomic_columns = abund_table[abund_table.columns[0]].str.split(';', expand=True).drop(columns=0)

    # Rename the new columns as per the taxonomic ranks
    taxonomic_columns.columns = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

    # Join the new taxonomic columns with the original abundance data, assuming 
    # the abundance data starts from the second column
    abund_table = pd.concat([taxonomic_columns, abund_table.iloc[:, 1:]], axis=1)

    # Remove the first row corresponding to the sums of the counts in each column
    abund_table = abund_table.iloc[1:, :]

    # Delete additional characters (e.g. 'k__', 'p__', or '[]') from the taxonomic columns
    for col in abund_table.columns[:7]:  # Assuming the first 7 columns are taxonomic ranks
        abund_table[col] = abund_table[col].apply(lambda x: x[3:] if pd.notnull(x) else x)
        abund_table[col] = abund_table[col].str.replace('[', '').str.replace(']', '')

    # Delete rows with NAN value in the tax_rank column
    abund_table = abund_table.dropna(subset=[tax_rank])

    # Delete rows with empty strings, None, or whitespace in the tax_rank column
    abund_table[tax_rank] = abund_table[tax_rank].fillna('')  # Replace NaN with empty string
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

    # Reset index
    abund_table = abund_table.reset_index(drop=True)

    # Identify the columns for aggregation (abundance data) and the taxonomic columns
    tax_column_names = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

    # Find the index of the tax_rank in the taxonomic_columns list
    tax_rank_index = tax_column_names.index(tax_rank)

    # Group by the taxonomic ranks up to and including the tax_rank
    groupby_columns = tax_column_names[:tax_rank_index + 1]
    aggregated_abund_table = abund_table.groupby(groupby_columns).sum()

    # Reset index to turn the groupby columns back into columns in the DataFrame
    aggregated_abund_table = aggregated_abund_table.reset_index()

    return aggregated_abund_table