import os
import json
import logging
import pymongo


def load_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data


def set_log(log_path, log_name="evidence.log"):
    if not os.path.isdir(log_path):
        raise IOError("{} directory does not exist, please edit your log argument value".format(log_path))
    log_path = os.path.join(log_path, log_name)
    logging.basicConfig(filename=log_path,
                        format='%(levelname)s - %(asctime)s - %(message)s', filemode='w', level=logging.INFO)
    return log_path


def updater(evidences, collection):
    for evidence in evidences:
        evidence_id = evidence.get('_id')
        evidence_type = evidence.get('type')
        evidence_head = evidence.get('head')
        evidence_pertains_to = evidence.get('pertainsTo')

        new_values = {}
        if evidence_type:
            new_values.setdefault("type", evidence_type)
        if evidence_head:
            new_values.setdefault("head", evidence_head)
        if evidence_pertains_to:
            new_values.setdefault("pertainsTo", evidence_pertains_to)

        query = {"_id": evidence_id}
        formatted_new_values = {
            "$set": new_values
        }

        collection.update_one(query, formatted_new_values)


def uploader(evidences, collection):
    for evidence in evidences:
        evidence_id = evidence.get('_id')
        evidence_type = evidence.get('type')
        evidence_head = evidence.get('head')
        evidence_pertains_to = evidence.get('pertainsTo')
        evidence_code = evidence.get('code')
        evidence_name = evidence.get('name')
        evidence_note = evidence.get('note')

        new_values = {}
        if evidence_id:
            new_values.setdefault("_id", evidence_id)
        if evidence_type:
            new_values.setdefault("type", evidence_type)
        if evidence_head:
            new_values.setdefault("head", evidence_head)
        if evidence_pertains_to:
            new_values.setdefault("pertainsTo", evidence_pertains_to)
        if evidence_code:
            new_values.setdefault("code", evidence_code)
        if evidence_name:
            new_values.setdefault("name", evidence_name)
        if evidence_note:
            new_values.setdefault("note", evidence_note)

        # print(new_values)
        try:
            collection.insert_one(new_values)
        except pymongo.errors.DuplicateKeyError:
            logging.error(f'"{evidence_id}" is already in RegulonDB.')
