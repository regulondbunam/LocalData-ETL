import argparse


def load():
    parser = argparse.ArgumentParser(description="Data updater/uploader, it will take the _id field as the field to get the object to update or to upload new evidences",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-d", "--directory",
        help="Directory where the json files are located",
        default="../RawData/EvidenceCatalog"
    )

    parser.add_argument(
        "-db", "--database",
        help="Directory with the evidences to update",
        default="regulondbmultigenomic",
        metavar="regulondbmultigenomic"
    )

    parser.add_argument(
        "-i", "--input-file",
        help="JSON input file to process",
        required=False
    )

    parser.add_argument(
        "-l", "--log",
        help="Directory that contains log of the invalid data, the reason why the data is being rejected.",
        default="../logs/EvidenceCatalog/"
    )

    parser.add_argument(
        "-u", "--url",
        help="URL to establish a connection between the process and MongoDB",
        default="mongodb://localhost:27017/",
        metavar="mongodb://localhost:27017/"
    )

    parser.add_argument(
        "-upd",
        "--update",
        help="Sets the program to update existing evidences",
        default="../RawData/EvidenceCatalog/update_evidences.json"
    )

    parser.add_argument(
        "-upl",
        "--upload",
        help="Sets the program to upload new evidences",
        default="../RawData/EvidenceCatalog/new_evidences.json"
    )

    arguments = parser.parse_args()

    return arguments
