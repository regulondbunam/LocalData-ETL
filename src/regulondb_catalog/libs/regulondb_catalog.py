import re
import logging

import multigenomic_api

from libs import utils
from libs import evicence_catalog_utils

evidence_ids = {}
evidence_codes = {}
new_evidence_codes = {}
unknwon_ids = []


def append_update_ecocyc_evidence(evidence_catalog, update_evidences, unknwon_evidences):
    ev_code = f'{evidence_catalog["EVIDENCE_CODE"]}'
    ev_id = f'{evidence_catalog["EVIDENCE_ID"]}'
    # print(f"{evidence_catalog}")
    try:
        ecocyc_evidence = multigenomic_api.evidences.find_one_by_code(ev_code)
    except Exception:
        # print(f'{ev_id} : {ev_code} : {evidence_catalog["EVIDENCE_NAME"]}')
        ecocyc_evidence = None

    if ecocyc_evidence is None:
        try:
            ecocyc_evidence = multigenomic_api.evidences.find_by_id(ev_id)
        except:
            ecocyc_evidence = None

    if ecocyc_evidence is not None:
        evidence_ids.update({ev_id: ecocyc_evidence.id})
        evidence_codes.update({ev_id: ev_code})
        update_evidence = {"_id": ecocyc_evidence.id}
        evidence_type = evidence_catalog["EVIDENCE_TYPE (Weak, Strong, Confirmed)"]
        evidence_head = evidence_catalog["HEAD"]
        object_type = evidence_catalog["TYPE_OBJECT"]

        if evidence_type is not None:
            update_evidence.update({'type': evidence_type.strip(' ')})
        if evidence_head is not None:
            update_evidence.update({'head': evidence_head})
        if object_type is not None:
            object_type = object_type.split('|')
            update_evidence.update({'pertainsTo': object_type})

        update_evidences.append(update_evidence)
    else:
        logging.critical(
            f"Evidence {evidence_catalog['EVIDENCE_ID']} {evidence_catalog['EVIDENCE_CODE']}" f" is not registered in EcoCyc, please check this out, inconsistencies might be presented.")
        unknwon_evidence = {"_id": evidence_catalog['EVIDENCE_ID']}
        evidence_type = evidence_catalog["EVIDENCE_TYPE (Weak, Strong, Confirmed)"]
        evidence_code = evidence_catalog["EVIDENCE_CODE"]
        evidence_name = evidence_catalog["EVIDENCE_NAME"]
        evidence_note = evidence_catalog["EVIDENCE_NOTE"]
        evidence_internal_comment = evidence_catalog["EVIDENCE_INTERNAL_COMMENT"]
        evidence_head = evidence_catalog["HEAD"]
        object_type = evidence_catalog["TYPE_OBJECT"]

        if evidence_type is not None:
            unknwon_evidence.update({'type': evidence_type.strip(' ')})
        if evidence_head is not None:
            unknwon_evidence.update({'head': evidence_head})
        if object_type is not None:
            object_type = object_type.split('|')
            unknwon_evidence.update({'pertainsTo': object_type})
        if evidence_code is not None:
            unknwon_evidence.update({'code': evidence_code})
        if evidence_name is not None:
            unknwon_evidence.update({'name': evidence_name})
        if evidence_note is not None:
            unknwon_evidence.update({'note': evidence_note})
        if evidence_internal_comment is not None:
            unknwon_evidence.update(
                {'internalComment': evidence_internal_comment})

        evidence_ids.update(
            {evidence_catalog['EVIDENCE_ID']: evidence_catalog['EVIDENCE_ID']})
        evidence_codes.update({evidence_catalog['EVIDENCE_ID']: evidence_code})
        unknwon_evidences.append(unknwon_evidence)


def extract_process(catalog_evidences_filename: str, new_evidences_filename: str, update_evidences_filename: str, unknwon_evidences_filename: str) -> None:
    evidences_catalog = evicence_catalog_utils.get_evidences_catalog(
        catalog_evidences_filename)
    new_evidences = []
    update_evidences = []
    unknwon_evidences = []
    for evidence in evidences_catalog:
        # evidence_id = evidence["EVIDENCE_ID"]
        # evidence_code = evidence["EVIDENCE_CODE"]
        # evidence_type = evidence["EVIDENCE_TYPE (Weak, Strong, Confirmed)"].strip()
        # evidence_head = evidence["HEAD"]
        # evidence_name = evidence["EVIDENCE_NAME"]
        # print(evidence["EVIDENCE_ID"])
        evidence_status = evidence["STATUS"]
        if evidence_status:
            if evidence_status.lower() == 'checked':
                append_update_ecocyc_evidence(
                    evidence, update_evidences, new_evidences)

            elif evidence_status.lower() == 'new':
                new_evidence = {"_id": evidence['EVIDENCE_ID']}

                evidence_type = evidence["EVIDENCE_TYPE (Weak, Strong, Confirmed)"]
                evidence_head = evidence["HEAD"]
                object_type = evidence["TYPE_OBJECT"]
                evidence_code = evidence["EVIDENCE_CODE"]
                evidence_name = evidence["EVIDENCE_NAME"]
                evidence_note = evidence["EVIDENCE_NOTE"]
                evidence_internal_comment = evidence["EVIDENCE_INTERNAL_COMMENT"]

                if evidence_type is not None:
                    new_evidence.update({'type': evidence_type.strip(' ')})
                if evidence_head is not None:
                    new_evidence.update({'head': evidence_head})
                if object_type is not None:
                    object_type = object_type.split('|')
                    new_evidence.update({'pertainsTo': object_type})
                if evidence_code is not None:
                    new_evidence.update({'code': evidence_code})
                if evidence_name is not None:
                    new_evidence.update({'name': evidence_name})
                if evidence_note is not None:
                    new_evidence.update({'note': evidence_note})
                if evidence_internal_comment is not None:
                    new_evidence.update(
                        {'internalComment': evidence_internal_comment})

                new_evidence_codes.update(
                    {evidence['EVIDENCE_ID']: evidence_code})
                new_evidences.append(new_evidence)

    temp_new_evidences = []
    for new_ev in new_evidences:

        original_name = new_ev.get('name')
        old_ids = re.findall('GID[0-9]{9}', original_name)
        new_name = original_name
        if old_ids is not []:
            for old_id in old_ids:
                new_id = evidence_codes.get(old_id)
                if new_id:
                    #new_name = re.sub('GID[0-9]{9}', new_id, new_name)
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
                        #new_head = re.sub('GID[0-9]{9}', new_id, new_head)
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
                        #new_head = re.sub('GID[0-9]{9}', new_id, new_head)
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
                    #new_code = re.sub('GID[0-9]{9}', new_id, new_code)
                    new_code = new_code.replace(old_id, new_id)
                    # new_code = re.sub('RDB[A-Z]{7}[0-9]{5}', new_id, new_code)
        new_ev.update({'code': new_code})
        code_ids = re.findall('GID[0-9]{9}', new_code)
        if new_ev.get('head'):
            head_id = re.findall('GID[0-9]{9}', new_ev.get('head'))
            if head_id == []:
                temp_new_evidences.append(new_ev)
            else:
                unknwon_evidences.append(new_ev)
        else:
            if code_ids == []:
                temp_new_evidences.append(new_ev)
            else:
                unknwon_evidences.append(new_ev)
        #print(new_ev.get('_id'), new_name, new_code)

    for upd_ev in update_evidences:

        original_head = upd_ev.get('head')
        if original_head:
            old_ids = re.findall('GID[0-9]{9}', original_head)
            new_head = original_head
            if old_ids is not []:
                for old_id in old_ids:
                    new_id = evidence_codes.get(old_id)
                    if new_id:
                        new_head = new_head.replace(old_id, new_id)
            upd_ev.update({'head': new_head})

    utils.create_json({'classAcronym': 'ECOLI', 'collectionName': 'evidences', 'organism': 'ECOLI',
                      'subClassAcronym': 'EVC', 'collectionData': temp_new_evidences}, new_evidences_filename)
    utils.create_json({'classAcronym': 'ECOLI', 'collectionName': 'evidences', 'organism': 'ECOLI',
                      'subClassAcronym': 'EVC', 'collectionData': update_evidences}, update_evidences_filename)
    utils.create_json({'classAcronym': 'ECOLI', 'collectionName': 'evidences', 'organism': 'ECOLI',
                      'subClassAcronym': 'EVC', 'collectionData': unknwon_evidences}, unknwon_evidences_filename)
