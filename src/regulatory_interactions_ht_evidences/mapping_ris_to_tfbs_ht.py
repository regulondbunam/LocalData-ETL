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

files_paths = {
    'ri_file': os.path.join(base_path, "RI_mapping_to_TFBS-HT/input/TF-RISet_v1.0 - Sheet1.tsv"),
    'chip_seq_authors': os.path.join(base_path, "ChIP-seq/author_files/"),
    'chip_exo_authors': os.path.join(base_path, "ChIP-exo/author_files/"),
    'dap_seq_authors': os.path.join(base_path, "DAP-seq/author_files/"),
    'gselex_authors': os.path.join(base_path, "gSELEX/author_files/"),
    'chip_seq_dataset': os.path.join(base_path, "ChIP-seq/metadata/DatasetCollection.xlsx"),
    'chip_exo_dataset': os.path.join(base_path, "ChIP-exo/metadata/DatasetCollection.xlsx"),
    'dap_seq_dataset': os.path.join(base_path, "DAP-seq/metadata/DatasetCollection.xlsx"),
    'gselex_dataset': os.path.join(base_path, "gSELEX/metadata/DatasetCollection.xlsx"),
}

# ri_file_path = base_path + \
#     "RI_mapping_to_TFBS-HT/input/TF-RISet_v1.0 - Sheet1.tsv"
# chipexoPath = base_path + \
#     "ChIP-exo/author_files/"
# chipseqPath = base_path + \
#     "ChIP-seq/author_files/"
# dapseqPath = base_path + \
#     "DAP-seq/author_files/"
# gselexPath = base_path + \
#     "gSELEX/author_files/"
# chipexoMetPath = base_path + \
#     "ChIP-exo/metadata/DatasetCollection.xlsx"
# chipseqMetPath = base_path + \
#     "ChIP-seq/metadata/DatasetCollection.xlsx"
# dapseqMetPath = base_path + \
#     "DAP-seq/metadata/DatasetCollection.xlsx"
# gselexMetPath = base_path + \
#     "gSELEX/metadata/DatasetCollection.xlsx"

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
allCollections = [
        {
            'data_frame': chip_seq_dataframe,
            'collection_name': 'Chipseq',
            'evidence_code': "EXP-CHIP-SEQ",
            'authors_data_path': files_paths.get('chip_seq_authors', None)
         },
        {
            'data_frame': chip_exo_dataframe,
            'collection_name': 'Chipexo',
            'evidence_code': "EXP-CHIP-EXO",
            'authors_data_path': files_paths.get('chip_exo_authors', None)
         },
        {
            'data_frame': gselex_dataframe,
            'collection_name': 'Gselex',
            'evidence_code': "EXP-GSELEX",
            'authors_data_path': files_paths.get('gselex_authors', None)
         },
        {
            'data_frame': dap_seq_dataframe,
            'collection_name': 'Dapseq',
            'evidence_code': "EXP-DAP-SEQ",
            'authors_data_path': files_paths.get('dap_seq_authors', None)
         },
]

# Create the variables containing the paths for the output files
output_file_path = os.path.join(
    base_path,
    "RI_mapping_to_TFBS-HT/output/Classical_confirmed_Strong_noHT_RIs_.v12.0_mapped.txt"
)
error_output_file_path = os.path.join(
    base_path,
    "RI_mapping_to_TFBS-HT/output/Error_Class_conf_withoutHTdatasets_without_coords_v0.2.txt"
)

# Open the output files
outputFile = open(output_file_path, "w")
error_output_file = open(error_output_file_path, "w")

# Write the column names in the output file
risColumnsNamesArrays = ri_dataframe.columns.values
risColumnsNamesList = list(risColumnsNamesArrays)
riColumnNames = ""
for c in risColumnsNamesList:
    riColumnNames += (c + "\t")
print(riColumnNames)
outputColumNames = riColumnNames + \
    "Evidence;Reference" + "\t" + "matchingpeaks" + "\n"
outputFile.write(outputColumNames)

# Filter the RIset, must remain only RIs with site, because the mapping process needs the site
ri_dataframes = ri_dataframe[ri_dataframe['7)tfrsLeft'] != "-"]
print("RIs shape")
print(ri_dataframe.shape)
print(ri_dataframes.shape)

# loop through each row of the RIs dataframe and assing the variables: riLine, riTf, riSiteStart, riSiteEnd and riCenter
for index, row in ri_dataframes.iterrows():
    # Save the complete RI row as a string
    riLine0 = row
    riLine = ""
    for a in riLine0:
        b = str(a)
        riLine += (b + "\t")
    print(riLine)
    riTf = row['4)regulatorName']  # ['4)tfName']
    if pd.isna(row['7)tfrsLeft']) or pd.isna(row['8)tfrsRight']):
        print(row['7)tfrsLeft'], type(row['7)tfrsLeft']))
        continue
    riSiteStart = int(row['7)tfrsLeft'])
    riSiteEnd = int(row['8)tfrsRight'])
    length = riSiteEnd - riSiteStart
    print(length)
    riCenter = riSiteStart + (length / 2)
    print(riCenter)

    # To start with the mapping:
    # Create a vector to save all evidence-references of peaks matching with ach RI
    evsRefs = []

    # Create a vector to save the data of peaks matching with ach RI
    matchingPeaks = []

    # If the current RI contain site then mapping it, if not, continue to the next RI
    if (riSiteStart != "-"):
        # loop through the elements of the vector allCollections
        for collection in allCollections:
            current_metadata = collection['data_frame']
            collection_name = collection['collection_name']
            authors_path = collection['authors_data_path']
            evidence_code = collection['evidence_code']

            # Saltar si el DataFrame es None o está vacío
            if current_metadata is None or current_metadata.empty:
                continue

            print('Working on collection:', collection_name)

            # filter the current metadata to obtain only rows were the TF match with the TF of the current RI.
            filteredMetadata = current_metadata[current_metadata["RegulonDB TF Name"] == riTf]

            # Ignore for the mapping proccess datasets from gSELEX that have not cut off
            if collection_name == "Gselex":
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "IHF"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "H-NS"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "Fis"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "Lrp"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "TFs"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "IHF"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "H-NS"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "Fis"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "HU"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "Dan"]
                filteredMetadata = filteredMetadata[filteredMetadata["RegulonDB TF Name"] != "Dps"]

            print("Ri_TF: ", riTf)
            print(current_metadata.shape)
            print(filteredMetadata.shape)

            # loop through each row of the filtered metadata of the current collection_name to compare each dataset with the same TF of the current RI
            for i, row in filteredMetadata.iterrows():
                fileName = row['Dataset File Name']
                pmidCell = str(row['PMID'])
                pmid = pmidCell.replace(".0", "")
                print("PMID: ", pmid)
                # only if filename exist, the mapping can continue
                if pd.notna(fileName):
                    evidenceReference = "(" + str(evidence_code) + \
                        ";" + str(pmid) + ")"
                    # load in a dataframe the data in the file corresponding to the current file name
                    currentDatasetPath = str(authors_path) + str(fileName)
                    dfCurrentDataset = pd.read_csv(
                        currentDatasetPath, sep='\t', header=0)
                    print(currentDatasetPath)
                    # loop through each row of the current dataset assigning the variables peakTfMainName, peakStart, peakEnd, peakCenter, peakMaximumCoverage,
                    for j, row in dfCurrentDataset.iterrows():
                        peakTfMainName = row['TF_name*']
                        pStart = row['Peak_start']
                        pEnd = row['Peak_end']
                        peakCenter = row['Peak center']
                        peakMaximumCoverage = row['Peak Maximum Coverage Position']
                        peakIntensity = row['Peak Intensity Fold Change/Binding intensity (%)']
                        peakType = "x"
                        # If the row have peak start and peak end:
                        if pd.notna(pStart):
                            peakStart = pStart
                            peakEnd = pEnd
                            peakType = "a"
                        else:
                            # If the row have not peak start and peak end but have peak center:
                            if pd.notna(peakCenter):
                                if peakCenter != "NOT FOUND":
                                    peakStart = peakCenter - 100
                                    peakEnd = peakCenter + 100
                                    peakType = "b"
                                else:
                                    peakStart = 0
                                    peakEnd = 0
                                    peakType = "f"
                            else:
                                # If the row have not peak start and peak or peak center but have peak maximum coverage:
                                if pd.notna(peakMaximumCoverage):
                                    peakStart = peakMaximumCoverage - 100
                                    peakEnd = peakMaximumCoverage + 100
                                    peakType = "c"
                                else:
                                    # If the row have not peak start and peak end or peak center or peak maximum coverage:
                                    errorOutputLine = (
                                        str(fileName) + "\t" + str(pmid) + "\n")
                                    error_output_file.write(errorOutputLine)
                                    peakType = "d"

                        fileNamePeakStart = "(" + str(evidence_code) + ":" + str(fileName) + ":" + str(
                            peakStart) + "-" + str(peakEnd) + ":" + str(peakType) + ":" + str(peakIntensity) + ")"
                        # Mapping of the current RI to the current peak
                        if (riTf == peakTfMainName) & (riCenter > peakStart) & (riCenter < peakEnd):
                            print("yes")
                            matchingPeaks.append(fileNamePeakStart)
                            if evidenceReference not in evsRefs:
                                evsRefs.append(evidenceReference)

       # The next 9 lines of code are only for modify the format of the data of evidence-reference and matching peaks
        evsRefs2 = str(evsRefs)
        evsRefs3 = evsRefs2.replace("[", "")
        evsRefs4 = evsRefs3.replace("]", "")
        evsRefsString = evsRefs4.replace("'", "")
        matchingPeaks2 = str(matchingPeaks)
        matchingPeaks3 = matchingPeaks2.replace("[", "")
        matchingPeaks4 = matchingPeaks3.replace("]", "")
        matchingPeaksString = matchingPeaks4.replace("'", "")
        # Write in the output file the current RI with the new evidences and refreneces and the peaks matching
        outputLine1 = (str(riLine) + str(evsRefsString) +
                       "\t" + str(matchingPeaksString) + "\n")
        outputFile.write(outputLine1)
    else:
        # If any peak of any collection_name match with the current RI, then write in the output file only the current RI line with the mapping columns empty
        outputLine2 = (str(riLine) + "\t" + "\n")
        outputFile.write(outputLine2)
outputFile.close()
print("Terminado")
