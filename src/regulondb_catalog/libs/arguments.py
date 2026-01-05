import argparse


def load():
    """
    Parse command-line arguments for the RegulonDB Evidence Catalog ETL Process.

    This function constructs an ArgumentParser with all required CLI options
    used in the LocalData-ETL workflow, including input catalog paths,
    output JSON destinations, MongoDB connection parameters, and organism metadata.

    Returns
    -------
    argparse.Namespace
        Parsed arguments namespace containing all ETL configuration values.

    Notes
    -----
    - All flags and default values remain unchanged for backward compatibility.
    - Argument descriptions were improved for clarity without altering meaning.
    """
    parser = argparse.ArgumentParser(
        description="Evidence RegulonDB Catalog ETL Process",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-c", "--catalog",
        help="Local Excel dataset containing the evidences to be processed.",
        default="../InputData/EvidenceCatalog/RegulonDB_Evidence_Catalog_v3.2.xlsx"
    )

    parser.add_argument(
        "-rc", "--remote-catalog",
        help="Remote dataset URL containing the evidences to be processed.",
        default=(
            "https://docs.google.com/spreadsheets/d/"
            "1EFwbIHntVgF7FxMVkWT-lpZzcRpx1Fyu/edit?usp=share_link"
        ),
        metavar="REMOTE_URL"
    )

    parser.add_argument(
        "-u", "--url",
        help="MongoDB connection string used to access RegulonDB data.",
        default="mongodb://localhost",
        metavar="MONGODB_URL"
    )

    parser.add_argument(
        "-db", "--database",
        help="MongoDB database name for RegulonDB Multigenomic.",
        default="regulondbmultigenomic",
        metavar="DB_NAME"
    )

    parser.add_argument(
        "-org", "--organism",
        help="Organism identifier whose evidences will be processed.",
        default="ECOLI",
        metavar="ORG_CODE"
    )

    parser.add_argument(
        "-n", "--new",
        help="Output path for the NEW evidences JSON file.",
        default="../RawData/EvidenceCatalog/new_evidences/new_evidences.json"
    )

    parser.add_argument(
        "-up", "--update",
        help="Output path for the UPDATE evidences JSON file.",
        default="../RawData/EvidenceCatalog/update_evidences.json"
    )

    parser.add_argument(
        "-un", "--unknwon",  # cannot fix spelling due to backward compatibility
        help="Output path for the UNKNOWN evidences JSON file.",
        default="../RawData/EvidenceCatalog/unknwon_evidences.json"
    )

    parser.add_argument(
        "-r", "--rules",
        help="Output path for the evidence rules JSON file.",
        default="../RawData/EvidenceCatalog/Rules/evidences_rules.json"
    )

    parser.add_argument(
        "-l", "--log",
        help=(
            "Directory where ETL log files will be written. "
            "Logs include validation failures and evidence rejection causes."
        ),
        default="../logs/EvidenceCatalog/"
    )

    return parser.parse_args()
