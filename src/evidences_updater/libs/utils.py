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
        raise IOError(
            "{} directory does not exist, please edit your log argument value".format(log_path))
    log_path = os.path.join(log_path, log_name)
    logging.basicConfig(filename=log_path,
                        format='%(levelname)s - %(asctime)s - %(message)s', filemode='w', level=logging.INFO)
    return log_path


def updater(evidences, collection):
    for evidence in evidences:
        evidence_id = evidence.get('_id', None)
        evidence_type = evidence.get('type', None)
        evidence_head = evidence.get('head', None)
        evidence_pertains_to = evidence.get('pertainsTo', None)
        evidence_cv_rule = evidence.get('crossEvidenceCodeRule', None)
        evidence_category = evidence.get('evidenceCategory', None)
        evidence_note_web = evidence.get('noteWeb', None)
        evidence_approach = evidence.get('evidenceApproach', None)
        evidence_code = evidence.get('code', None)

        new_values = {}
        if evidence_type:
            new_values.setdefault("type", evidence_type)
        if evidence_head:
            new_values.setdefault("head", evidence_head)
        if evidence_pertains_to:
            new_values.setdefault("pertainsTo", evidence_pertains_to)
        if evidence_cv_rule:
            new_values.setdefault('crossEvidenceCodeRule', evidence_cv_rule)
        if evidence_category:
            new_values.setdefault('evidenceCategory', evidence_category)
        if evidence_note_web:
            new_values.setdefault('noteWeb', evidence_note_web)
        if evidence_approach:
            new_values.setdefault('evidenceApproach', evidence_approach)
        if evidence_code:
            new_values.setdefault('code', evidence_code)

        query = {"_id": evidence_id}
        formatted_new_values = {
            "$set": new_values
        }

        collection.update_one(query, formatted_new_values)


def uploader(evidences, collection):
    for evidence in evidences:
        evidence_id = evidence.get('_id', None)
        evidence_type = evidence.get('type', None)
        evidence_head = evidence.get('head', None)
        evidence_pertains_to = evidence.get('pertainsTo', None)
        evidence_code = evidence.get('code', None)
        evidence_name = evidence.get('name', None)
        evidence_note = evidence.get('note', None)
        evidence_cv_rule = evidence.get('crossEvidenceCodeRule', None)
        evidence_category = evidence.get('evidenceCategory', None)
        evidence_note_web = evidence.get('noteWeb', None)
        evidence_approach = evidence.get('evidenceApproach', None)

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
        if evidence_cv_rule:
            new_values.setdefault('crossEvidenceCodeRule', evidence_cv_rule)
        if evidence_category:
            new_values.setdefault('evidenceCategory', evidence_category)
        if evidence_note_web:
            new_values.setdefault('noteWeb', evidence_note_web)
        if evidence_approach:
            new_values.setdefault('evidenceApproach', evidence_approach)

        # print(new_values)
        try:
            collection.insert_one(new_values)
        except pymongo.errors.DuplicateKeyError:
            logging.error(f'"{evidence_id}" is already in RegulonDB.')
