import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import multigenomic_api

from libs import utils
from libs import arguments
from libs import regulondb_catalog


def run(arguments):
    multigenomic_api.connect(arguments.database, arguments.url)
    utils.set_log(arguments.log, "regulondb_evidence_catalog.log")
    regulondb_catalog.extract_process(
        arguments.catalog, arguments.new, arguments.update, arguments.unknwon)


if __name__ == '__main__':
    arguments = arguments.load()
    run(arguments)
