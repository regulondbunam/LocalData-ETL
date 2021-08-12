import os
import logging

import pymongo

from libs import arguments
from libs import utils


def run(args):

    utils.set_log(args.log, "regulondb_evidence_update.log")

    mongo_client = pymongo.MongoClient(args.url)
    db = mongo_client[args.database]
    collection = db["evidences"]

    if args.update and args.update != "":
        print('Updating Evidences')
        evidences = utils.load_file(args.update)
        utils.updater(evidences.get('collectionData'), collection)

    if args.upload and args.upload != "":
        print('Uploading New Evidences')
        evidences = utils.load_file(args.upload)
        utils.uploader(evidences.get('collectionData'), collection)

    if not args.upload and not args.update:
        print('Please select an opertation -upd -upl')


if __name__ == '__main__':
    args = arguments.load()
    run(args)
