import logging
import re
from typing import Any, Dict, List, Optional

import multigenomic_api
import identifiers_api

from regulondb_catalog.libs import utils
from regulondb_catalog.libs import evidence_catalog_utils

# Globals (kept for backward compatibility)
evidence_codes: Dict[str, str] = {}
new_evidence_codes: Dict[str, str] = {}  # unused but kept to avoid breaking imports
unknwon_ids: List[str] = []             # unused but kept to avoid breaking imports

EV_COLLECTION = "evidences"

# Precompiled regex patterns
GID_PATTERN = re.compile(r"GID[0-9]{9}")
RDB_PATTERN = re.compile(r"RDB[A-Z]{7}[0-9]{5}")


def get_evidences_ids(
    url: str,
    database: str,
    organism: str,
    collection: str
) -> Dict[str, str]:
    """
    Generates an evidence Original IDs dictionary.

    Params:
        - url: Database URL.
        - database: Database name.
        - organism: Organism.
        - collection: Collection to extract IDs.

    Returns:
        - original_ids: Original IDs dictionary.
    """
    identifiers_api.connect(url)
    try:
        original_ids = identifiers_api.get_identifiers(collection, database, organism)
    finally:
        identifiers_api.disconnect()
    return original_ids


def evidence_obj_builder(evidence_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the evidence dictionary object with all metadata necessary in the process.

    Params:
        - evidence_dict: Evidence dictionary from Excel file.

    Returns:
        - evidence_obj: Evidence object with all metadata.
    """
    ev_type = evidence_dict.get("EVIDENCE_TYPE")
    if isinstance(ev_type, str):
        ev_type = ev_type.strip()

    type_obj = evidence_dict.get("TYPE_OBJECT")
    if type_obj:
        if "|" in type_obj:
            type_obj = type_obj.split("|")
        if "," in type_obj:
            type_obj = type_obj.split(",")
        if isinstance(type_obj, str):
            type_obj = [type_obj]

    ev_code_rule = evidence_dict.get("CV_NUMBER_RULE")
    if ev_code_rule:
        ev_code_rule = int(ev_code_rule)

    evidence_obj = {
        "_id": evidence_dict.get("EVIDENCE_ID"),
        "cyc_id": evidence_dict.get("ECOCYC_ID"),
        "status": evidence_dict.get("STATUS"),
        "type": ev_type,
        "head": evidence_dict.get("HEAD"),
        "pertainsTo": type_obj,
        "code": evidence_dict.get("EVIDENCE_CODE"),
        "name": evidence_dict.get("EVIDENCE_NAME"),
        "note": evidence_dict.get("EVIDENCE_NOTE"),
        "internalComent": evidence_dict.get("EVIDENCE_INTERNAL_COMMENT"),
        "crossEvidenceCodeRule": ev_code_rule,
        "evidenceCategory": evidence_dict.get("EVIDENCE_CATEGORY"),
        "noteWeb": evidence_dict.get("EVIDENCE_NOTE_WEB"),
        "evidenceApproach": evidence_dict.get("EVIDENCE_APPROACH"),
        "class": evidence_dict.get("CLASS"),
    }
    return evidence_obj


def evidence_doc_builder(evidence_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the evidence document that is going to be inserted in the json file.

    Params:
        - evidence_obj: Evidence object with all metadata.

    Returns:
        - evidence_document: Evidence object with only necessary data for database.
    """
    evidence_document = {
        "_id": evidence_obj.get("_id"),
        "code": evidence_obj.get("code"),
        "head": evidence_obj.get("head"),
        "internalComent": evidence_obj.get("internalComent"),
        "name": evidence_obj.get("name"),
        "note": evidence_obj.get("note"),
        "pertainsTo": evidence_obj.get("pertainsTo"),
        "type": evidence_obj.get("type"),
        "class": evidence_obj.get("class"),
        "crossEvidenceCodeRule": evidence_obj.get("crossEvidenceCodeRule"),
        "evidenceCategory": evidence_obj.get("evidenceCategory"),
        "evidenceApproach": evidence_obj.get("evidenceApproach"),
        "noteWeb": evidence_obj.get("noteWeb"),
    }
    return evidence_document


def evidence_rule_builder(evidence_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates the evidence rules dictionaries objects with all metadata necessary
    in the Datamarts process.

    Params:
        - evidence_obj: Evidence object with all metadata.

    Returns:
        - evidence_rule_obj: Evidence rule object.
    """
    name = evidence_obj.get("name")
    if not name:
        evidence_rule_values: List[int] = []
    else:
        inside_parentheses = name[name.find("(") + 1 : name.find(")")]
        parts = inside_parentheses.split("/")
        evidence_rule_values = [int(x) for x in parts] if parts else []

    evidence_rule_obj = {
        "rules_values": evidence_rule_values,
        "type": evidence_obj.get("type"),
        "pertainsTo": evidence_obj.get("pertainsTo"),
        "evidenceCategory": evidence_obj.get("evidenceCategory"),
    }
    return evidence_rule_obj


def _find_mg_evidence(
    ev_rdb_id: Optional[str],
    ev_code: Optional[str],
    ev_id: Optional[str],
    url: str,
    database: str,
) -> Optional[Any]:
    """
    Try to find the evidence in multigenomic in three steps:
    1. by original ID (ev_rdb_id)
    2. by code (EV-{code})
    3. by _id (ev_id)

    Logic is kept identical, only the connection handling is centralized.
    """
    multigenomic_api.connect(database, url)
    try:
        mg_evidence = None
        # 1) by original ID
        if ev_rdb_id:
            try:
                mg_evidence = multigenomic_api.evidences.find_by_id(ev_rdb_id)
            except Exception:
                mg_evidence = None

        # 2) by EV-code
        if not mg_evidence and ev_code:
            try:
                mg_evidence = multigenomic_api.evidences.find_by_code(f"EV-{ev_code}")
            except Exception:
                mg_evidence = None

        # 3) by _id
        if not mg_evidence and ev_id:
            try:
                mg_evidence = multigenomic_api.evidences.find_by_id(ev_id)
            except Exception:
                mg_evidence = None

        return mg_evidence

    finally:
        multigenomic_api.disconnect()


def append_update_ecocyc_evidence(
    evidence_obj: Dict[str, Any],
    update_evidences: List[Dict[str, Any]],
    unknown_evidences: List[Dict[str, Any]],
    url: str,
    database: str,
    evidence_original_ids: Dict[str, str],
) -> None:
    """
    Insert evidences to update or unknown in their lists.

    Params:
        - evidence_obj: Evidence object with all metadata.
        - update_evidences: Evidences to update list.
        - unknown_evidences: Unknown evidences list.
        - url: Database URL.
        - database: Database name.
        - evidence_original_ids: Original IDs dictionary.
    """
    ev_code = evidence_obj.get("code")
    ev_cyc_id = evidence_obj.get("cyc_id")
    ev_rdb_id = evidence_original_ids.get(f"|{ev_cyc_id}|")
    ev_id = evidence_obj.get("_id")

    try:
        mg_evidence = _find_mg_evidence(ev_rdb_id, ev_code, ev_id, url, database)
    except Exception:
        print(f'Problem Querying >  {ev_id} : {ev_code} : {evidence_obj.get("name")}')
        mg_evidence = None

    if mg_evidence:
        evidence_codes[ev_id] = ev_code  # type: ignore[index]
        evidence_obj["_id"] = mg_evidence.id
        update_evidence = evidence_doc_builder(evidence_obj)
        update_evidences.append(update_evidence)
    else:
        logging.critical(
            f"Evidence {ev_id} {ev_code} is not registered in RegulonDBMultigenomic, "
            f"please check this out, inconsistencies might be presented."
        )
        if ev_id and ev_code:
            evidence_codes[ev_id] = ev_code
        # keep original _id for unknown evidences
        unknown_evidence = evidence_doc_builder(evidence_obj)
        unknown_evidences.append(unknown_evidence)


def _replace_ids_in_text(
    text: Optional[str],
    pattern: re.Pattern,
    codes_map: Dict[str, str],
) -> Optional[str]:
    """
    Replace occurrences of IDs in a text according to a pattern and a mapping.

    Logic mimics:
        old_ids = re.findall(pattern, text)
        new_text = text
        if old_ids is not []:
            for old_id in old_ids:
                new_id = evidence_codes.get(old_id)
                if new_id:
                    new_text = new_text.replace(old_id, new_id)
    """
    if not text:
        return text

    old_ids = pattern.findall(text)
    if not old_ids:
        return text

    new_text = text
    for old_id in old_ids:
        new_id = codes_map.get(old_id)
        if new_id:
            new_text = new_text.replace(old_id, new_id)

    return new_text


def extract_process(
    catalog_evidences_filename: str,
    new_evidences_filename: str,
    update_evidences_filename: str,
    unknown_evidences_filename: str,
    evidence_rules_filename: str,
    url: str,
    database: str,
    organism: str,
) -> None:
    """
    Manage the extraction, transformation and load of evidences json files.

    Params:
        - catalog_evidences_filename: Evidence catalog file name.
        - new_evidences_filename: New evidences catalog file name.
        - update_evidences_filename: Update evidences catalog file name.
        - unknown_evidences_filename: Unknown evidences catalog file name.
        - evidence_rules_filename: Evidences rules catalog file name.
        - url: Database URL.
        - database: Database name.
        - organism: Organism name.
    """
    evidence_original_ids = get_evidences_ids(url, database, organism, EV_COLLECTION)

    evidences_catalog = evidence_catalog_utils.get_evidences_catalog(
        catalog_evidences_filename
    )

    new_evidences: List[Dict[str, Any]] = []
    update_evidences: List[Dict[str, Any]] = []
    unknown_evidences: List[Dict[str, Any]] = []
    evidence_rules: List[Dict[str, Any]] = []

    # First pass: build evidence objects and sort them
    for evidence in evidences_catalog:
        evidence_obj = evidence_obj_builder(evidence)

        evidence_cyc_id = evidence_obj.get("cyc_id")
        evidence_status = evidence_obj.get("status")
        evidence_class = evidence_obj.get("class")

        if not evidence_status:
            continue

        status_lower = evidence_status.lower()
        class_lower = evidence_class.lower() if isinstance(evidence_class, str) else None

        if class_lower == "rule":
            evidence_rule_obj = evidence_rule_builder(evidence_obj)
            evidence_rules.append(evidence_rule_obj)
            continue

        # Only evidences with Ecocyc ID will be processed
        if status_lower == "update" and evidence_cyc_id:
            append_update_ecocyc_evidence(
                evidence_obj,
                update_evidences,
                new_evidences,  # keep original logic: pass new_evidences as "unknown_evidences" here
                url,
                database,
                evidence_original_ids,
            )
        elif status_lower == "new" and evidence_cyc_id:
            new_evidence = evidence_doc_builder(evidence_obj)
            new_evidences.append(new_evidence)

    # Second pass: adjust IDs in new evidences
    temp_new_evidences: List[Dict[str, Any]] = []
    for new_ev in new_evidences:
        if not new_ev.get("_id"):
            continue
        if new_ev.get("evidenceCategory") == "independent cross-validation":
            continue

        # Replace IDs in 'name' (GID)
        original_name = new_ev.get("name")
        new_name = _replace_ids_in_text(original_name, GID_PATTERN, evidence_codes)
        if new_name is not None:
            new_ev["name"] = new_name

        # Replace IDs in 'head' (RDB then GID, order preserved)
        original_head = new_ev.get("head")
        if original_head:
            head_after_rdb = _replace_ids_in_text(
                original_head, RDB_PATTERN, evidence_codes
            )
            head_after_gid = _replace_ids_in_text(
                head_after_rdb, GID_PATTERN, evidence_codes
            )
            if head_after_gid is not None:
                new_ev["head"] = head_after_gid

        # Replace IDs in 'code' (GID)
        original_code = new_ev.get("code")
        new_code = _replace_ids_in_text(original_code, GID_PATTERN, evidence_codes)
        if new_code is not None:
            new_ev["code"] = new_code

        # Classification into temp_new_evidences vs unknown_evidences
        code_ids = GID_PATTERN.findall(new_ev.get("code") or "")
        head_value = new_ev.get("head")
        if head_value:
            head_ids = GID_PATTERN.findall(head_value)
            if not head_ids:
                temp_new_evidences.append(new_ev)
            else:
                unknown_evidences.append(new_ev)
        else:
            if not code_ids:
                temp_new_evidences.append(new_ev)
            else:
                unknown_evidences.append(new_ev)

    # Third pass: clean heads in update_evidences
    for upd_ev in update_evidences:
        original_head = upd_ev.get("head")
        if not original_head:
            continue

        old_ids = GID_PATTERN.findall(original_head)
        if not old_ids:
            continue

        for old_id in old_ids:
            new_id = evidence_codes.get(old_id)
            if new_id is not None:
                upd_ev["head"] = new_id
            else:
                upd_ev["head"] = None

    base_metadata = {
        "classAcronym": "ECOLI",
        "collectionName": "evidences",
        "organism": "ECOLI",
        "subClassAcronym": "EVC",
    }

    utils.create_json(
        {**base_metadata, "collectionData": temp_new_evidences},
        new_evidences_filename,
    )
    utils.create_json(
        {**base_metadata, "collectionData": update_evidences},
        update_evidences_filename,
    )
    utils.create_json(
        {**base_metadata, "collectionData": unknown_evidences},
        unknown_evidences_filename,
    )

    utils.create_json(evidence_rules, evidence_rules_filename)
