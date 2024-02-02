import argparse


def load():
    parser = argparse.ArgumentParser(description="Analytical cross-validation is an active evaluation of confidence and integrates multiple evidence by combining independent types of evidence, with the intention to confirm individual objects and mutually exclude false positives. It follows the same principles of science as applied by wet-lab scientists, where data are confirmed by repetitions on the one hand, and by additional experimental strategies to exclude alternative explanations on the other.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-d", "--directory",
        help="Directory where the json files are located",
        default="../InputData/HT_RIs/DatasetsTFBSRegulonDB12.0/"
    )

    parser.add_argument(
        "-db", "--database",
        help="Data base name",
        default="regulondbmultigenomic",
        metavar="regulondbmultigenomic"
    )

    parser.add_argument(
        "-iddb", "--id-database",
        help="IDs data base name",
        default="regulondbidentifiers",
        metavar="regulondbidentifiers"
    )

    parser.add_argument(
        "-u", "--url",
        help="URL to establish a connection between the process and MongoDB",
        default="mongodb://localhost:27017/",
        metavar="mongodb://localhost:27017/"
    )

    parser.add_argument(
        "-l", "--log",
        help="Directory that contains log of the invalid data, the reason why the data is being rejected.",
        default="../logs/ht_ris_log/"
    )

    parser.add_argument(
        "-r", "--rules",
        help="The evidence rules file",
        default="../RawData/EvidenceCatalog/Rules/evidences_rules.json",
    )

    arguments = parser.parse_args()

    return arguments
