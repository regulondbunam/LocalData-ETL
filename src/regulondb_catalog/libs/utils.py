import os
import logging
import json


def set_log(log_path, log_name="evidence.log"):
    if not os.path.isdir(log_path):
        raise IOError(
            "{} directory does not exist, please edit your log argument value".format(log_path))
    log_path = os.path.join(log_path, log_name)
    logging.basicConfig(filename=log_path,
                        format='%(levelname)s - %(asctime)s - %(message)s', filemode='w', level=logging.INFO)
    return log_path


def create_json(data, filename):
    if filename[-5:] != ".json":
        filename = "{}.json".format(filename)
    with open(filename, 'w') as fn:
        json.dump(data, fn, indent=2)
    print(f'JSON file created at: \n\t{filename}')
