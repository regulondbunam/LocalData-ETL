import re
import json

import pymongo
import pandas as pd

from libs import arguments

args = arguments.load()

database = args.database
id_database = args.id_database
url = args.url
client = pymongo.MongoClient(url)
db = client[database]
evidences_collection = db['evidences']
publications_collection = db['publications']
reg_iteractions_collection = db['regulatoryInteractions']

basePath = args.directory
inputFilePath = basePath + "RI_mapping_to_TFBS-HT/output/New_ev_RIs_mapped.tsv"
file_df = pd.read_csv(inputFilePath, sep='\t', header=0)

ri_list = []
ri_without_citations = []
for index, row in file_df.iterrows():
    if isinstance(row['New (Evidence:reference)'], str):
        if row['New (Evidence:reference)'] != '(nan)':
            ev_refs = row['New (Evidence:reference)']
            ev_refs = ev_refs.replace(' ', '')
            ev_refs = ev_refs.replace('),(', ';')
            ev_refs = ev_refs.replace('(', '').replace(')', '')
            ev_refs = ev_refs.split(';')

            citations = []
            for ev_ref in ev_refs:
                raw_citations = ev_ref.split(':')
                ev_id = None
                ev_obj = evidences_collection.find_one(
                    {'code': raw_citations[0]})
                if ev_obj is not None:
                    ev_id = ev_obj.get('_id')
                if ev_id is None:
                    short_ev_code = raw_citations[0].replace('EXP-', '')
                    regx = re.compile(short_ev_code)
                    ev_id = evidences_collection.find_one(
                        {'code': regx}).get('_id')
                publications = []
                pmids = raw_citations[1].split(',')
                for pmid in pmids:
                    pub_obj = publications_collection.find_one(
                        {'pmid': pmid})
                    if pub_obj is not None:
                        publications.append(pub_obj.get('_id'))
                    else:
                        publications.append(pmid)
                if ev_id:
                    for pub_id in publications:
                        citation = {
                            'evidences_id': ev_id,
                            'publications_id': pub_id,
                        }
                        citations.append(citation)
            ri_dict = {
                '_id': row['1)riId'],
                'citations': citations
            }
            ri_list.append(ri_dict)
        else:
            ri_dict = {
                '_id': row['1)riId'],
                'citations': row['New (Evidence:reference)']
            }
            ri_without_citations.append(ri_dict)
    else:
        ri_dict = {
            '_id': row['1)riId'],
            'citations': row['New (Evidence:reference)']
        }
        ri_without_citations.append(ri_dict)

modified_documents = 0
for ht_ri in ri_list:
    ht_ri_id = ht_ri.get("_id")
    query = {'_id': ht_ri_id}
    mg_ri = reg_iteractions_collection.find_one(query)
    mg_ri_citations = mg_ri.get("citations", [])
    mg_ri_evidences = []

    for mg_ri_citation in mg_ri_citations:
        evidence_id = mg_ri_citation.get('evidences_id')
        if evidence_id:
            mg_ri_evidences.append(evidence_id)

    ht_ri_citations = ht_ri.get("citations")
    # print(f'{ht_ri_id}')
    new_citations = []
    update_citations = []
    for ht_ri_citation in ht_ri_citations:
        if ht_ri_citation.get('evidences_id') in mg_ri_citations:
            # print("UPDATE: ", ht_ri_citation)
            update_citations.append(ht_ri_citation)
        else:
            # print("NEW: ", ht_ri_citation)
            new_citations.append(ht_ri_citation)
    for new_citation in new_citations:
        pass
        try:
            modified_documents += reg_iteractions_collection.update_one(
                {"_id": ht_ri_id},
                {"$push": {"citations": new_citation}},
                upsert=True
            ).modified_count
        except pymongo.errors.WriteError:
            modified_documents += 1
print(
    f'Total of RIs processed: {len(ri_list)}, Total of evidences inserted: {modified_documents}'
)

with open('modified_ris.json', 'w') as json_file:
    json.dump(ri_list, json_file)
with open('unmodified_ris.json', 'w') as json_file:
    json.dump(ri_without_citations, json_file)
'''
    Last try 11 nov 2023:
    Total of RIs processed: 1281, Total of RIs Modified: 1965
    Last try 31 jan 2024
    Total of RIs processed: 1329, Total of evidences inserted: 2107
'''