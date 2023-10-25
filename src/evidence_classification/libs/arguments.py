import argparse


def load():
    parser = argparse.ArgumentParser(description="Analytical cross-validation is an active evaluation of confidence and integrates multiple evidence by combining independent types of evidence, with the intention to confirm individual objects and mutually exclude false positives. It follows the same principles of science as applied by wet-lab scientists, where data are confirmed by repetitions on the one hand, and by additional experimental strategies to exclude alternative explanations on the other.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-a",
        "--all",
        help="Sets the program to read and update all the available classes, ignoring all arguments.",
        action="store_true",
    )

    parser.add_argument(
        "-d", "--directory",
        help="Directory where the json files are located",
        default="Results/"
    )

    parser.add_argument(
        "-db", "--database",
        help="Directory with the evidences to update",
        default="regulondbmultigenomic",
        metavar="regulondbmultigenomic"
    )

    parser.add_argument(
        "-org", "--organism",
        help="Organism whose information is been downloaded.",
        default="ECOLI",
        metavar="ecoli",
    )

    parser.add_argument(
        "-v", "--version",
        help="RegulonDB's release version",
        metavar="12.0",
        required=True
    )

    parser.add_argument(
        "-s", "--source",
        help="Source's name",
        metavar="EcoCyc",
        required=True
    )

    parser.add_argument(
        "-sv", "--sourceversion",
        help="Source's release version",
        metavar="27.0",
        required=True
    )

    parser.add_argument(
        "-i", "--input-file",
        help="JSON input file to process",
        required=False
    )

    parser.add_argument(
        "-l", "--log",
        help="Directory that contains log of the invalid data, the reason why the data is being rejected.",
        default="Results/log/"
    )

    parser.add_argument(
        "-u", "--url",
        help="URL to establish a connection between the process and MongoDB",
        default="mongodb://localhost:27017/",
        metavar="mongodb://localhost:27017/"
    )

    parser.add_argument(
        "-r", "--rules",
        help="The evidence rules file",
        default="Results/Rules/evidences_rules.json",
    )

    # COLLECTIONS ARGUMENTS

    parser.add_argument(
        "-ev",
        "--evidences",
        help="Sets the program to update confidenceLevel property of Evidences",
        action="store_true",
    )

    parser.add_argument(
        "-extdb",
        "--external-databases",
        help="Sets the program to update confidenceLevel property of External Databases",
        action="store_true",
    )

    parser.add_argument(
        "-gn",
        "--genes",
        help="Sets the program to update confidenceLevel property of Genes",
        action="store_true",
    )

    parser.add_argument(
        "-got",
        "--gene-ontology",
        help="Sets the program to update confidenceLevel property of Ontologies(MultiFun, GO Terms)",
        action="store_true",
    )

    parser.add_argument(
        "-gotm",
        "--got-terms",
        help="Sets the program to update confidenceLevel property of Ontologies' Terms",
        action="store_true",
        dest="got_terms",
    )

    parser.add_argument(
        "-mft",
        "--multifun-terms",
        help="Sets the program to update confidenceLevel property of Ontologies' Terms",
        action="store_true",
    )

    parser.add_argument(
        "-mot",
        "--multifun-ontology",
        help="Sets the program to update confidenceLevel property of Ontologies(MultiFun, GO Terms)",
        action="store_true",
    )

    parser.add_argument(
        "-mp",
        "--modified-protein",
        help="Sets the program to update confidenceLevel property of Modified Proteins",
        action="store_true",
    )

    parser.add_argument(
        "-mt",
        "--motifs",
        help="Sets the program to update confidenceLevel property of Motifs",
        action="store_true",
    )

    parser.add_argument(
        "-op",
        "--operons",
        help="Sets the program to update confidenceLevel property of Operons",
        action="store_true",
    )

    parser.add_argument(
        "-ot",
        "--ontologies",
        help="Sets the program to update confidenceLevel property of Ontologies(MultiFun, GO Terms)",
        action="store_true",
    )

    parser.add_argument(
        "-pb",
        "--publications",
        help="Sets the program to update confidenceLevel property of Publications",
        action="store_true",
    )

    parser.add_argument(
        "-pc",
        "--protein-complex",
        help="Sets the program to update confidenceLevel property of Protein Complexes",
        action="store_true",
    )

    parser.add_argument(
        "-pd",
        "--products",
        help="Sets the program to update confidenceLevel property of Products",
        action="store_true",
    )

    parser.add_argument(
        "-pm",
        "--promoters",
        help="Sets the program to update confidenceLevel property of Promoters",
        action="store_true",
    )

    parser.add_argument(
        "-rc",
        "--regulatory-continuants",
        help="Sets the program to update confidenceLevel property of Regulatory Continuants",
        action="store_true",
    )

    parser.add_argument(
        "-rcplx",
        "--regulatory-complexes",
        help="Sets the program to update confidenceLevel property of Regulatory Complexes",
        action="store_true",
    )

    parser.add_argument(
        "-ri",
        "--regulatory-interactions",
        help="Sets the program to update confidenceLevel property of Regulatory Interactions",
        action="store_true",
    )

    parser.add_argument(
        "-sf",
        "--sigma-factors",
        help="Sets the program to update confidenceLevel property of Sigma Factors",
        action="store_true",
    )

    parser.add_argument(
        "-sg",
        "--segments",
        help="Sets the program to update confidenceLevel property of Segments",
        action="store_true",
        dest="segments",
    )

    parser.add_argument(
        "-smc",
        "--small-molecule-complex",
        help="Sets the program to update confidenceLevel property of Small Molecules",
        action="store_true",
    )

    parser.add_argument(
        "-st",
        "--sites",
        help="Sets the program to update confidenceLevel property of Sites",
        action="store_true",
    )

    parser.add_argument(
        "-tf",
        "--transcription-factors",
        help="Sets the program to update confidenceLevel property of Transcription Factors",
        action="store_true",
    )

    parser.add_argument(
        "-tm",
        "--terminators",
        help="Sets the program to update confidenceLevel property of Terminators",
        action="store_true",
    )

    parser.add_argument(
        "-tu",
        "--transcription-units",
        help="Sets the program to update confidenceLevel property of Transcription Units",
        action="store_true",
    )

    arguments = parser.parse_args()

    return arguments
