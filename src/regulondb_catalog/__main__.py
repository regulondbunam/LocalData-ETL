import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import multigenomic_api

from libs import utils
from libs import arguments
from libs import regulondb_catalog


def run(arguments):
    utils.set_log(arguments.log, "regulondb_evidence_catalog.log")
    print(f'Reading: \n\t{arguments.catalog}')
    regulondb_catalog.extract_process(
        arguments.catalog, arguments.new, arguments.update, arguments.unknwon, arguments.rules, arguments.url, arguments.database, arguments.organism)


if __name__ == '__main__':
    arguments = arguments.load()
    run(arguments)
