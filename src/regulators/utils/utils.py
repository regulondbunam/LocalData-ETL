import os
import sys
# import json
import logging

import pymongo

import identifiers_api as id_api


def set_log(log_path, log_name="regulators.log"):
    if not os.path.isdir(log_path):
        raise IOError(
            f"{log_path} directory does not exist, please edit your log argument value")
    log_path = os.path.join(log_path, log_name)
    logging.basicConfig(
        filename=log_path,
        format='%(levelname)s - %(asctime)s - %(message)s',
        filemode='w',
        level=logging.INFO)
    return log_path


def updater(regulators, collection):
    for regulator in regulators:
        query = {"_id": regulator.get('_id')}
        formatted_new_values = {
            "$set": regulator
        }
        collection.update_one(query, formatted_new_values)


def uploader(regulators, collection):
    for regulator in regulators:
        try:
            collection.insert_one(regulator)
        except pymongo.errors.DuplicateKeyError:
            logging.error(f'"{regulator.get("_id")}" is already in RegulonDB.')


def get_only_properties_with_values(properties):
    properties = {key: value for key, value in properties.items() if value}
    return properties


def get_cyc_ids(url, collection_name, ontology_name, organism):
    id_api.connect(url)
    collection_identifiers = id_api.regulondbmultigenomic.get_identifiers_by(
        type=collection_name,
        ontology_name=ontology_name,
        organism=organism
    )
    id_api.disconnect()
    return collection_identifiers


def get_cyc_id_by_rdb_id(rdb_id, cyc_ids):
    cyc_id = list(cyc_ids.keys())[list(cyc_ids.values()).index(rdb_id)]
    return cyc_id


def print_progress(current, total, collection_name, bar_length=40):
    """
    Displays a real-time progress bar in the console, updating on the same line.

    This function calculates the completion fraction, generates a visual progress
    bar using block characters, and outputs the progress percentage and current
    count relative to the total.

    Args:
        current (int): The number of items currently processed.
        total (int): The total number of items to be processed.
        collection_name (str): The name of the collection or process being tracked.
        bar_length (int, optional): The fixed length of the progress bar display.
                                    Defaults to 40.

    Returns:
        None: The function only performs output to stdout.
    """
    fraction = current / total if total else 1
    filled = int(bar_length * fraction)
    bar = "█" * filled + "-" * (bar_length - filled)
    percent = int(fraction * 100)
    sys.stdout.write(f"\rProcessing {collection_name}: |{bar}| {percent}% ({current}/{total}) objects processed")
    sys.stdout.flush()