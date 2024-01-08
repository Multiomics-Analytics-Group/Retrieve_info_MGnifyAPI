#%%
from Functions_preprocessing import load_abund_table, preprocess_abund_table_phylum, preprocess_abund_table

# Load one study abundance table
selected_study = 'MGYS00001392'

# Set the folder name 
folder_path = f"../Output/Unified_analyses/{selected_study}/"

# Load abundance tables
abund_table_phylum = load_abund_table(folder_path, selected_study, phylum=True)
abund_table = load_abund_table(folder_path, selected_study, phylum=False)
#%%
# Preprocess abundance tables 
abund_table_phylum = preprocess_abund_table_phylum(abund_table_phylum)
abund_table_genus = preprocess_abund_table(abund_table, tax_rank = "Genus")

#%%
# Export the abundance tables as csv files
abund_table_phylum.to_csv("../Output/Abundance_tables_processed/MGYS00001392/MGYS00001392_phylum_taxonomy_abundances_v3.0_clean.csv", index=False)
abund_table_genus.to_csv("../Output/Abundance_tables_processed/MGYS00001392/MGYS00001392_genus_taxonomy_abundances_v3.0_clean.csv", index=False)
#%%