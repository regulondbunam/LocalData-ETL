import argparse


def load():
    parser = argparse.ArgumentParser(description="Data updater/uploader, it will take the _id field as the field to get the object to update or to upload new evidences",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-org",
        "--organism",
        help="Organism whose information is been downloaded.",
        default="ECOLI",
        metavar="ecoli",
    )

    parser.add_argument(
        "-d", "--directory",
        help="Directory where the json files are located",
        default="../RawData/Regulators/"
    )

    parser.add_argument(
        "-db", "--database",
        help="Directory with the evidences to update",
        default="regulondbmultigenomic",
        metavar="regulondbmultigenomic"
    )

    parser.add_argument(
        "-l", "--log",
        help="Directory that contains log of the invalid data, the reason why the data is being rejected.",
        default="../logs/Regulators"
    )

    parser.add_argument(
        "-u", "--url",
        help="URL to establish a connection between the process and MongoDB",
        default="mongodb://localhost:27017/",
        metavar="mongodb://localhost:27017/"
    )

    arguments = parser.parse_args()

    return arguments
