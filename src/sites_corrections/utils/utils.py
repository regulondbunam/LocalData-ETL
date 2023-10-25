import os
import json
import logging
import csv

import pymongo

import identifiers_api as id_api


def set_log(log_path, log_name="sites.log"):
    if not os.path.isdir(log_path):
        raise IOError(
            "{} directory does not exist, please edit your log argument value".format(log_path))
    log_path = os.path.join(log_path, log_name)
    logging.basicConfig(filename=log_path,
                        format='%(levelname)s - %(asctime)s - %(message)s', filemode='w', level=logging.INFO)
    return log_path


def updater(sites, collection):
    modified_documents = 0
    for site in sites:
        query = {"_id": site.get('_id')}
        formatted_new_values = {
            "$set": {
                'length': site.get('length'),
                'leftEndPosition': site.get('left'),
                'rightEndPosition': site.get('right'),
                'sequence': site.get('sequence'),
            }
        }
        modified_documents += collection.update_one(
            query, formatted_new_values).modified_count
    print(f'{modified_documents} documents updated')


def get_only_properties_with_values(properties):
    properties = {key: value for key, value in properties.items() if value}
    return properties


def get_sites_from_csv_file(file_name, pt_connection, collection):
    sites = []
    with open(f'{file_name}', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            site_id = row.get('SITE_ID', None)
            site_length = int(row.get('SITE_LENGTH', None))
            query = {"_id": site_id}
            mg_site = collection.find_one(query)
            site_absolute_pos = mg_site.get('absolutePosition')
            left = site_absolute_pos - int(site_length / 2)
            right = site_absolute_pos + int(site_length / 2)

            sequence = get_sequence(
                left_end_position=left,
                right_end_position=right,
                pt_connection=pt_connection
            )
            print(site_id, mg_site.get('absolutePosition'), left, right, sequence)
            site = {
                '_id': site_id,
                'length': site_length,
                'left': int(left),
                'right': int(right),
                'sequence': sequence,
            }
            if site not in sites:
                sites.append(site)
    return sites


def get_sequence(left_end_position, right_end_position, pt_connection, strand="forward", offset=10):
    sequence = None
    if left_end_position and right_end_position:
        # if we have an offset value then we proceed in a different form
        if offset is not None:
            # We add the offset to the positions
            lend = left_end_position - offset
            rend = right_end_position + offset
            # with the positions values modified by the offset we get the
            # sequence
            sequence = pt_connection.get_sequence(lend, rend, "X")
            sequence = sequence[:offset].lower() + sequence[offset:]
            sequence = sequence[: len(
                sequence) - offset] + sequence[-offset:].lower()
        else:
            sequence = pt_connection.get_sequence(
                left_end_position, right_end_position, "X")
        if strand == "reverse" and sequence is not None:
            sequence = pt_connection.get_reverse_complement(sequence)
    return sequence
