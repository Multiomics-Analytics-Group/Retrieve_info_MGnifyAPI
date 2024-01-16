from Functions_preprocessing import load_abund_table, preprocess_abund_table_phylum, preprocess_abund_table, drop_duplicatedsamples
import pandas as pd

# Load one study abundance table
selected_study = 'MGYS00001392'

# Set the folder name 
folder_path = f"../Output/Unified_analyses/{selected_study}/"

# Load abundance tables
abund_table_phylum = load_abund_table(folder_path, selected_study, phylum=True)
abund_table = load_abund_table(folder_path, selected_study, phylum=False)

# Preprocess abundance tables 
abund_table_phylum = preprocess_abund_table_phylum(abund_table_phylum)
abund_table_genus = preprocess_abund_table(abund_table, tax_rank = "Genus")

# Load sample metadata
sample_metadata = pd.read_csv(f"../Output/{selected_study}_samples_metadata.csv")

# Drop duplicated samples
abund_table_phylum, missing_samp_phyl, dropped_ana_phyl = drop_duplicatedsamples(abund_table_phylum, sample_metadata, phylum=True)
abund_table_genus, missing_samp_genus, dropped_ana_genus = drop_duplicatedsamples(abund_table_genus, sample_metadata, phylum=False)

# Export the abundance tables as csv files
abund_table_phylum.to_csv(f"../Output/Abundance_tables_processed/{selected_study}/{selected_study}_phylum_taxonomy_abundances_clean.csv", index=False)
abund_table_genus.to_csv(f"../Output/Abundance_tables_processed/{selected_study}/{selected_study}_genus_taxonomy_abundances_clean.csv", index=False)

# Export the dropped samples as csv file
dropped_ana_phyl.to_csv(f"../Output/Abundance_tables_processed/{selected_study}/{selected_study}_dropped_samples.csv", index=False)

# Export the missing samples as a txt file
with open(f"../Output/Abundance_tables_processed/{selected_study}/{selected_study}_missing_samples.txt", "w") as output:
    output.write(str(missing_samp_phyl))