"""Update RI documents with new HT-binding citations.

This script reads the summary table produced by the previous step
(`../RawData/New_ev_RIs_mapped.tsv`) and updates the MongoDB collection
`regulatoryInteractions` by appending **only truly new citations**.

A citation is considered new when the (evidence, publication) pair
does not already exist in the RI document — i.e., by the composite key:
`(evidences_id, publications_id)`.

Outputs:
- MongoDB updates under `regulatoryInteractions.citations` (append-only).
- `ri_events.log` with CSV-like auditing lines.
- `modified_ris.json` / `unmodified_ris.json` with the attempted updates.

Phases:
1) Load arguments, set I/O paths, and connect to MongoDB.
2) Read input TSV and sanitize column names/strings.
3) Parse "New (Evidence:reference)" safely into (evidence_code, pmids[]) items.
4) Resolve `evidences_id` and `publications_id` for each parsed item.
5) For each RI, compare against existing citations using (evidence, publication) pairs.
6) Insert only missing pairs; log every action for traceability.
"""

# standard
import os
import re
import json
import sys
from datetime import datetime
from typing import List, Tuple, Optional

# thirdparty
import pandas as pd
import pymongo

# local
from libs import arguments


def print_progress(current: int, total: int, label: str, inserted: int, bar_length: int = 40) -> None:
    """
    Displays a real-time progress bar in the console, updating on the same line.
    Also shows a running counter of inserted citations.

    Args:
        current: processed items count.
        total: total items count.
        label: short label for the process.
        inserted: total inserted citations so far.
        bar_length: fixed progress bar length.
    """
    fraction = current / total if total else 1
    filled = int(bar_length * fraction)
    bar = "█" * filled + "-" * (bar_length - filled)
    percent = int(fraction * 100)

    sys.stdout.write(
        f"\r{label}: |{bar}| {percent}% ({current}/{total}) | inserted: {inserted}"
    )
    sys.stdout.flush()

    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


def log_event(ri_id: str, action: str, details: str = "", log_path: str = "ri_events.log") -> None:
    """Append a CSV-like audit line to the local log file.

    Args:
        ri_id: RI identifier (_id) that the event relates to.
        action: Short tag describing the event (e.g., 'UPDATED', 'ERROR').
        details: Optional free text with extra context.
        log_path: output log file path.
    """
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"{ts},{ri_id},{action}"
    if details:
        line += f",{details}"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_new_evidences_cell(cell: str) -> List[Tuple[str, List[str]]]:
    """Parse the 'New (Evidence:reference)' cell into items.

    Expected formats (summary WITHOUT ORIGIN):
      - "(EVIDENCE:PMID)"
      - "(EVIDENCE:PMID1, PMID2)" for multiple PMIDs in one evidence item
      - Multiple items: "(...:...), (...:...)" (each wrapped in parentheses)

    Parsing strategy:
      - Extract inner contents between parentheses with regex.
      - For each inner string, split by ':' -> [EVIDENCE, PMIDs...]
      - Clean 'CIT:' prefix in PMIDs when present.

    Args:
        cell: Raw string from the "New (Evidence:reference)" column.

    Returns:
        List of tuples (evidence_code, pmid_list). Returns an empty list if
        the cell is empty or "(nan)".
    """
    if not isinstance(cell, str) or not cell.strip() or cell.strip() == "(nan)":
        return []

    s = cell.strip()
    parts = re.findall(r"\((.*?)\)", s)  # grab everything inside "(...)"
    items: List[Tuple[str, List[str]]] = []

    for p in parts:
        core = p.strip().replace("CIT:", "")  # normalize PMIDs if CIT: was included
        chunks = [c.strip() for c in core.split(":") if c.strip()]
        if not chunks:
            continue
        evid_code = chunks[0]
        pmids: List[str] = []
        if len(chunks) > 1:
            pmids = [x.strip() for x in chunks[1].split(",") if x.strip()]
        items.append((evid_code, pmids))

    return items


def main() -> None:
    # ========== Phase 1: arguments, DB connection ==========
    args = arguments.load()

    database = args.database
    id_database = args.id_database  # reserved for future use
    url = args.url
    client = pymongo.MongoClient(url)
    db = client[database]

    evidences_collection = db["evidences"]
    publications_collection = db["publications"]
    reg_interactions_collection = db["regulatoryInteractions"]

    # Keep for pipeline consistency
    basePath = args.directory  # not used here

    # ---------- I/O from args ----------
    input_dir = args.output
    output_dir = args.output
    log_path = getattr(args, "log_path", "ri_events.log")

    os.makedirs(output_dir, exist_ok=True)

    # ========== Phase 2: read input summary & sanitize ==========
    inputFilePath = os.path.join(input_dir, "New_ev_RIs_mapped.tsv")  # summary w/o ORIGIN
    file_df = pd.read_csv(inputFilePath, sep="\t", header=0)

    # Normalize headers and trim string values for safety
    file_df.rename(columns=lambda c: c.strip(), inplace=True)
    file_df = file_df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Containers for export/reporting
    ri_list = []
    ri_without_citations = []

    # ========== Phase 3–4: parse & resolve IDs ==========
    for _, row in file_df.iterrows():
        raw_new = row.get("New (Evidence:reference)", None)

        # No new evidences for this RI -> keep record & skip
        if not isinstance(raw_new, str) or raw_new.strip() == "" or raw_new.strip() == "(nan)":
            ri_without_citations.append({"_id": row["ri_id"], "citations": raw_new})
            continue

        parsed_items = parse_new_evidences_cell(raw_new)

        citations = []
        for evid_code, pmids in parsed_items:
            # Resolve evidences_id by exact code, with a regex fallback removing 'EXP-'
            ev_id: Optional[str] = None
            ev_obj = evidences_collection.find_one({"code": evid_code})
            if ev_obj is not None:
                ev_id = ev_obj.get("_id")
            if ev_id is None:
                short_ev_code = evid_code.replace("EXP-", "")
                regx = re.compile(short_ev_code)
                ev_obj2 = evidences_collection.find_one({"code": regx})
                if ev_obj2 is not None:
                    ev_id = ev_obj2.get("_id")

            if not ev_id:
                # Evidence code not found: log and continue
                log_event(row["ri_id"], "WARN_NO_EVIDENCE", f"code={evid_code}", log_path=log_path)
                continue

            # Resolve publications_id by pmid; if not found, keep the PMID string
            for pmid in pmids if pmids else [""]:
                pmid_clean = pmid.replace("CIT:", "").strip()
                if not pmid_clean:
                    continue

                pub_obj = publications_collection.find_one({"pmid": pmid_clean})
                pub_id = pub_obj.get("_id") if pub_obj is not None else pmid_clean

                citation = {
                    "evidences_id": ev_id,
                    "publications_id": pub_id,
                }
                citations.append(citation)

        if citations:
            ri_list.append({"_id": row["ri_id"], "citations": citations})
        else:
            ri_without_citations.append({"_id": row["ri_id"], "citations": "(nan)"})

    # ========== Phase 5–6: de-dup vs existing and update ==========
    modified_documents = 0
    inserted_citations = 0
    total_ris = len(ri_list)
    processed_ris = 0

    for ht_ri in ri_list:
        processed_ris += 1
        print_progress(processed_ris, total_ris, "Updating regulatoryInteractions", inserted_citations)

        ht_ri_id = ht_ri.get("_id")
        query = {"_id": ht_ri_id}

        mg_ri = reg_interactions_collection.find_one(query)  # may be None
        mg_ri_citations = (mg_ri or {}).get("citations", [])

        # Build set of existing (evidence, publication) pairs to avoid duplicates
        existing_pairs = set()
        for c in mg_ri_citations:
            ev = c.get("evidences_id")
            pub = c.get("publications_id")
            if ev and pub:
                existing_pairs.add((str(ev), str(pub)))

        ht_ri_citations = ht_ri.get("citations", [])
        new_citations = []
        for ht_cit in ht_ri_citations:
            pair = (str(ht_cit.get("evidences_id")), str(ht_cit.get("publications_id")))
            if pair not in existing_pairs:
                new_citations.append(ht_cit)

        if not new_citations:
            log_event(ht_ri_id, "ALREADY_PRESENT", "no new citations (evidence+publication)", log_path=log_path)
            continue

        any_change = False
        for new_citation in new_citations:
            try:
                result = reg_interactions_collection.update_one(
                    {"_id": ht_ri_id},
                    {"$push": {"citations": new_citation}},
                    upsert=True,
                )

                if result.upserted_id is not None:
                    log_event(ht_ri_id, "INSERTED", "created doc & added citation", log_path=log_path)
                    any_change = True
                elif result.modified_count > 0:
                    log_event(ht_ri_id, "UPDATED", "added citation", log_path=log_path)
                    any_change = True
                else:
                    log_event(ht_ri_id, "NO_CHANGE", "push produced no diff", log_path=log_path)

                modified_documents += result.modified_count
                inserted_citations += result.modified_count

                # refresh progress display with new inserted count
                print_progress(processed_ris, total_ris, "Updating regulatoryInteractions", inserted_citations)

            except pymongo.errors.WriteError as e:
                log_event(ht_ri_id, "ERROR", str(e), log_path=log_path)

        if not any_change:
            log_event(ht_ri_id, "SKIPPED", "filtered as duplicates", log_path=log_path)

    print(f"Total of RIs processed: {len(ri_list)}, Total of evidences inserted: {modified_documents}")

    # ========== Exports for audit ==========
    with open(os.path.join(output_dir, "modified_ris.json"), "w", encoding="utf-8") as json_file:
        json.dump(ri_list, json_file, ensure_ascii=False, default=str)
    with open(os.path.join(output_dir, "unmodified_ris.json"), "w", encoding="utf-8") as json_file:
        json.dump(ri_without_citations, json_file, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
