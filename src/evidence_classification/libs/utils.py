import os


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


def updater(mg_object_id, confidence_level, collection):
    new_values = {}
    new_values.setdefault("confidenceLevel", confidence_level)

    query = {"_id": mg_object_id}
    formatted_new_values = {
        "$set": new_values
    }

    collection.update_one(query, formatted_new_values)
