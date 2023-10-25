'''
NAME
      Identification of new HT-binding evidence from the RIs mapping to HT-peaks proccess

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

IMPUT
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
basePath = args.directory
riMappedFilePath = basePath + \
    "RI_mapping_to_TFBS-HT/output/Classical_confirmed_Strong_noHT_RIs_.v12.0_mapped.txt"
dfRiMapped = pd.read_csv(riMappedFilePath, sep="\t", comment='#', header=0)

# Create the variables containing the paths for the outputfiles
outputFilePath = basePath + "RI_mapping_to_TFBS-HT/output/New_ev_RIs_mapped.tsv"
outputFile = open(outputFilePath, "w")
# Create the header for the output file
risColumnsNamesArrays = dfRiMapped.columns.values
risColumnsNamesList = list(risColumnsNamesArrays)
riColumnNames = ""
for c in risColumnsNamesList:
    riColumnNames += (c + "\t")
print(riColumnNames)
outputColumNames = riColumnNames + "New (Evidence:reference)" + "\n"
outputFile.write(outputColumNames)

print("RIs Mapped shape")
print(dfRiMapped.shape)

counter = 0
counterB = 0
# loop through each row of the RIs dataframe
for index, row in dfRiMapped.iterrows():
    # Save the complete RI row as a string
    riLine0 = row
    riLine = ""
    for a in riLine0:
        b = str(a)
        riLine += (b + "\t")
    print(riLine)
    counter += 1
    print(counter)
    # Create a vector for the new evidence-references
    evsRefsNew = []
    tfrsEvidences = row['20)tfrsEvidence']
    tfrsEvidence = str(tfrsEvidences)
    riEvidences = row['21)riEvidence']
    riEvidence = str(riEvidences)
    htEvidence = row['Evidence;Reference']
    htEvidenceString = str(htEvidence)
    if "), (" in htEvidenceString:
        print("yes")
        htEvidenceVector = htEvidenceString.split("), (")
        monitor = 0
        for i in htEvidenceVector:
            singleEvidence1 = i
            singleEvidence2 = singleEvidence1.replace("(", "")
            singleEvidence3 = singleEvidence2.replace(")", "")
            singleEvidenceVector = singleEvidence3.split(";")
            singleEvidenceCode = singleEvidenceVector[0]
            print(singleEvidenceCode)
            # This is the most important step for determain if the evidence is new or not
            if (singleEvidenceCode not in tfrsEvidence) and (singleEvidenceCode not in riEvidence):
                newSingleEvidence = "(" + str(singleEvidence3) + ")"
                newSingleEvidenceS = newSingleEvidence.replace(";", ":")
                evsRefsNew.append(newSingleEvidenceS)

    else:
        singleEvidence = htEvidenceString.replace("(", "")
        singleEvidence = singleEvidence.replace(")", "")
        singleEvidenceVector = singleEvidence.split(";")
        singleEvidenceCode = singleEvidenceVector[0]
        monitor = 0
        if (singleEvidenceCode not in tfrsEvidence) and (singleEvidenceCode not in riEvidence):
            newSingleEvidence = "(" + str(singleEvidence) + ")"
            newSingleEvidenceS = newSingleEvidence.replace(";", ":")
            evsRefsNew.append(newSingleEvidenceS)
    # The next four lines of code are only for modify the format of the data
    evsRefsNew2 = str(evsRefsNew)
    evsRefsNew3 = evsRefsNew2.replace("[", "")
    evsRefsNew4 = evsRefsNew3.replace("]", "")
    evsRefsNewString = evsRefsNew4.replace("'", "")
    # Write in the output file the current RI with the new evidences and refreneces
    outputLine1 = (str(riLine) + str(evsRefsNewString) + "\n")
    outputFile.write(outputLine1)
    counterB += 1
    print("counterB", counterB)
outputFile.close()
print("Terminado")
