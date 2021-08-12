import os

from libs import utils


def get_confidences(mg_objects, collection_name, mg_api, mg_db):
    updated_documents = 0
    for mg_object in mg_objects:
        object_id = mg_object.id
        object_citations = mg_object.citations
        confidence_levels = []
        confidence_level = None
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
            # print(f'confidenceLevel: {confidence_level}, {confidence_levels}')
    print(
        f'\tTotal of {collection_name} updated {updated_documents} of {len(mg_objects)}')


def promoters_confidences(mg_api, mg_db):
    mg_objects = mg_api.promoters.get_all()
    collection_name = 'promoters'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def transcription_factors_confidences(mg_api, mg_db):
    mg_objects = mg_api.transcription_factors.get_all()
    collection_name = 'transcriptionFactors'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def transcription_units_confidences(mg_api, mg_db):
    mg_objects = mg_api.transcription_units.get_all()
    collection_name = 'transcriptionUnits'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def genes_confidences(mg_api, mg_db):
    mg_objects = mg_api.genes.get_all()
    collection_name = 'genes'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def products_confidences(mg_api, mg_db):
    mg_objects = mg_api.products.get_all()
    collection_name = 'products'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def regulatory_complexes_confidences(mg_api, mg_db):
    mg_objects = mg_api.regulatory_complexes.get_all()
    collection_name = 'regulatoryComplexes'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def regulatory_continuants_confidences(mg_api, mg_db):
    mg_objects = mg_api.regulatory_continuants.get_all()
    collection_name = 'regulatoryContinuants'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def regulatory_interactions_confidences(mg_api, mg_db):
    mg_objects = mg_api.regulatory_interactions.get_all()
    collection_name = 'regulatoryInteractions'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def regulatory_sites_confidences(mg_api, mg_db):
    mg_objects = mg_api.regulatory_sites.get_all()
    collection_name = 'regulatorySites'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def segments_confidences(mg_api, mg_db):
    mg_objects = mg_api.segments.get_all()
    collection_name = 'segments'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def sigma_factors_confidences(mg_api, mg_db):
    mg_objects = mg_api.sigma_factors.get_all()
    collection_name = 'sigmaFactors'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)


def terminators_confidences(mg_api, mg_db):
    mg_objects = mg_api.terminators.get_all()
    collection_name = 'terminators'
    get_confidences(mg_objects, collection_name, mg_api, mg_db)
