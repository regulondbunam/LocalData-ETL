import os
import itertools

import identifiers_api as id_api
import multigenomic_api as mg_api
import pymongo

from .utils import set_identifier_object
from libs import utils


def get_confidences(mg_objects, collection_name, mg_api, mg_db):
    updated_documents = 0
    for mg_object in mg_objects:
        object_id = mg_object.id
        object_citations = mg_object.citations
        confidence_levels = []
        confidence_level = None

        additive_evidences = utils.get_mg_objects_additive_evidences(
            mg_object.id,
            collection_name,
            mg_db
        )
        if additive_evidences is not None:
            for add_evidence in additive_evidences:
                add_ev_confidence_level = utils.get_mg_additive_evidences(
                    add_evidence, "additiveEvidences", mg_db)
                if add_ev_confidence_level:
                    confidence_levels.append(add_ev_confidence_level)

        else:
            if collection_name == 'regulatoryInteractions':
                ri_site = mg_object.regulatory_sites_id
                if ri_site:
                    '''mg_api.connect(kwargs.get('database', None),
                                   kwargs.get('url', None))'''
                    mg_site = mg_api.regulatory_sites.find_by_id(ri_site)
                    site_citations = mg_site.citations
                    if site_citations:
                        object_citations.extend(site_citations)
                    # mg_api.disconnect()
            for citation in object_citations:
                if citation.evidences_id is not None:
                    mg_evidence = mg_api.evidences.find_by_id(
                        citation.evidences_id)
                    if mg_evidence.type:
                        confidence_levels.append(mg_evidence.type)

        confidence_level = utils.set_confidence_level(confidence_levels)

        if confidence_levels:
            # update
            updated_documents += 1
            mg_collection = mg_db[collection_name]
            utils.updater(object_id, confidence_level, mg_collection)
            # print(f'{collection_name} : {object_id}')
            #print(f'confidenceLevel: {confidence_level}, {confidence_levels}')
    print(
        f'\tTotal of {collection_name} updated {updated_documents} of {len(mg_objects)}')


def get_additive_evidences_ids(url, collection_name, organism, ontology_name=None):
    id_api.connect(url)
    collection_identifiers = id_api.regulondbmultigenomic.get_identifiers_by(
        type=collection_name,
        ontology_name=ontology_name,
        organism=organism
    )
    id_api.disconnect()
    return collection_identifiers


def additive_evidences(mg_objects, mg_collection_name, ae_collection, rules, mg_db, **kwargs):
    # print(collection_identifiers)
    collection_identifiers = get_additive_evidences_ids(
        kwargs.get('url', None), ae_collection, kwargs.get('organism'))
    objs_w_ae = 0
    for mg_object in mg_objects:
        print(f'Working on object {mg_object.id}')
        additive_evidence_ids_list = []
        additive_evidence_list = []
        object_citations = mg_object.citations
        evidences = []
        mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
        for citation in object_citations:
            if citation.evidences_id is not None:
                mg_evidence = mg_api.evidences.find_by_id(
                    citation.evidences_id)
                if mg_evidence.cv_code_rule:
                    evidence = {
                        '_id': mg_evidence.id,
                        'code': mg_evidence.code,
                        'rule': mg_evidence.cv_code_rule
                    }
                    evidences.append(evidence)
        mg_api.disconnect()
        if mg_collection_name == 'regulatoryInteractions':
            ri_site = mg_object.regulatory_sites_id
            if ri_site:
                mg_api.connect(kwargs.get('database', None),
                               kwargs.get('url', None))
                mg_site = mg_api.regulatory_sites.find_by_id(ri_site)
                site_citations = mg_site.citations
                for citation in site_citations:
                    if citation.evidences_id is not None:
                        mg_evidence = mg_api.evidences.find_by_id(
                            citation.evidences_id)
                        if mg_evidence.cv_code_rule:
                            evidence = {
                                '_id': mg_evidence.id,
                                'code': mg_evidence.code,
                                'rule': mg_evidence.cv_code_rule
                            }
                            evidences.append(evidence)
                mg_api.disconnect()

        ev_rules = []
        acepted_rules = []
        additive_rules = []

        for ev in evidences:
            if ev.get('rule') not in ev_rules:
                ev_rules.append(ev.get('rule'))
        temp_rules = []
        temp_acept_rules = []
        if ev_rules:
            for rule in rules:
                if any(item in rule.get('rules_values') for item in ev_rules):
                    additive_rules.append(rule)
                temp_rules.append(rule.get('rules_values'))
                '''if all(item in ev_rules for item in rule.get('rules_values')):
                    additive_rules.append(rule)'''
            # aev_rules.append(rule.get('rules_values'))
        for aev_rule in additive_rules:
            if all(item in ev_rules for item in aev_rule.get('rules_values')):
                acepted_rules.append(aev_rule)
                temp_acept_rules.append(aev_rule.get('rules_values'))
        # print('EV_RULES', ev_rules)
        '''if acepted_rules != []:
            print('TEMP_RULES', temp_rules)
            print('TEMP_ACEPT_RULES', temp_acept_rules)'''
        # print('ADEV_RULES', acepted_rules)
        # print(ev_rules, aev_rules)
        if acepted_rules:
            # print('EV_Rules: ', ev_rules, ' AEV_Rules: ', acepted_rules)
            additive_evidence_list.extend(build_additive_evidence(
                acepted_rules, evidences))
            # print('AE_List: ', additive_evidence_list)

            objs_w_ae += len(additive_evidence_list)

        # Generar AE_ID
        # Armar el IDObj
        if additive_evidence_list != []:
            # print(len(additive_evidence_list))
            for additive_evidence in additive_evidence_list:
                # si hay identifiers y si hay uno con el mismo code se usara ese como el id del AE sino se dejara el proceso existente.
                existing_id = exist_on_identifiers('regulondbidentifiers', kwargs.get(
                    'url', None), additive_evidence.get('_id', None))
                if not existing_id:
                    metadata_properties = {}
                    metadata_properties["classAcronym"] = kwargs.get(
                        'organism', None)
                    metadata_properties["subClassAcronym"] = 'AEC'
                    metadata_properties["ontologyName"] = kwargs.get(
                        'ontologyName', None)
                    metadata_properties["organism"] = kwargs.get(
                        'organism', None)
                    metadata_properties["regulondbReleaseVersion"] = kwargs.get(
                        'version', None)
                    metadata_properties["uniqueDataString"] = None
                    metadata_properties["database"] = kwargs.get(
                        'database', None)
                    metadata_properties["sourceDBName"] = kwargs.get(
                        'source', None)
                    metadata_properties["sourceDBVersion"] = kwargs.get(
                        'sourceversion', None)
                    metadata_properties["type"] = 'additiveEvidences'

                    id_object = set_identifier_object(additive_evidence,
                                                      'additiveEvidences', **metadata_properties)
                    # print(id_object)
                    handle_id(id_object, collection_identifiers,
                              kwargs.get('url', None))
                    new_collection_identifiers = get_additive_evidences_ids(
                        kwargs.get('url', None), ae_collection, kwargs.get('organism'))
                    new_id = new_collection_identifiers[additive_evidence.get(
                        '_id')]
                else:
                    new_id = existing_id
                additive_evidence.update({'_id': new_id})
                if new_id not in additive_evidence_ids_list:
                    additive_evidence_ids_list.append(new_id)
            # print('Final_AE: ', additive_evidence_list,
            #      additive_evidence_ids_list)

            # Subir AE a mongo
            utils.ae_uploader(
                additive_evidence_list,
                ae_collection,
                mg_db
            )
            # Actualizar el obj con su AE
            utils.ae_updater(
                mg_object.id,
                additive_evidence_ids_list,
                mg_collection_name,
                mg_db
            )
        else:
            pass
            # print(f'No AE for {object_id}')

    print('Objects with Additive Evidences', objs_w_ae)


def exist_on_identifiers(database, url, temp_id):
    mongo_client = pymongo.MongoClient(url)
    db = mongo_client[database]
    collection = db["identifiers"]
    query = {"objectOriginalSourceId": temp_id}
    id_obj = collection.find_one(query)
    if id_obj is None:
        print('no existe', temp_id)
        return None
    else:
        return id_obj.get('_id', None)


def handle_id(identifier_object, collection_registered_identifiers, url):
    # if the identifier already exists, we will updated its
    # lastRegulonDBVersionUsed field
    id_api.connect(url)
    if identifier_object is not None:
        if identifier_object["_id"] in collection_registered_identifiers:
            object_id = collection_registered_identifiers[identifier_object["_id"]]
            last_regulondb_version_used = identifier_object["lastRegulonDBReleaseUsed"]
            id_api.update_id(object_id, last_regulondb_version_used)
        # otherwise we create a new RegulonDB Identifier
        else:
            # print(f'Creating ID :{identifier_object.get("_id")}')
            id_api.create_id(identifier_object)
    id_api.disconnect()


def get_all_rules_combination(rule, evidences):
    rule_dict = {}
    rule_list = []
    # print(rule.get("rules_values", None))
    for code in rule.get("rules_values", None):
        for ev in evidences:
            if ev.get('rule', None) == code:
                rule_dict.setdefault(f"{code}", []).append(ev)
    # print('rule_dict', rule_dict)
    for code in rule.get("rules_values", None):
        # print(code)
        rule_list.append(rule_dict.get(f"{code}"))
    # print('rule_list', rule_list, list(itertools.product(*rule_list)))
    return list(itertools.product(*rule_list))

# TODO: No used?


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic.get(key, None) == value:
            return dic
    return -1


def build_additive_evidence(rules, evidences):
    additive_rules = []
    for rule in rules:
        rules_comb = get_all_rules_combination(rule, evidences)
        for i in rules_comb:
            code = ""
            codes = []
            ev_ids = []
            for v in i:
                ev_ids.append(v.get('_id'))
                code = code + v.get("code", None) + "/"
                codes.append(v.get('rule', None))
            rule = find(rules, "rules_values", codes)
            ae_dict = {
                "_id": f"AE_ID({code[:-1]})",
                "code": f"AE({code[:-1]})",
                "confidenceLevel": rule.get("type", None),
                "category": rule.get("evidenceCategory", None),
                "pertainsTo": rule.get("pertainsTo"),
                "rules": rule.get("rules_values"),
                "evidenceIds": ev_ids
            }
            # print('ev_ids: ', ev_ids)
            # print('ae_dict', ae_dict)
            additive_rules.append(ae_dict)
    # additive_rules = list({v['_id']: v for v in additive_rules}.values())
    return additive_rules


def promoters_confidences(mg_db, rules, **kwargs):
    collection_name = 'promoters'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.promoters.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def transcription_factors_confidences(mg_db, rules, **kwargs):
    collection_name = 'transcriptionFactors'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.transcription_factors.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def transcription_units_confidences(mg_db, rules, **kwargs):
    collection_name = 'transcriptionUnits'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.transcription_units.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def genes_confidences(mg_db, rules, **kwargs):
    collection_name = 'genes'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.genes.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def products_confidences(mg_db, rules, **kwargs):
    collection_name = 'products'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.products.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def regulatory_complexes_confidences(mg_db, rules, **kwargs):
    collection_name = 'regulatoryComplexes'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.regulatory_complexes.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def regulatory_continuants_confidences(mg_db, rules, **kwargs):
    collection_name = 'regulatoryContinuants'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.regulatory_continuants.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def regulatory_interactions_confidences(mg_db, rules, **kwargs):
    collection_name = 'regulatoryInteractions'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.regulatory_interactions.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def regulatory_sites_confidences(mg_db, rules, **kwargs):
    collection_name = 'regulatorySites'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.regulatory_sites.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def segments_confidences(mg_db, rules, **kwargs):
    collection_name = 'segments'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.segments.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def sigma_factors_confidences(mg_db, rules, **kwargs):
    collection_name = 'sigmaFactors'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.sigma_factors.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()


def terminators_confidences(mg_db, rules, **kwargs):
    collection_name = 'terminators'
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    mg_objects = mg_api.terminators.get_all()
    mg_api.disconnect()
    additive_evidences(mg_objects, collection_name,
                       'additiveEvidences', rules, mg_db, **kwargs)
    mg_api.connect(kwargs.get('database', None), kwargs.get('url', None))
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
    mg_api.disconnect()
