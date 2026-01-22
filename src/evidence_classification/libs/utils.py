import os
import logging
import pymongo

from domain.additive_evidence import additive_evidence


def set_confidence_level(confidence_levels):
    confidence_level = None
    if 'W' in confidence_levels:
        confidence_level = 'W'
    if 'S' in confidence_levels and 'C' not in confidence_levels:
        confidence_level = 'S'
    if 'S' in confidence_levels and 'W' not in confidence_levels and 'C' not in confidence_levels:
        confidence_level = 'S'
    if 'C' in confidence_levels:
        confidence_level = 'C'
    return confidence_level


def get_mg_objects_additive_evidences(mg_object_id, collection_name, mg_db):
    collection = mg_db[collection_name]
    mg_object = collection.find_one(mg_object_id)
    if mg_object:
        additive_evidences = mg_object.get("additiveEvidences")
        # if additive_evidences:
        # print(additive_evidences)
        return additive_evidences
    else:
        return None


def get_mg_additive_evidences(mg_object_id, collection_name, mg_db):
    collection = mg_db[collection_name]
    mg_object = collection.find_one(mg_object_id)
    if mg_object:
        ae_set_confidence_level = mg_object.get("confidenceLevel")
        # print(ae_set_confidence_level)
        return ae_set_confidence_level
    else:
        return None


def updater(mg_object_id, confidence_level, collection):
    new_values = {}
    new_values.setdefault("confidenceLevel", confidence_level)

    query = {"_id": mg_object_id}
    formatted_new_values = {
        "$set": new_values
    }

    collection.update_one(query, formatted_new_values)


def ae_updater(mg_object_id, additive_evidences, collection_name, mg_db):
    collection = mg_db[collection_name]

    new_values = {}
    new_values.setdefault("additiveEvidences", additive_evidences)

    query = {"_id": mg_object_id}
    formatted_new_values = {
        "$set": new_values
    }
    # print(collection_name, " : ", new_values)
    collection.update_one(query, formatted_new_values)


def ae_uploader(additive_evidences, collection_name, mg_db):
    collection = mg_db[collection_name]
    for ae_evidence in additive_evidences:
        ae_evidence_id = ae_evidence.get('_id', None)
        ae_evidence_code = ae_evidence.get('code', None)
        ae_evidence_category = ae_evidence.get('category', None)
        ae_evidence_confidence_level = ae_evidence.get('confidenceLevel', None)
        ae_evidence_pertains_to = ae_evidence.get('pertainsTo', None)
        ae_evidence_rules = ae_evidence.get('rules', None)
        ae_evidence_evidences_ids = ae_evidence.get('evidenceIds', None)

        new_values = {}
        if ae_evidence_id:
            new_values.setdefault("_id", ae_evidence_id)
        if ae_evidence_code:
            new_values.setdefault("code", ae_evidence_code)
        if ae_evidence_category:
            new_values.setdefault("category", ae_evidence_category)
        if ae_evidence_confidence_level:
            new_values.setdefault(
                "confidenceLevel", ae_evidence_confidence_level)
        if ae_evidence_pertains_to:
            new_values.setdefault("pertainsTo", ae_evidence_pertains_to)
        if ae_evidence_rules:
            new_values.setdefault("rules", ae_evidence_rules)
        if ae_evidence_evidences_ids:
            new_values.setdefault("evidenceIds", ae_evidence_evidences_ids)

        # print(new_values)
        try:
            collection.insert_one(new_values)
            pass
        except pymongo.errors.DuplicateKeyError:
            pass
            # logging.error(f'"{ae_evidence_id}" is already in RegulonDB.')


def build_identifier_object(object_id, **kwargs):
    identifier = {
        "_id": object_id,
        "classAcronym": kwargs.get("classAcronym", None),
        "createdOnRegulonDBRelease": kwargs.get("regulondbReleaseVersion", None),
        "lastRegulonDBReleaseUsed": kwargs.get("regulondbReleaseVersion", None),
        "objectOriginalSourceId": object_id,
        "ontologyName": kwargs.get("ontologyName", None),
        "organism": kwargs.get("organism", None),
        "propertiesToMakeId": kwargs.get("uniqueDataString", None),
        "regulondbDatabase": kwargs.get("database", None),
        "sourceDBName": kwargs.get("sourceDBName", None),
        "sourceDBVersion": kwargs.get("sourceDBVersion", None),
        "subClassAcronym": kwargs.get("subClassAcronym", None),
        "type": kwargs.get("type", None)
    }

    return identifier


get_unique_data = {
    "additiveEvidences": additive_evidence
}


def remove_organism_property_from(identifier_object):
    if identifier_object["type"] in ["ontologies", "term"]:
        identifier_object["organism"] = None


def set_identifier_object(json_object, collection_name, **metadata_properties):
    # print(collection_name)
    # if collection_name not in ["ontologies", "terms"] else "ontologies"
    if collection_name == "segments":
        return None
    metadata_properties["type"] = collection_name
    metadata_properties["uniqueDataString"] = get_unique_data[collection_name](
        **json_object)

    object_id = json_object["_id"]

    identifier_object = build_identifier_object(
        object_id, **metadata_properties)
    remove_organism_property_from(identifier_object)

    return identifier_object
