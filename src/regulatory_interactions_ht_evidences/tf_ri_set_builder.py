"""
TF-RI Set <> Multigenomic Edition
Generate a minimal, normalized TF-RI_set.tsv from MongoDB (EcoCyc/RegulonDB MG).

Defaults:
- URL: mongodb://localhost:27017
- DB: regulondbmultigenomic
- Collection: regulatoryInteractions
- Output dir: ../../../InputData
- Output file: <out_dir>/TF-RI_set.tsv
"""

import os
import argparse
from typing import List, Dict, Any

from pymongo import MongoClient
import pandas as pd


DEFAULT_MONGO_URL = "mongodb://localhost:27017"
DEFAULT_DB_NAME = "regulondbmultigenomic"
DEFAULT_SRC_COLLECTION = "regulatoryInteractions"
DEFAULT_OUT_DIR = "../../../InputData"
DEFAULT_OUT_FILENAME = "TF-RI_set.tsv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate TF-RI_set.tsv from MongoDB (Multigenomic).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-u", "--mongo-url",
        dest="mongo_url",
        default=DEFAULT_MONGO_URL,
        help="MongoDB connection string",
        metavar="mongodb://host:port",
    )
    parser.add_argument(
        "-db", "--db-name",
        dest="db_name",
        default=DEFAULT_DB_NAME,
        help="MongoDB database name",
        metavar="regulondbmultigenomic",
    )
    parser.add_argument(
        "-c", "--collection",
        dest="src_collection",
        default=DEFAULT_SRC_COLLECTION,
        help="Source collection name",
        metavar="regulatoryInteractions",
    )
    parser.add_argument(
        "-o", "--out-dir",
        dest="out_dir",
        default=DEFAULT_OUT_DIR,
        help="Output directory",
        metavar="../../../InputData",
    )
    parser.add_argument(
        "--out-tsv",
        dest="out_tsv",
        default=None,
        help="Output TSV path (overrides --out-dir/TF-RI_set.tsv)",
        metavar="PATH",
    )

    return parser.parse_args()


def build_pipeline() -> List[Dict[str, Any]]:
    return [
        {"$match": {"regulationClass": "|Transcription-Factor-Binding|"}},
        {"$project": {
            "_id": 0,
            "ri_id": "$_id",
            "ri_citations": "$citations",
            "regulatorySites_id": 1,
            "regulator": 1
        }},
        {"$lookup": {
            "from": "regulatoryComplexes",
            "let": {"rcId": "$regulator._id", "isRC": {"$eq": ["$regulator.type", "regulatoryComplex"]}},
            "pipeline": [
                {"$match": {"$expr": {"$and": ["$$isRC", {"$eq": ["$_id", "$$rcId"]}]}}},
                {"$project": {"_id": 0, "products": 1}}
            ],
            "as": "_rc"
        }},
        {"$set": {
            "_rcProductsAll": {
                "$reduce": {"input": "$_rc", "initialValue": [], "in": {"$concatArrays": ["$$value", {"$ifNull": ["$$this.products", []]}]}}
            }
        }},
        {"$set": {"_rcProductIds": {"$map": {"input": "$_rcProductsAll", "as": "p", "in": "$$p.products_id"}}}},
        {"$set": {
            "regulator_product_ids": {
                "$cond": [{"$eq": ["$regulator.type", "product"]}, ["$regulator._id"], "$_rcProductIds"]
            }
        }},
        {"$lookup": {
            "from": "transcriptionFactors",
            "let": {"productIds": "$regulator_product_ids"},
            "pipeline": [
                {"$match": {"$expr": {"$gt": [{"$size": {"$setIntersection": ["$products_ids", "$$productIds"]}}, 0]}}},
                {"$project": {"_id": 0, "abbreviatedName": 1, "products_ids": 1}}
            ],
            "as": "regulator_TFs"
        }},
        {"$set": {"tf_name": {"$first": "$regulator_TFs.abbreviatedName"}}},
        {"$project": {"_rc": 0, "_rcProductsAll": 0, "_rcProductIds": 0, "regulator_product_ids": 0, "regulator": 0, "regulator_TFs": 0}},
        {"$lookup": {
            "from": "regulatorySites",
            "localField": "regulatorySites_id",
            "foreignField": "_id",
            "pipeline": [{"$project": {
                "site_id": "$_id",
                "_id": 0,
                "site_citations": "$citations",
                "leftEndPosition": 1,
                "rightEndPosition": 1,
                "sequence": 1
            }}],
            "as": "site"
        }},
        {"$set": {"site": {"$first": "$site"}}},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", {"$ifNull": ["$site", {}]}]}}},
        {"$project": {"regulatorySites_id": 0, "site": 0}},
        {"$project": {
            "ri_id": 1,
            "tf_name": 1,
            "site_id": 1,
            "site_left": "$leftEndPosition",
            "site_right": "$rightEndPosition",
            "site_evidences_ids": "$site_citations.evidences_id",
            "site_pmids_ids": "$site_citations.publications_id",
            "ri_evidences_ids": "$ri_citations.evidences_id",
            "ri_pmids_ids": "$ri_citations.publications_id"
        }},
        {"$set": {
            "site_evidences_ids": {"$setUnion": ["$site_evidences_ids", []]},
            "site_pmids_ids": {"$setUnion": ["$site_pmids_ids", []]},
            "ri_evidences_ids": {"$setUnion": ["$ri_evidences_ids", []]},
            "ri_pmids_ids": {"$setUnion": ["$ri_pmids_ids", []]}
        }},
        {"$lookup": {
            "from": "evidences",
            "localField": "ri_evidences_ids",
            "foreignField": "_id",
            "pipeline": [{"$project": {"code": 1, "_id": 0}}],
            "as": "ri_evidences"
        }},
        {"$lookup": {
            "from": "evidences",
            "localField": "site_evidences_ids",
            "foreignField": "_id",
            "pipeline": [{"$project": {"code": 1, "_id": 0}}],
            "as": "site_evidences"
        }},
        {"$lookup": {
            "from": "publications",
            "localField": "ri_pmids_ids",
            "foreignField": "_id",
            "pipeline": [{"$project": {"pmid": 1, "_id": 0}}],
            "as": "ri_pmids"
        }},
        {"$lookup": {
            "from": "publications",
            "localField": "site_pmids_ids",
            "foreignField": "_id",
            "pipeline": [{"$project": {"pmid": 1, "_id": 0}}],
            "as": "site_pmids"
        }},
        {"$project": {
            "site_evidences_ids": 0,
            "site_pmids_ids": 0,
            "ri_evidences_ids": 0,
            "ri_pmids_ids": 0
        }},
        {"$set": {
            "ri_evidences": {"$map": {"input": "$ri_evidences", "as": "e", "in": "$$e.code"}},
            "site_evidences": {"$map": {"input": "$site_evidences", "as": "e", "in": "$$e.code"}},
            "ri_pmids": {"$map": {"input": "$ri_pmids", "as": "p", "in": "$$p.pmid"}},
            "site_pmids": {"$map": {"input": {"$ifNull": ["$site_pmids", []]}, "as": "p", "in": "$$p.pmid"}}
        }}
    ]


def to_minimal_rows(doc: Dict[str, Any]) -> Dict[str, Any]:
    def list_to_str(v):
        if v is None:
            return ""
        if isinstance(v, list):
            return ";".join(str(x) for x in v if x is not None)
        return str(v)

    return {
        "ri_id": doc.get("ri_id", ""),
        "tf_name": doc.get("tf_name", ""),
        "site_left": doc.get("site_left", ""),
        "site_right": doc.get("site_right", ""),
        "site_evidences": list_to_str(doc.get("site_evidences", [])),
        "ri_evidences": list_to_str(doc.get("ri_evidences", [])),
        "site_pmids": list_to_str(doc.get("site_pmids", [])),
        "ri_pmids": list_to_str(doc.get("ri_pmids", [])),
    }


def main():
    args = parse_args()

    out_dir = args.out_dir
    out_tsv = args.out_tsv or os.path.join(out_dir, DEFAULT_OUT_FILENAME)

    os.makedirs(out_dir, exist_ok=True)

    client = MongoClient(args.mongo_url)
    db = client[args.db_name]
    col = db[args.src_collection]

    pipeline = build_pipeline()
    cursor = col.aggregate(pipeline, allowDiskUse=True)

    rows = [to_minimal_rows(doc) for doc in cursor]

    cols = ["ri_id", "tf_name", "site_left", "site_right",
            "site_evidences", "ri_evidences", "site_pmids", "ri_pmids"]
    df = pd.DataFrame(rows, columns=cols)

    for c in ["site_left", "site_right"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df.to_csv(out_tsv, sep="\t", index=False)
    print(f"TF-RI_set.tsv written to: {out_tsv}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()
