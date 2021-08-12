import argparse


def load():
    parser = argparse.ArgumentParser(description="Evidence RegulonDB Catalog ETL Process",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-c", "--catalog",
        help="Dataset with the evidences to be processed",
        default="Input_Data/RegulonDB-Evidence_Catalog_v1.0.xls"
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
        "-n", "--new",
        help="New evidences file",
        default="Results/new_evidences/new_evidences.json",
    )
    parser.add_argument(
        "-up", "--update",
        help="The evidences to update",
        default="Results/update_evidences.json",
    )

    parser.add_argument(
        "-un", "--unknwon",
        help="The unknwon evidences file",
        default="Results/unknwon_evidences.json",
    )

    parser.add_argument(
        "-l", "--log",
        help="Directory that contains log of the invalid data, the reason why the data is being rejected.",
        default="Results/log/"
    )
    arguments = parser.parse_args()
    return arguments
