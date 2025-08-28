'''
NAME
      Identification of new HT-binding evidence from the RIs mapping to HT-peaks process

VERSION
       3.0

AUTHOR
       Paloma Lara <palomalf86@gmail.com>

DESCRIPTION

CATEGORY
       mapping programs

USAGE
       program [OPTIONS]

ARGUMENTS

SOFTWARE REQUERIMENTS

INPUT
     RISet.txt file mapped containing the additional "Evidence;Referencecolumns" and "matchingpeaks"
     (the output file from the script "Mapeo_RIs_to_TFBSs-HT_v4.0.py")

OUTPUT
     An RISet_mapped.txt file with three additional columns: "Evidence;Referencecolumns" "and matchingpeaks" "New (Evidence:reference)"
CREATION DATE
     30/06/2023

LOCATION EN GIT

'''
print("inicio")
import os

import pandas as pd

from libs import arguments

args = arguments.load()

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 50)

# Create the variables containing the paths to the RIs-mapped file
base_path = args.directory
ri_mapped_file_path = base_path + \
    "RI_mapping_to_TFBS-HT/output/Classical_confirmed_Strong_noHT_RIs_.v12.0_mapped.txt"
df_ri_mapped = pd.read_csv(ri_mapped_file_path, sep="\t", comment='#', header=0)

# Create the variables containing the paths for the output files
output_file_path = base_path + "RI_mapping_to_TFBS-HT/output/New_ev_RIs_mapped.tsv"
output_file = open(output_file_path, "w")

# Create the header for the output file
ris_columns_names_arrays = df_ri_mapped.columns.values
ris_columns_names_list = list(ris_columns_names_arrays)
ri_column_names = ""
for c in ris_columns_names_list:
    ri_column_names += (c + "\t")
print(ri_column_names)
output_column_names = ri_column_names + "New (Evidence:reference)" + "\n"
output_file.write(output_column_names)

print("RIs Mapped shape")
print(df_ri_mapped.shape)

counter = 0
counter_b = 0

# loop through each row of the RIs dataframe
for index, row in df_ri_mapped.iterrows():
    # Save the complete RI row as a string
    ri_line_0 = row
    ri_line = ""
    for a in ri_line_0:
        b = str(a)
        ri_line += (b + "\t")
    print(ri_line)
    counter += 1
    print(counter)

    # Create a vector for the new evidence-references
    evs_refs_new = []
    tfrs_evidences = row.get('20)tfrsEvidence', None)
    tfrs_evidence = str(tfrs_evidences)
    ri_evidences = row.get('21)riEvidence', None)
    ri_evidence = str(ri_evidences)
    ht_evidence = row.get('Evidence;Reference', None)
    ht_evidence_string = str(ht_evidence)

    if "), (" in ht_evidence_string:
        print("yes")
        ht_evidence_vector = ht_evidence_string.split("), (")
        monitor = 0
        for i in ht_evidence_vector:
            single_evidence_1 = i
            single_evidence_2 = single_evidence_1.replace("(", "")
            single_evidence_3 = single_evidence_2.replace(")", "")
            single_evidence_vector = single_evidence_3.split(";")
            single_evidence_code = single_evidence_vector[0]
            print(single_evidence_code)
            # This is the most important step for determine if the evidence is new or not
            if (single_evidence_code not in tfrs_evidence) and (single_evidence_code not in ri_evidence):
                new_single_evidence = "(" + str(single_evidence_3) + ")"
                new_single_evidence_s = new_single_evidence.replace(";", ":")
                evs_refs_new.append(new_single_evidence_s)

    else:
        single_evidence = ht_evidence_string.replace("(", "")
        single_evidence = single_evidence.replace(")", "")
        single_evidence_vector = single_evidence.split(";")
        single_evidence_code = single_evidence_vector[0]
        monitor = 0
        if (single_evidence_code not in tfrs_evidence) and (single_evidence_code not in ri_evidence):
            new_single_evidence = "(" + str(single_evidence) + ")"
            new_single_evidence_s = new_single_evidence.replace(";", ":")
            evs_refs_new.append(new_single_evidence_s)

    # The next four lines of code are only for modify the format of the data
    evs_refs_new_2 = str(evs_refs_new)
    evs_refs_new_3 = evs_refs_new_2.replace("[", "")
    evs_refs_new_4 = evs_refs_new_3.replace("]", "")
    evs_refs_new_string = evs_refs_new_4.replace("'", "")

    # Write in the output file the current RI with the new evidences and references
    output_line_1 = (str(ri_line) + str(evs_refs_new_string) + "\n")
    output_file.write(output_line_1)
    counter_b += 1
    print("counter_b", counter_b)

output_file.close()
print("Terminado")
