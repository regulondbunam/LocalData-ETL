import os
import json

import multigenomic_api as mg_api
import pymongo

from libs import arguments
from libs import collections


def run(args):

    #mg_api.connect(args.database, args.url)

    mongo_client = pymongo.MongoClient(args.url)
    mg_db = mongo_client[args.database]
    rules = load_rules(args.rules)
    kwargs = {
        'url': args.url,
        'database': args.database,
        'organism': args.organism,
        'ontology': None,
        'version': args.version,
        'source': args.source,
        'sourceversion': args.sourceversion,

    }

    if args.all or args.promoters:
        print('Updating Promoters confidenceLevel')
        collections.promoters_confidences(
            mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.regulatory_interactions:
        print('Updating RIs confidenceLevel')
        collections.regulatory_interactions_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.sites:
        print('Updating Sites confidenceLevel')
        collections.regulatory_sites_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.transcription_units:
        print('Updating TUs confidenceLevel')
        collections.transcription_units_confidences(
            mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.terminators:
        print('Updating Terminators confidenceLevel')
        collections.terminators_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.regulatory_continuants:
        print('Updating Regulatory Continuants confidenceLevel')
        # collections.regulatory_continuants_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
        pass
    if args.all or args.products:
        print('Updating Products confidenceLevel')
        collections.products_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.regulatory_complexes:
        print('Updating Regulatory Complexes confidenceLevel')
        collections.regulatory_complexes_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.transcription_factors:
        print('Updating TFs confidenceLevel')
        collections.transcription_factors_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.genes:
        print('Updating Genes confidenceLevel')
        collections.genes_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    if args.all or args.segments:
        print('Updating Segments confidenceLevel')
        # collections.segments_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
        pass
    if args.all or args.sigma_factors:
        print('Updating Sgima Factors confidenceLevel')
        collections.sigma_factors_confidences(mg_db, rules, **kwargs)
        print('Updating completed')
    mg_api.disconnect()


def load_rules(rules_path):
    with open(rules_path) as json_file:
        return json.load(json_file)


if __name__ == '__main__':
    args = arguments.load()
    run(args)
