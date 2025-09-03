'''
NAME
       RIs mapping to peaks from HT-TF binding collection

VERSION
       4.5

AUTHOR
       Paloma Lara <palomalf86@gmail.com>

EDITOR
    Felipe Betancourt <phill.betan@gmail.com>

DESCRIPTION
       
CATEGORY
       mapping programs

USAGE
       program [OPTIONS]

ARGUMENTS

SOFTWARE REQUERIMENTS

IMPUT
     RISet.txt file (Downolad from RegulondB )
     Metadata files (.xlsx) from all four HT_TFBSs collections 
     Four Directories with all datasets for each collection

OUTPUT
     An RISet_mapped.txt file containing two additional columns "Evidence;Reference" and "matchingpeaks"
CREATION DATE
     30/06/2023
     
LOCATION EN GIT 

'''

# standard
import os

# thirdparty
import pandas as pd

# local
from libs import arguments
from utils import utils

print("inicio")

args = arguments.load()

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 50)

# Create the variables containing the paths to the RIs file, the directories with the datasets for each collection
base_path = args.directory

data_origin = args.author

files_paths = {
    'ri_file': os.path.join(base_path, "RI_mapping_to_TFBS-HT/input/TF-RISet.tsv"),
    'chip_seq_authors': os.path.join(base_path, "ChIP-seq/author_files/"),
    'chip_exo_authors': os.path.join(base_path, "ChIP-exo/author_files/"),
    'dap_seq_authors': os.path.join(base_path, "DAP-seq/author_files/"),
    'gselex_authors': os.path.join(base_path, "gSELEX/author_files/"),
    'chip_seq_dataset': os.path.join(base_path, "ChIP-seq/metadata/DatasetCollection.xlsx"),
    'chip_exo_dataset': os.path.join(base_path, "ChIP-exo/metadata/DatasetCollection.xlsx"),
    'dap_seq_dataset': os.path.join(base_path, "DAP-seq/metadata/DatasetCollection.xlsx"),
    'gselex_dataset': os.path.join(base_path, "gSELEX/metadata/DatasetCollection.xlsx"),
}

# Load in a dataframe the RIs file
ri_dataframe = pd.read_csv(files_paths.get('ri_file', None), sep="\t", comment='#', header=0)

# Load in a dataframe the metadata file of each collection
chip_exo_dataframe = utils.load_dataframe(
    path=files_paths.get('chip_exo_dataset', None)
)
chip_seq_dataframe = utils.load_dataframe(
    path=files_paths.get('chip_seq_dataset', None)
)
gselex_dataframe = utils.load_dataframe(
    path=files_paths.get('gselex_dataset', None)
)
dap_seq_dataframe = utils.load_dataframe(
    path=files_paths.get('dap_seq_dataset', None)
)

# Create a vector with the name of each collection of HT-TFBSs
all_collections = [
    {
        'data_frame': chip_seq_dataframe,
        'collection_name': 'Chipseq',
        'evidence_code': (
            "EXP-CHIP-SEQ-MANUAL" if data_origin == "galagan" else "EXP-CHIP-SEQ"
        ),
        'authors_data_path': files_paths.get('chip_seq_authors', None)
    },
    {
        'data_frame': chip_exo_dataframe,
        'collection_name': 'Chipexo',
        'evidence_code': (
            "EXP-CHIP-EXO-MANUAL" if data_origin == "otro_caso" else "EXP-CHIP-EXO"
        ),
        'authors_data_path': files_paths.get('chip_exo_authors', None)
    },
    {
        'data_frame': gselex_dataframe,
        'collection_name': 'Gselex',
        'evidence_code': (
            "EXP-GSELEX-MANUAL" if data_origin == "algún_otro" else "EXP-GSELEX"
        ),
        'authors_data_path': files_paths.get('gselex_authors', None)
    },
    {
        'data_frame': dap_seq_dataframe,
        'collection_name': 'Dapseq',
        'evidence_code': (
            "EXP-DAP-SEQ-MANUAL" if data_origin == "caso_especial" else "EXP-DAP-SEQ"
        ),
        'authors_data_path': files_paths.get('dap_seq_authors', None)
    },
]

# Create the variables containing the paths for the output files
output_file_path = os.path.join(
    base_path,
    "RI_mapping_to_TFBS-HT/output/Classical_confirmed_Strong_HT_mapped.txt"
)
error_output_file_path = os.path.join(
    base_path,
    "RI_mapping_to_TFBS-HT/output/Error_Class_conf_withoutHTdatasets_without_coords.txt"
)

# Open the output files
output_file = open(output_file_path, "w")
error_output_file = open(error_output_file_path, "w")

# Write the column names in the output file
ris_columns_names_arrays = ri_dataframe.columns.values
ris_columns_names_list = list(ris_columns_names_arrays)
ri_column_names = ""
for c in ris_columns_names_list:
    ri_column_names += (c + "\t")
print(ri_column_names)
output_column_names = ri_column_names + \
    "Evidence;Reference" + "\t" + "matchingpeaks" + "\n"
output_file.write(output_column_names)

# Filter the RIset, must remain only RIs with site, because the mapping process needs the site
ri_dataframes = ri_dataframe[ri_dataframe['7)tfrsLeft'] != "-"]
print("RIs shape")
print(ri_dataframe.shape)
print(ri_dataframes.shape)

# loop through each row of the RIs dataframe and assing the variables: ri_line, ri_tf, ri_site_start, ri_site_end and ri_center
for index, row in ri_dataframes.iterrows():
    # Save the complete RI row as a string
    ri_line0 = row
    ri_line = ""
    for a in ri_line0:
        b = str(a)
        ri_line += (b + "\t")
    print(ri_line)
    ri_tf = row['4)regulatorName']  # ['4)tfName']
    if pd.isna(row['7)tfrsLeft']) or pd.isna(row['8)tfrsRight']):
        print(row['7)tfrsLeft'], type(row['7)tfrsLeft']))
        continue
    ri_site_start = int(row['7)tfrsLeft'])
    ri_site_end = int(row['8)tfrsRight'])
    length = ri_site_end - ri_site_start
    print(length)
    ri_center = ri_site_start + (length / 2)
    print(ri_center)

    # To start with the mapping:
    # Create a vector to save all evidence-references of peaks matching with ach RI
    evs_refs = []

    # Create a vector to save the data of peaks matching with ach RI
    matching_peaks = []

    # If the current RI contain site then mapping it, if not, continue to the next RI
    if (ri_site_start != "-"):
        # loop through the elements of the vector all_collections
        for collection in all_collections:
            current_metadata = collection['data_frame']
            collection_name = collection['collection_name']
            authors_path = collection['authors_data_path']
            evidence_code = collection['evidence_code']

            # Skip if the DataFrame is None or empty
            if current_metadata is None or current_metadata.empty:
                continue

            print('Working on collection:', collection_name)

            # filter the current metadata to obtain only rows were the TF match with the TF of the current RI.
            filtered_metadata = current_metadata[current_metadata["RegulonDB TF Name"] == ri_tf]

            # Ignore for the mapping proccess datasets from gSELEX that have not cut off
            if collection_name == "Gselex":
                excluded_tfs = ["IHF", "H-NS", "Fis", "Lrp", "TFs", "HU", "Dan", "Dps"]
                filtered_metadata = filtered_metadata[
                    ~filtered_metadata["RegulonDB TF Name"].isin(excluded_tfs)
                ]

            print("Ri_TF: ", ri_tf)
            print(current_metadata.shape)
            print(filtered_metadata.shape)

            # loop through each row of the filtered metadata of the current collection_name to compare each dataset with the same TF of the current RI
            for i, row in filtered_metadata.iterrows():
                file_name = row['Dataset File Name']
                pmid_cell = str(row['PMID'])
                pmid = pmid_cell.replace(".0", "")
                print("PMID: ", pmid)
                # only if filename exist, the mapping can continue
                if pd.notna(file_name):
                    if data_origin == 'galagan':
                        # Forzar CIT de la publicación (PMID 38505828) para Galagan
                        evidence_reference = f"({evidence_code};CIT:38505828)"
                    else:
                        evidence_reference = f"({evidence_code};{pmid})"
                    # load in a dataframe the data in the file corresponding to the current file name
                    current_dataset_path = str(authors_path) + str(file_name)
                    df_current_dataset = pd.read_csv(
                        current_dataset_path, sep='\t', header=0)
                    print(current_dataset_path)
                    # loop through each row of the current dataset assigning the variables peak_tf_main_name, peak_start, peak_end, peak_center, peak_maximum_coverage,
                    for j, row in df_current_dataset.iterrows():
                        peak_tf_main_name = row.get('TF_name*', None)
                        p_start = row.get('Peak_start', None)
                        p_end = row.get('Peak_end', None)
                        peak_center = row.get('Peak center', None)
                        peak_maximum_coverage = row.get('Peak Maximum Coverage Position', None)
                        peak_intensity = row.get('Peak Intensity Fold Change/Binding intensity (%)', None)
                        peak_type = "x"

                        # If the row have peak start and peak end:
                        if pd.notna(p_start):
                            peak_start = p_start
                            peak_end = p_end
                            peak_type = "a"
                        else:
                            # If the row have not peak start and peak end but have peak center:
                            if pd.notna(peak_center):
                                if peak_center != "NOT FOUND":
                                    peak_start = peak_center - 100
                                    peak_end = peak_center + 100
                                    peak_type = "b"
                                else:
                                    peak_start = 0
                                    peak_end = 0
                                    peak_type = "f"
                            else:
                                # If the row have not peak start and peak or peak center but have peak maximum coverage:
                                if pd.notna(peak_maximum_coverage):
                                    peak_start = peak_maximum_coverage - 100
                                    peak_end = peak_maximum_coverage + 100
                                    peak_type = "c"
                                else:
                                    # If the row have not peak start and peak end or peak center or peak maximum coverage:
                                    error_output_line = str(file_name) + "\t" + str(pmid) + "\n"
                                    error_output_file.write(error_output_line)
                                    peak_type = "d"

                        file_name_peak_start = (
                                "(" + str(evidence_code) + ":" + str(file_name) + ":" +
                                str(peak_start) + "-" + str(peak_end) + ":" +
                                str(peak_type) + ":" + str(peak_intensity) + ")"
                        )

                        # Mapping of the current RI to the current peak
                        if (ri_tf == peak_tf_main_name) & (ri_center > peak_start) & (ri_center < peak_end):
                            print("yes")
                            matching_peaks.append(file_name_peak_start)
                            if evidence_reference not in evs_refs:
                                evs_refs.append(evidence_reference)

        # The next 9 lines of code are only for modify the format of the data of evidence-reference and matching peaks
        evs_refs2 = str(evs_refs)
        evs_refs3 = evs_refs2.replace("[", "")
        evs_refs4 = evs_refs3.replace("]", "")
        evs_refs_string = evs_refs4.replace("'", "")
        matching_peaks2 = str(matching_peaks)
        matching_peaks3 = matching_peaks2.replace("[", "")
        matching_peaks4 = matching_peaks3.replace("]", "")
        matching_peaks_string = matching_peaks4.replace("'", "")
        # Write in the output file the current RI with the new evidences and refreneces and the peaks matching
        output_line_1 = (str(ri_line) + str(evs_refs_string) +
                         "\t" + str(matching_peaks_string) + "\n")
        output_file.write(output_line_1)
    else:
        # If any peak of any collection_name match with the current RI, then write in the output file only the current RI line with the mapping columns empty
        output_line_2 = (str(ri_line) + "\t" + "\n")
        output_file.write(output_line_2)

output_file.close()
print("Terminado")
