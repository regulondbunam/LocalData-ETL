import argparse


def load():
    parser = argparse.ArgumentParser(description="Evidence RegulonDB Catalog ETL Process",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-c", "--catalog",
        help="Dataset with the evidences to be processed",
        default="../InputData/EvidenceCatalog/RegulonDB_Evidence_Catalog_v3.2.xlsx"
    )

    parser.add_argument(
        "-rc", "--remote-catalog",
        help="Dataset with the evidences to be processed from url",
        default="https://docs.google.com/spreadsheets/d/1EFwbIHntVgF7FxMVkWT-lpZzcRpx1Fyu/edit?usp=share_link&ouid=105816430825590805829&rtpof=true&sd=true",
        metavar="https://docs.google.com/spreadsheets/d/1EFwbIHntVgF7FxMVkWT-lpZzcRpx1Fyu/edit?usp=share_link&ouid=105816430825590805829&rtpof=true&sd=true"
    )
    parser.add_argument(
        "-u", "--url",
        help="URL to establish a connection between the process and MongoDB",
        default="mongodb://localhost",
        metavar="mongodb://localhost"
    )

    parser.add_argument(
        "-db", "--database",
        help="Directory with the evidences to update",
        default="regulondbmultigenomic",
        metavar="regulondbmultigenomic"
    )

    parser.add_argument(
        "-org",
        "--organism",
        help="Organism whose information is been downloaded.",
        default="ECOLI",
        metavar="ecoli",
    )

    parser.add_argument(
        "-n", "--new",
        help="New evidences file",
        default="../RawData/EvidenceCatalog/new_evidences/new_evidences.json",
    )
    parser.add_argument(
        "-up", "--update",
        help="The evidences to update",
        default="../RawData/EvidenceCatalog/update_evidences.json",
    )

    parser.add_argument(
        "-un", "--unknwon",
        help="The unknwon evidences file",
        default="../RawData/EvidenceCatalog/unknwon_evidences.json",
    )

    parser.add_argument(
        "-r", "--rules",
        help="The evidence rules file",
        default="../RawData/EvidenceCatalog/Rules/evidences_rules.json",
    )

    parser.add_argument(
        "-l", "--log",
        help="Directory that contains log of the invalid data, the reason why the data is being rejected.",
        default="../logs/EvidenceCatalog/"
    )
    arguments = parser.parse_args()
    return arguments
