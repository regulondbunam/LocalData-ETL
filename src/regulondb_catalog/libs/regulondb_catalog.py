from ast import Str
import re
import logging

import multigenomic_api
import identifiers_api

from libs import utils
from libs import evidence_catalog_utils

evidence_codes = {}
new_evidence_codes = {}
unknwon_ids = []
EV_COLLECTION = "evidences"


def get_evidences_ids(url, database, organism, collection):
    '''
    Generates an evidence Original IDs dictionary.

    Params:
        - `url`, `String`, Database URL.
        - `database`, `String`, Database name.
        - `organism`, `String`, Organism.
        - `collection`, `String`, Collection to extract IDs.

    Returns:
        - `original_ids`, `Dict`, Original IDs dictionary.
    '''
    identifiers_api.connect(url)
    original_ids = identifiers_api.get_identifiers(
        collection, database, organism)
    identifiers_api.disconnect()
    return original_ids


def evidence_obj_builder(evidence_dict):
    '''
    Generates the evidence dictionary object with all metadata necessary in the process.

    Params:
        - `evidence_dict`, `Dict`, Evidence dictionary from Excel file.

    Returns:
        - `evidence_obj`, `Dict`, Evidence object with all metadata.
    '''
    evidence_obj = {}
    evidence_obj.update({'_id': evidence_dict.get('EVIDENCE_ID', None)})
    evidence_obj.update({'cyc_id': evidence_dict.get('ECOCYC_ID', None)})
    evidence_obj.update({'status': evidence_dict.get('STATUS', None)})
    ev_type = evidence_dict.get('EVIDENCE_TYPE', None)
    if ev_type:
        ev_type = ev_type.strip(' ')
    evidence_obj.update({'type': ev_type})
    evidence_obj.update({'head': evidence_dict.get('HEAD', None)})
    type_obj = evidence_dict.get('TYPE_OBJECT', None)
    if type_obj:
        if '|' in type_obj:
            type_obj = type_obj.split('|')
        if ',' in type_obj:
            type_obj = type_obj.split(',')
        if isinstance(type_obj, str):
            type_obj = [type_obj]
    evidence_obj.update({'pertainsTo': type_obj})
    evidence_obj.update({'code': evidence_dict.get('EVIDENCE_CODE', None)})
    evidence_obj.update({'name': evidence_dict.get('EVIDENCE_NAME', None)})
    evidence_obj.update({'note': evidence_dict.get('EVIDENCE_NOTE', None)})
    evidence_obj.update(
        {'internalComent': evidence_dict.get('EVIDENCE_INTERNAL_COMMENT', None)})
    ev_code_rule = evidence_dict.get('CV_NUMBER_RULE', None)
    if ev_code_rule:
        ev_code_rule = int(ev_code_rule)
    evidence_obj.update({'crossEvidenceCodeRule': ev_code_rule})
    evidence_obj.update(
        {'evidenceCategory': evidence_dict.get('EVIDENCE_CATEGORY', None)})
    evidence_obj.update(
        {'noteWeb': evidence_dict.get('EVIDENCE_NOTE_WEB', None)})
    evidence_obj.update(
        {'evidenceApproach': evidence_dict.get('EVIDENCE_APPROACH', None)})
    evidence_obj.update({'class': evidence_dict.get('CLASS', None)})
    return evidence_obj


def evidence_doc_builder(evidence_obj):
    '''
    Generates the evidence document that going to be insertet in the json file.

    Params:
        - `evidence_obj`, `Dict`, Evidence object with all metadata.

    Returns:
        - `evidence_document`, `Dict`, Evidence object with only necessary data for database.
    '''
    evidence_document = {}
    evidence_document.update({'_id': evidence_obj.get('_id', None)})
    evidence_document.update({'code': evidence_obj.get('code', None)})
    evidence_document.update({'head': evidence_obj.get('head', None)})
    evidence_document.update(
        {'internalComent': evidence_obj.get('internalComent', None)})
    evidence_document.update({'name': evidence_obj.get('name', None)})
    evidence_document.update({'note': evidence_obj.get('note', None)})
    evidence_document.update(
        {'pertainsTo': evidence_obj.get('pertainsTo', None)})
    evidence_document.update({'type': evidence_obj.get('type', None)})
    evidence_document.update({'class': evidence_obj.get('class', None)})
    evidence_document.update(
        {'crossEvidenceCodeRule': evidence_obj.get('crossEvidenceCodeRule', None)})
    evidence_document.update(
        {'evidenceCategory': evidence_obj.get('evidenceCategory', None)})
    evidence_document.update(
        {'evidenceApproach': evidence_obj.get('evidenceApproach', None)})
    evidence_document.update({'noteWeb': evidence_obj.get('noteWeb', None)})

    return evidence_document


def evidence_rule_builder(evidence_obj):
    '''
    Generates the evidence rules dictionaries objects with all metadata necessary in the Datamarts process.

    Params:
        - `evidence_obj`, `Dict`, Evidence object with all metadata.

    Returns:
        - `evidence_rule_obj`, `Dict`, Evidence rule object.
    '''
    evidence_rule_obj = {}
    evidence_rule_values = evidence_obj.get('name', None)
    '''evidence_rule_values = evidence_rule_values.replace(
        'cross validation ', '')
    evidence_rule_values = evidence_rule_values.replace('(', '')
    evidence_rule_values = evidence_rule_values.replace(')', '')'''
    evidence_rule_values = evidence_rule_values[
        evidence_rule_values.find("(") + 1:evidence_rule_values.find(")")
    ]
    evidence_rule_values = evidence_rule_values.split('/')
    if isinstance(evidence_rule_values, list):
        evidence_rule_values = [int(x) for x in evidence_rule_values]
    evidence_rule_obj.update({'rules_values': evidence_rule_values})
    evidence_rule_obj.update({'type': evidence_obj.get('type', None)})
    evidence_rule_obj.update(
        {'pertainsTo': evidence_obj.get('pertainsTo', None)})
    evidence_rule_obj.update(
        {'evidenceCategory': evidence_obj.get('evidenceCategory', None)})

    return evidence_rule_obj


def append_update_ecocyc_evidence(
        evidence_obj: dict,
        update_evidences: list,
        unknown_evidences: list,
        url: str,
        database: str,
        evidence_original_ids: list
):
    '''
    Insert evidences to update or unkown in their lists.

    Params:
        - `evidence_obj`, `Dict`, Evidence object with all metadata.
        - `update_evidences`, `List`, Evidences to update list.
        - `unknown_evidences`, `List`, Unkown evidences list.
        - `url`, `String`, Database URL.
        - `database`, `String`, Database name.
        - `evidence_original_ids`, `Dict`, Original IDs dictionary.
    '''
    ev_code = evidence_obj.get('code', None)
    ev_cyc_id = evidence_obj.get("cyc_id", None)
    ev_rdb_id = evidence_original_ids.get(f'|{ev_cyc_id}|')
    ev_id = evidence_obj.get("_id", None)
    # print(f"{ev_cyc_id} <-> {ev_rdb_id}")

    try:
        multigenomic_api.connect(database, url)
        mg_evidence = multigenomic_api.evidences.find_by_id(ev_rdb_id)
        multigenomic_api.disconnect()
    except Exception:
        print(
            f'Problem Querying >  {ev_id} : {ev_code} : {evidence_obj.get("name",None)}')
        mg_evidence = None

    if not mg_evidence:
        try:
            multigenomic_api.connect(database, url)
            mg_evidence = multigenomic_api.evidences.find_by_code(ev_code)
            multigenomic_api.disconnect()
        except:
            mg_evidence = None
    if not mg_evidence:
        try:
            multigenomic_api.connect(database, url)
            mg_evidence = multigenomic_api.evidences.find_by_id(ev_id)
            multigenomic_api.disconnect()
        except:
            mg_evidence = None

    if mg_evidence:
        evidence_codes.update({ev_id: ev_code})
        evidence_obj.update({'_id': mg_evidence.id})
        update_evidence = evidence_doc_builder(evidence_obj)
        update_evidences.append(update_evidence)
    else:
        logging.critical(
            f"Evidence {ev_id} {ev_code}" f" is not registered in RegulonDBMultigenomic, please check this out, inconsistencies might be presented."
        )
        evidence_codes.update({ev_id: ev_code})
        evidence_obj.update({'_id': mg_evidence.id})
        unknown_evidence = evidence_doc_builder(evidence_obj)
        unknown_evidences.append(unknown_evidence)


def extract_process(
    catalog_evidences_filename: str,
    new_evidences_filename: str,
    update_evidences_filename: str,
    unknown_evidences_filename: str,
    evidence_rules_filename: str,
    url: str,
    database: str,
    organism: str
) -> None:
    '''
    Manage the extraction transformation an load of evidences json files.

    Params:
        - `catalog_evidences_filename`, `String`, Evidence catalog file name.
        - `new_evidences_filename`, `String`, New Evidences catalog file name.
        - `update_evidences_filename`, `String`, Update Evidences catalog file name.
        - `unknown_evidences_filename`, `String`, Unknown Evidences catalog file name.
        - `evidence_rules_filename`, `String`, Evidences Rules catalog file name.
        - `evidence_obj`, `Dict`, Evidence object with all metadata.
        - `url`, `String`, Database URL.
        - `database`, `String`, Database name.
        - `evidence_original_ids`, `Dict`, Original IDs dictionary.
    '''
    evidence_original_ids = get_evidences_ids(
        url, database, organism, EV_COLLECTION)
    # print(evidence_original_ids)
    evidences_catalog = evidence_catalog_utils.get_evidences_catalog(
        catalog_evidences_filename)
    new_evidences = []
    update_evidences = []
    unknown_evidences = []
    evidence_rules = []
    for evidence in evidences_catalog:
        # Extracting data from Evidence dict with full metadata
        evidence_obj = evidence_obj_builder(evidence)

        evidence_cyc_id = evidence_obj.get('cyc_id', None)
        evidence_status = evidence_obj.get('status', None)
        evidence_class = evidence_obj.get('class', None)

        if evidence_status:
            if evidence_class.lower() == 'rule':
                evidence_rule_obj = evidence_rule_builder(evidence_obj)
                evidence_rules.append(evidence_rule_obj)
                continue
            # Only Evidences with it Ecocyc ID will be peocessed
            if evidence_status.lower() == 'update':
                if evidence_cyc_id:
                    append_update_ecocyc_evidence(
                        evidence_obj,
                        update_evidences,
                        new_evidences,
                        url,
                        database,
                        evidence_original_ids
                    )

            elif evidence_status.lower() == 'new':
                if evidence_cyc_id:
                    new_evidence = evidence_doc_builder(evidence_obj)
                    new_evidences.append(new_evidence)

    # TODO: When there are New Evidences check that procedure works corectly
    temp_new_evidences = []
    for new_ev in new_evidences:
        if not new_ev.get('_id'):
            continue
        if new_ev.get('evidenceCategory') == 'independent cross-validation':
            continue
        original_name = new_ev.get('name')
        old_ids = re.findall('GID[0-9]{9}', original_name)
        new_name = original_name
        if old_ids is not []:
            for old_id in old_ids:
                new_id = evidence_codes.get(old_id)
                if new_id:
                    # new_name = re.sub('GID[0-9]{9}', new_id, new_name)
                    new_name = new_name.replace(old_id, new_id)
                    # new_name = re.sub('RDB[A-Z]{7}[0-9]{5}', new_id, new_name)
        new_ev.update({'name': new_name})

        original_head = new_ev.get('head')
        if original_head:
            old_ids = re.findall('RDB[A-Z]{7}[0-9]{5}', original_head)
            new_head = original_head
            if old_ids is not []:
                for old_id in old_ids:
                    new_id = evidence_codes.get(old_id)
                    if new_id:
                        new_head = new_head.replace(old_id, new_id)
                        # new_head = re.sub('GID[0-9]{9}', new_id, new_head)
                        # new_head = re.sub('RDB[A-Z]{7}[0-9]{5}', new_id, new_head)
            new_ev.update({'head': new_head})
        original_head = new_ev.get('head')
        if original_head:
            old_ids = re.findall('GID[0-9]{9}', original_head)
            new_head = original_head
            if old_ids is not []:
                for old_id in old_ids:
                    new_id = evidence_codes.get(old_id)
                    if new_id:
                        new_head = new_head.replace(old_id, new_id)
                        # new_head = re.sub('GID[0-9]{9}', new_id, new_head)
                        # new_head = re.sub('RDB[A-Z]{7}[0-9]{5}', new_id, new_head)
            new_ev.update({'head': new_head})

        original_code = new_ev.get('code')
        old_ids = re.findall('GID[0-9]{9}', original_code)
        new_code = original_code
        if old_ids is not []:
            for old_id in old_ids:
                new_id = evidence_codes.get(old_id)
                if new_id:
                    # print(new_id)
                    # new_code = re.sub('GID[0-9]{9}', new_id, new_code)
                    new_code = new_code.replace(old_id, new_id)
                    # new_code = re.sub('RDB[A-Z]{7}[0-9]{5}', new_id, new_code)
        new_ev.update({'code': new_code})
        code_ids = re.findall('GID[0-9]{9}', new_code)
        if new_ev.get('head'):
            head_id = re.findall('GID[0-9]{9}', new_ev.get('head'))
            if head_id == []:
                temp_new_evidences.append(new_ev)
            else:
                unknown_evidences.append(new_ev)
        else:
            if code_ids == []:
                temp_new_evidences.append(new_ev)
            else:
                unknown_evidences.append(new_ev)

    # The next procedure is for remove unknown head of update_evidences that have the old IDs format.
    for upd_ev in update_evidences:
        original_head = upd_ev.get('head')
        if original_head:
            old_ids = re.findall('GID[0-9]{9}', original_head)
            new_head = original_head
            for old_id in old_ids:
                new_id = evidence_codes.get(old_id)
                if new_id != None:
                    upd_ev.update({'head': new_id})
                else:
                    upd_ev.update({'head': None})

    utils.create_json({'classAcronym': 'ECOLI', 'collectionName': 'evidences', 'organism': 'ECOLI',
                      'subClassAcronym': 'EVC', 'collectionData': temp_new_evidences}, new_evidences_filename)
    utils.create_json({'classAcronym': 'ECOLI', 'collectionName': 'evidences', 'organism': 'ECOLI',
                      'subClassAcronym': 'EVC', 'collectionData': update_evidences}, update_evidences_filename)
    utils.create_json({'classAcronym': 'ECOLI', 'collectionName': 'evidences', 'organism': 'ECOLI',
                      'subClassAcronym': 'EVC', 'collectionData': unknown_evidences}, unknown_evidences_filename)
    utils.create_json({'rules': evidence_rules}, evidence_rules_filename)
