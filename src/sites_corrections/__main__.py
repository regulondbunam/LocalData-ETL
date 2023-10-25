import os
import json
import logging

import pymongo
import pythoncyc


from libs import arguments
from utils import utils


def run(**kwargs):

    organism = 'ECOLI'
    pt_connectipon = pythoncyc.select_organism(organism)
    mongo_client = pymongo.MongoClient(kwargs.get('url'))
    db = mongo_client[kwargs.get('database')]
    collection = db["regulatorySites"]

    sites = utils.get_sites_from_csv_file(
        kwargs.get('ri_file'), pt_connectipon, collection)

    utils.updater(sites, collection)


if __name__ == '__main__':
    args = arguments.load()
    run(
        ri_file=args.file_name,
        database=args.database,
        url=args.url,
    )
