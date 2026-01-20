"""
RI-to-HT peaks mapping (unified output)

This script consolidates mappings between Regulatory Interactions (RIs) and
high-throughput (HT) TF-binding peaks coming from multiple collections
(ChIP-seq, ChIP-exo, DAP-seq, gSELEX), producing a single TSV result and a
single error log. Outputs annotate each contribution with its data origin.

Phases:
1) Load configuration and services (identifiers API, arguments).
2) Resolve input/output locations and open unified outputs.
3) Build RI->EcoCyc identifier map.
4) Iterate over base paths (data origins), load RI set & collection metadata.
5) For each RI with site, scan datasets of matching TFs to find overlapping peaks:
   - Normalize peak coordinates (start/end/center/coverage).
   - Skip/record depending on evidence/manual conditions.
   - Accumulate per-RI evidence, peaks, and status flags (deduplicated).
6) Write a single combined TSV with fused columns for Evidence;Reference,
   matchingpeaks, RI_Ecocyc_ID, and STATUS.
"""

# standard
import os
import sys
from typing import Dict, Any, Set

# thirdparty
import pandas as pd
import identifiers_api

# local
from libs import arguments
from utils import utils

print("Start")


def print_progress(current, total, collection_name, bar_length=40):
    """
    Displays a real-time progress bar in the console, updating on the same line.
    """
    fraction = current / total if total else 1
    filled = int(bar_length * fraction)
    bar = "█" * filled + "-" * (bar_length - filled)
    percent = int(fraction * 100)
    sys.stdout.write(
        f"\rProcessing {collection_name}: |{bar}| {percent}% ({current}/{total}) objects processed"
    )
    sys.stdout.flush()


# ========== Phase 1: Config & external services ==========
args = arguments.load()
identifiers_api.connect(args.url)

# ========== Phase 2: I/O setup (unified outputs) ==========
INPUT_DIR = args.set_file
OUTPUT_DIR = args.output

COMMON_OUT_PATH = os.path.join(OUTPUT_DIR, "Classical_confirmed_Strong_HT_mapped.tsv")
COMMON_ERR_PATH = os.path.join(OUTPUT_DIR, "Error_Class_conf_withoutHTdatasets_without_coords.tsv")

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 50)


def get_ri_cyc_ids(database: str, organism: str, collection_name: str) -> Dict[str, str]:
    """Fetch a mapping of EcoCyc frame IDs to RI identifiers."""
    try:
        ri_cyc_ids = identifiers_api.get_identifiers(collection_name, database, organism)
        return ri_cyc_ids
    except Exception:
        print(f'Error extracting {collection_name} Original IDs')
        return {}


# ========== Phase 3: Build RI->EcoCyc map ==========
ri_cyc_ids_list = get_ri_cyc_ids(
    database=args.database,
    organism='ECOLI',
    collection_name='regulatoryInteractions'
)

# ========== Accumulator structure (per RI) ==========
ri_acc: Dict[str, Dict[str, Any]] = {}
header_written = False


def ri_has_ht_evidence(ri_set_row: pd.Series, evi_reference: str) -> bool:
    """Check if RI already contains the HT evidence reference."""
    evi_reference = evi_reference.replace("(", "").replace(")", "")
    try:
        evi, ref, *_ = evi_reference.split(";")
    except ValueError:
        return False

    ref = ref.replace("CIT:", "")
    target = {evi: ref}

    # RI-level evidence/PMIDs
    ri_evidence = str(ri_set_row.get("ri_evidences", "")).split(":")[0]
    ri_pmids = str(ri_set_row.get("ri_pmids", "")).split(";")
    for ri_pmid in ri_pmids:
        if target == {ri_evidence: ri_pmid.strip()}:
            return True

    # Site-level evidence/PMIDs
    site_evidence = str(ri_set_row.get("site_evidences", "")).split(":")[0]
    site_pmids = str(ri_set_row.get("site_pmids", "")).split(":")
    for site_pmid in site_pmids:
        if target == {site_evidence: site_pmid.strip()}:
            return True

    return False


# ========== Phase 4 & 5: Process sources, scan datasets, accumulate ==========
base_paths = args.directory
counter = 0

# Ensure output directory exists before writing
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(COMMON_OUT_PATH, "w", encoding="utf-8") as out_f, open(COMMON_ERR_PATH, "w", encoding="utf-8") as err_f:
    for base_path in base_paths.split(','):
        base_path = base_path.strip()
        if not base_path:
            continue

        # Data origin tag comes from the folder name (uppercased), used to annotate combined outputs
        data_origin: str = (base_path.split('/')[-2]).upper()

        files_paths = {
            # RI set is centralized under INPUT_DIR
            'ri_file': os.path.join(INPUT_DIR, "TF-RI_set.tsv"),
            # Authors data (peak datasets) per collection, under each base_path (origin)
            'chip_seq_authors': os.path.join(base_path, "ChIP-seq/author_files/"),
            'chip_exo_authors': os.path.join(base_path, "ChIP-exo/author_files/"),
            'dap_seq_authors': os.path.join(base_path, "DAP-seq/author_files/"),
            'gselex_authors': os.path.join(base_path, "gSELEX/author_files/"),
            # Metadata per collection, under each base_path (origin)
            'chip_seq_dataset': os.path.join(base_path, "ChIP-seq/metadata/DatasetCollection.xlsx"),
            'chip_exo_dataset': os.path.join(base_path, "ChIP-exo/metadata/DatasetCollection.xlsx"),
            'dap_seq_dataset': os.path.join(base_path, "DAP-seq/metadata/DatasetCollection.xlsx"),
            'gselex_dataset': os.path.join(base_path, "gSELEX/metadata/DatasetCollection.xlsx"),
        }

        # ---- 4.1 Load RI set and normalize column headers ----
        ri_df = pd.read_csv(files_paths['ri_file'], sep="\t", comment='#', header=0)
        ri_df.rename(columns=lambda c: c.strip(), inplace=True)  # remove trailing spaces in column names

        # Write the unified header only once (original RI columns + appended fields)
        if not header_written:
            original_cols = list(ri_df.columns.values)
            base_header = "\t".join(original_cols)
            extra_header = "\t".join(["Evidence;Reference", "matchingpeaks", "RI_Ecocyc_ID", "STATUS"])
            out_f.write(base_header + "\t" + extra_header + "\n")
            header_written = True

        # ---- 4.2 Load collection metadata (Excel) ----
        chip_exo_df = utils.load_dataframe(path=files_paths['chip_exo_dataset'])
        chip_seq_df = utils.load_dataframe(path=files_paths['chip_seq_dataset'])
        gselex_df = utils.load_dataframe(path=files_paths['gselex_dataset'])
        dap_seq_df = utils.load_dataframe(path=files_paths['dap_seq_dataset'])

        all_collections = [
            {
                'data_frame': chip_seq_df,
                'collection_name': 'Chipseq',
                'evidence_code': ("EXP-CHIP-SEQ-MANUAL" if data_origin == "GALAGAN" else "EXP-CHIP-SEQ"),
                'authors_data_path': files_paths['chip_seq_authors'],
            },
            {
                'data_frame': chip_exo_df,
                'collection_name': 'Chipexo',
                'evidence_code': ("EXP-CHIP-EXO-MANUAL" if data_origin == "GALAGAN" else "EXP-CHIP-EXO"),
                'authors_data_path': files_paths['chip_exo_authors'],
            },
            {
                'data_frame': gselex_df,
                'collection_name': 'Gselex',
                'evidence_code': ("EXP-GSELEX-MANUAL" if data_origin == "GALAGAN" else "EXP-GSELEX"),
                'authors_data_path': files_paths['gselex_authors'],
            },
            {
                'data_frame': dap_seq_df,
                'collection_name': 'Dapseq',
                'evidence_code': ("EXP-DAP-SEQ-MANUAL" if data_origin == "GALAGAN" else "EXP-DAP-SEQ"),
                'authors_data_path': files_paths['dap_seq_authors'],
            },
        ]

        # ---- 5.1 Keep only RIs with site coordinates (required for mapping) ----
        ri_df_sites = ri_df[ri_df['site_left'] != "-"]

        total_ris = len(ri_df_sites)
        processed_ris = 0

        # ---- 5.2 Iterate over RIs and perform peak overlap checks ----
        for _, ri_row in ri_df_sites.iterrows():
            # Rebuild the original RI line (tab-joined) to preserve original order
            ri_line_base = "\t".join(str(v) for v in ri_row.values)
            ri_tf = ri_row['tf_name']

            if pd.isna(ri_row['site_left']) or pd.isna(ri_row['site_right']):
                processed_ris += 1
                print_progress(processed_ris, total_ris, data_origin)
                continue

            # Compute RI center from left/right coords
            ri_site_start = int(ri_row['site_left'])
            ri_site_end = int(ri_row['site_right'])
            ri_center = ri_site_start + (ri_site_end - ri_site_start) / 2

            # Use the first column as RI ID key
            ri_id = ri_row.get('ri_id')

            # Map RI -> EcoCyc ID
            try:
                ri_cyc_id = list(ri_cyc_ids_list.keys())[list(ri_cyc_ids_list.values()).index(ri_id)]
            except ValueError:
                ri_cyc_id = ""

            # Initialize accumulator entry
            if ri_id not in ri_acc:
                ri_acc[ri_id] = {
                    'base_line': ri_line_base,
                    'evidence': set(),  # type: Set[str]
                    'peaks': set(),     # type: Set[str]
                    'status': set(),    # type: Set[str]
                    'ri_cyc_id': ri_cyc_id,
                }

            evs_refs: Set[str] = set()
            matching_peaks: Set[str] = set()
            status_flags: Set[str] = set()

            # ---- 5.3 For each collection: filter metadata for matching TF, read datasets, check overlaps ----
            for col in all_collections:
                df_meta = col['data_frame']
                if df_meta is None or df_meta.empty:
                    continue

                evidence_code = col['evidence_code']
                authors_path = col['authors_data_path']

                filtered = df_meta[df_meta["RegulonDB TF Name"] == ri_tf]

                # For gSELEX: exclude TFs without cutoff (per domain policy)
                if col['collection_name'] == "Gselex":
                    excluded_tfs = ["IHF", "H-NS", "Fis", "Lrp", "TFs", "HU", "Dan", "Dps"]
                    filtered = filtered[~filtered["RegulonDB TF Name"].isin(excluded_tfs)]

                for _, md_row in filtered.iterrows():
                    file_name = md_row['Dataset File Name']
                    pmid = str(md_row['PMID']).replace(".0", "")
                    if pd.isna(file_name):
                        continue

                    # Evidence;Reference (annotated with data_origin)
                    if data_origin == 'GALAGAN':
                        evidence_reference = f"({evidence_code};CIT:38505828;{data_origin})"
                    else:
                        evidence_reference = f"({evidence_code};{pmid};{data_origin})"

                    # Read the actual peak dataset for this metadata row
                    ds_path = str(authors_path) + str(file_name)
                    try:
                        df_ds = pd.read_csv(ds_path, sep='\t', header=0)
                    except Exception as e:
                        err_f.write(f"READ_ERROR\t{file_name}\t{pmid}\t{data_origin}\t{e}\n")
                        continue

                    # ---- 5.4 Iterate peaks and compute normalized coordinates ----
                    for _, pk in df_ds.iterrows():
                        p_start = pk.get('Peak_start', None)
                        p_end = pk.get('Peak_end', None)
                        p_center = pk.get('Peak center', None)
                        p_max = pk.get('Peak Maximum Coverage Position', None)
                        p_int = pk.get('Peak Intensity Fold Change/Binding intensity (%)', None)
                        tf_name = pk.get('TF_name*', None)

                        peak_type = "x"
                        if pd.notna(p_start):
                            # A) Has explicit start/end
                            peak_start, peak_end = p_start, p_end
                            peak_type = "a"
                        elif pd.notna(p_center):
                            # B) Use center ±100 if present and valid
                            if p_center != "NOT FOUND":
                                peak_start, peak_end = p_center - 100, p_center + 100
                                peak_type = "b"
                            else:
                                peak_start = peak_end = 0
                                peak_type = "f"
                        elif pd.notna(p_max):
                            # C) Use maximum coverage ±100
                            peak_start, peak_end = p_max - 100, p_max + 100
                            peak_type = "c"
                        else:
                            # D) No coordinates: log and mark as 'd'
                            err_f.write(f"{file_name}\t{pmid}\n")
                            peak_start = peak_end = 0
                            peak_type = "d"

                        # Peak representation annotated with origin (for fused 'matchingpeaks' column)
                        peak_repr = f"({evidence_code}:{file_name}:{peak_start}-{peak_end}:{peak_type}:{p_int};{data_origin})"

                        # Skip adding HT evidence if RI already contains a manual citation
                        has_manual = ri_has_ht_evidence(ri_row, evidence_reference)

                        # Overlap test: same TF and RI center within peak [start, end]
                        if (ri_tf == tf_name) and (ri_center > peak_start) and (ri_center < peak_end):
                            matching_peaks.add(peak_repr)
                            if not has_manual:
                                evs_refs.add(evidence_reference)
                                counter += 1
                            else:
                                status_flags.add("HAS_HT_EVIDENCE;" + data_origin)
                                err_f.write(f"SKIP_HT_FOR_MANUAL\t{file_name}\t{pmid}\t{data_origin}\n")

            # Status flags per origin based on whether overlaps were found
            if not matching_peaks:
                status_flags.add("NO_PEAK_MATCH;" + data_origin)
            else:
                status_flags.add("PEAK_MATCH;" + data_origin)

            # ---- 5.5 Merge per-RI accumulations (deduplicated) ----
            ri_acc[ri_id]['evidence'].update(evs_refs)
            ri_acc[ri_id]['peaks'].update(matching_peaks)
            ri_acc[ri_id]['status'].update(status_flags)
            if not ri_acc[ri_id]['ri_cyc_id'] and ri_cyc_id:
                ri_acc[ri_id]['ri_cyc_id'] = ri_cyc_id

            processed_ris += 1
            print_progress(processed_ris, total_ris, data_origin)

        if total_ris:
            print()  # newline after progress bar for this origin

    # ========== Phase 6: Final unified write ==========
    for ri_id, bundle in ri_acc.items():
        base_line = bundle['base_line']
        evs_str = ", ".join(sorted(bundle['evidence'])) if bundle['evidence'] else ""
        peaks_str = ", ".join(sorted(bundle['peaks'])) if bundle['peaks'] else ""
        status_str = ", ".join(sorted(bundle['status'])) if bundle['status'] else ""
        ri_cyc_id = bundle['ri_cyc_id'] or ""

        out_f.write(f"{base_line}\t{evs_str}\t{peaks_str}\t{ri_cyc_id}\t{status_str}\n")

print(f"Finished, RI processed {counter}")
print(f"Output File: {COMMON_OUT_PATH}")
print(f"Errors File: {COMMON_ERR_PATH}")
