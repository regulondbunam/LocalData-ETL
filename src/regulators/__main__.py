import os
import json
import logging

import pymongo
import multigenomic_api as mg_api


from libs import arguments
from utils import utils
from regulondb.regulators import Regulator


def regulator_object_builder(regulator_obj):
    regulator_dict = {
        '_id': regulator_obj.regulator_id,
        'name': regulator_obj.name,
        'abbreviatedName': regulator_obj.abbreviated_name,
        'citations': regulator_obj.citations,
        'confidenceLevel': regulator_obj.confidence_level,
        'externalCrossReferences': regulator_obj.external_cross_references,
        'type': regulator_obj.regulator_type,
        'synonyms': regulator_obj.synonyms,
        'regulatorClass': regulator_obj.regulator_class,
        'regulationType': regulator_obj.regulation_type,
    }
    return regulator_dict


def run(args):

    utils.set_log(args.log, "regulators.log")

    tf_ids = utils.get_cyc_ids(
        url=args.url,
        collection_name='transcriptionFactors',
        ontology_name=None,
        organism=args.organism
    )
    pd_ids = utils.get_cyc_ids(
        url=args.url,
        collection_name='products',
        ontology_name=None,
        organism=args.organism
    )
    continuant_ids = utils.get_cyc_ids(
        url=args.url,
        collection_name='regulatoryContinuants',
        ontology_name=None,
        organism=args.organism
    )
    ris_cyc_ids = utils.get_cyc_ids(
        url=args.url,
        collection_name='regulatoryInteractions',
        ontology_name=None,
        organism=args.organism
    )

    mongo_client = pymongo.MongoClient(args.url)
    db = mongo_client[args.database]
    collection = db["regulators"]

    mg_api.connect(args.database, args.url)
    tf_collection = mg_api.transcription_factors.get_all()
    pd_collection = mg_api.products.get_all()
    ri_collection = mg_api.regulatory_interactions.get_all()

    regulators_list = []

    for tf_obj in tf_collection:
        regulator_obj = Regulator(
            regulator_obj=tf_obj,
            regulator_type='transcriptionFactor',
            regulator_cyc_id=utils.get_cyc_id_by_rdb_id(tf_obj.id, tf_ids),
            database=args.database,
            url=args.url,
            organism=args.organism,
            ris_cyc_ids=ris_cyc_ids
        )
        regulator_dict = regulator_object_builder(regulator_obj)
        if regulator_dict not in regulators_list:
            regulators_list.append(regulator_dict)

    srna_products = []
    srna_products_ids = []
    for pd_obj in pd_collection:
        pd_type = pd_obj.type
        if pd_type and pd_type == 'small RNA':
            regulator_obj = Regulator(
                regulator_obj=pd_obj,
                regulator_type=pd_type,
                regulator_cyc_id=utils.get_cyc_id_by_rdb_id(pd_obj.id, pd_ids),
                database=args.database,
                url=args.url,
                organism=args.organism,
                ris_cyc_ids=ris_cyc_ids
            )
            regulator_dict = regulator_object_builder(regulator_obj)
            if regulator_dict not in srna_products:
                srna_products.append(regulator_dict)
                srna_products_ids.append(regulator_dict.get('_id'))

    for ri_obj in ri_collection:
        if not ri_obj.regulator:
            continue
        if ri_obj.regulator.type in ['product', 'regulatoryContinuant']:
            if ri_obj.regulator.id in srna_products_ids:
                srna_product = next(
                    (item for item in srna_products if item['_id']
                     == ri_obj.regulator.id), None
                )
                if srna_product not in regulators_list:
                    regulators_list.append(srna_product)
            if ri_obj.regulator.type == 'regulatoryContinuant':
                continuant_obj = mg_api.regulatory_continuants.find_by_id(
                    ri_obj.regulator.id)
                regulator_obj = Regulator(
                    regulator_obj=continuant_obj,
                    regulator_type=ri_obj.regulator.type,
                    regulator_cyc_id=utils.get_cyc_id_by_rdb_id(
                        continuant_obj.id, continuant_ids),
                    database=args.database,
                    url=args.url,
                    organism=args.organism,
                    ris_cyc_ids=ris_cyc_ids
                )
                regulator_dict = regulator_object_builder(regulator_obj)
                if regulator_dict not in regulators_list:
                    regulators_list.append(regulator_dict)
    mg_api.disconnect()

    regulators_clean = []
    for regulator in regulators_list:
        regulators_clean.append(
            utils.get_only_properties_with_values(regulator))

    print(f'There are {len(regulators_clean)} reglators')

    with open(f"{args.directory}/Regulators.json", "w") as outfile:
        json.dump(regulators_clean, outfile, indent=4, sort_keys=True)

    utils.updater(regulators_clean, collection)
    utils.uploader(regulators_clean, collection)


if __name__ == '__main__':
    args = arguments.load()
    os.environ["ORGANISM"] = args.organism
    run(args)
