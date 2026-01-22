# """Identify new HT-binding evidences from the unified RI→peaks mapping output.
#
# Reads the unified TSV produced by the RI→HT peaks mapping step and flags which
# HT evidences are NEW relative to the existing RI/site evidences.
#
# Outputs:
# - ../RawData/New_ev_RIs_mapped.tsv          → new evidences WITHOUT ORIGIN (EVIDENCE:PMID)
# - ../RawData/New_ev_RIs_mapped_report.tsv   → new evidences WITH ORIGIN (EVIDENCE:PMID:ORIGIN) + New Count
#
# Phases:
# 1) Load config and set I/O paths.
# 2) Read and sanitize the mapped RI table.
# 3) Iterate rows:
#    - Parse HT evidences robustly (supports multiple entries and ;ORIGIN).
#    - Compare ONLY the evidence CODE against RI/site evidences.
#    - Build lists of "new" evidences for output (no ORIGIN) and report (with ORIGIN).
#    - Preserve and extend STATUS with RI_WITH_NEW_EVIDENCE when applicable.
# 4) Write both outputs with proper headers.
# """
#
# # standard
# import os
# import re
# from typing import List
#
# # thirdparty
# import pandas as pd
#
# # local
# from libs import arguments
#
#
# def parse_ht_evidences(cell: str) -> List[str]:
#     """Return list of HT evidences (strings without parentheses).
#
#     Accepts: "(EVID;PMID;ORIGIN), (EVID;PMID;ORIGIN)" or "(EVID;PMID;ORIGIN)".
#     If no parentheses are found, returns [cell] as a fallback.
#     """
#     if not isinstance(cell, str) or cell.strip() == "" or cell.lower() == "nan":
#         return []
#     items = re.findall(r"\((.*?)\)", cell)
#     return items if items else [cell]
#
#
# def main() -> None:
#     print("Start")
#
#     # 1) Args + pandas opts
#     args = arguments.load()
#     pd.set_option("display.max_columns", 20)
#     pd.set_option("display.max_rows", 50)
#
#     # I/O (from CLI arguments)
#     INPUT_DIR = args.output
#     OUTPUT_DIR = args.output
#
#     ri_mapped_file_path = os.path.join(INPUT_DIR, "Classical_confirmed_Strong_HT_mapped.tsv")
#     output_file_path = os.path.join(OUTPUT_DIR, "New_ev_RIs_mapped.tsv")               # WITHOUT ORIGIN
#     report_output_file_path = os.path.join(OUTPUT_DIR, "New_ev_RIs_mapped_report.tsv") # WITH ORIGIN
#
#     # 2) Read + sanitize
#     df = pd.read_csv(ri_mapped_file_path, sep="\t", comment="#", header=0)
#     df.rename(columns=lambda c: c.strip(), inplace=True)
#     df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
#
#     # ---- Normalized column names (no legacy compat needed) ----
#     COL_TFRS = "site_evidence"
#     COL_RI = "ri_evidence"
#     COL_HT = "Evidence;Reference"
#     COL_STATUS = "STATUS"
#
#     if COL_HT not in df.columns:
#         raise KeyError("Missing 'Evidence;Reference' column in mapped input.")
#
#     # 4) Write outputs
#     with open(output_file_path, "w", encoding="utf-8") as f_out, \
#          open(report_output_file_path, "w", encoding="utf-8") as f_rep:
#
#         base_header = "\t".join(df.columns.tolist())
#         extra_name = "New (Evidence:reference)"     # WITHOUT ORIGIN
#         f_out.write(base_header + "\t" + extra_name + "\n")
#         f_rep.write(base_header + "\t" + extra_name + "\tNew Count\n")
#
#         print("RIs Mapped shape")
#         print(df.shape)
#
#         # 3) Iterate rows
#         for _, row in df.iterrows():
#             # Strings for comparison
#             tfrs_evidence = str(row.get(COL_TFRS, "") or "")
#             ri_evidence   = str(row.get(COL_RI, "")   or "")
#             ht_ev_str     = str(row.get(COL_HT, "")   or "")
#
#             # Parse HT evidences
#             ht_items = parse_ht_evidences(ht_ev_str)
#
#             new_evs_out: List[str] = []  # WITHOUT ORIGIN -> "(EVIDENCE:PMID)"
#             new_evs_rep: List[str] = []  # WITH ORIGIN    -> "(EVIDENCE:PMID:ORIGIN)"
#
#             for item in ht_items:
#                 parts = [p.strip() for p in item.split(";")]
#                 code = parts[0] if parts else ""
#
#                 # "New" if evidence CODE not present in site/RI evidences
#                 if code and (code not in tfrs_evidence) and (code not in ri_evidence):
#                     # report: keep ORIGIN (all segments), normalize ; -> :
#                     new_evs_rep.append("(" + item.replace(";", ":") + ")")
#
#                     # output: only EVIDENCE:PMID (first two segments)
#                     if len(parts) >= 2:
#                         new_evs_out.append("(" + parts[0] + ":" + parts[1] + ")")
#                     else:
#                         new_evs_out.append("(" + item.replace(";", ":") + ")")
#
#             # Extend STATUS if applicable
#             ri_line_row = [str(v) for v in row.values]
#             if new_evs_rep:
#                 status_idx = df.columns.get_loc(COL_STATUS)
#                 prev_status = ri_line_row[status_idx]
#                 tag = "RI_WITH_NEW_EVIDENCE"
#                 if prev_status and prev_status.lower() != "nan":
#                     if tag not in prev_status:
#                         ri_line_row[status_idx] = f"{prev_status}, {tag}"
#                 else:
#                     ri_line_row[status_idx] = tag
#
#             ri_line = "\t".join(ri_line_row)
#
#             # Write
#             new_out_str = ", ".join(new_evs_out)  # WITHOUT ORIGIN
#             new_rep_str = ", ".join(new_evs_rep)  # WITH ORIGIN
#             new_count = str(len(new_evs_rep))
#
#             f_out.write(ri_line + "\t" + new_out_str + "\n")
#             f_rep.write(ri_line + "\t" + new_rep_str + "\t" + new_count + "\n")
#
#     print("Finished")
#     print(f"Output (without ORIGIN):  {output_file_path}")
#     print(f"Report (with ORIGIN):    {report_output_file_path}")
#
#
# if __name__ == "__main__":
#     main()
"""Identify new HT-binding evidences from the unified RI→peaks mapping output.

Reads the unified TSV produced by the RI→HT peaks mapping step and flags which
HT evidences are NEW relative to the existing RI/site evidences.

Outputs:
- ../RawData/New_ev_RIs_mapped.tsv          → new evidences WITHOUT ORIGIN (EVIDENCE:PMID)
- ../RawData/New_ev_RIs_mapped_report.tsv   → new evidences WITH ORIGIN (EVIDENCE:PMID:ORIGIN) + New Count
"""

# standard
import os
import re
import sys
from typing import List

# thirdparty
import pandas as pd

# local
from libs import arguments


def print_progress(current: int, total: int, label: str, bar_length: int = 40) -> None:
    """
    Displays a real-time progress bar in the console, updating on the same line.
    """
    fraction = current / total if total else 1
    filled = int(bar_length * fraction)
    bar = "█" * filled + "-" * (bar_length - filled)
    percent = int(fraction * 100)
    sys.stdout.write(f"\r{label}: |{bar}| {percent}% ({current}/{total})")
    sys.stdout.flush()


def parse_ht_evidences(cell: str) -> List[str]:
    """Return list of HT evidences (strings without parentheses)."""
    if not isinstance(cell, str) or cell.strip() == "" or cell.lower() == "nan":
        return []
    items = re.findall(r"\((.*?)\)", cell)
    return items if items else [cell]


def main() -> None:
    print("Start")

    # 1) Args + pandas opts
    args = arguments.load()
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.max_rows", 50)

    # I/O (from CLI arguments)
    INPUT_DIR = args.output
    OUTPUT_DIR = args.output

    ri_mapped_file_path = os.path.join(INPUT_DIR, "Classical_confirmed_Strong_HT_mapped.tsv")
    output_file_path = os.path.join(OUTPUT_DIR, "New_ev_RIs_mapped.tsv")               # WITHOUT ORIGIN
    report_output_file_path = os.path.join(OUTPUT_DIR, "New_ev_RIs_mapped_report.tsv") # WITH ORIGIN

    # 2) Read + sanitize
    df = pd.read_csv(ri_mapped_file_path, sep="\t", comment="#", header=0)
    df.rename(columns=lambda c: c.strip(), inplace=True)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # ---- Normalized column names (no legacy compat needed) ----
    COL_TFRS = "site_evidence"
    COL_RI = "ri_evidence"
    COL_HT = "Evidence;Reference"
    COL_STATUS = "STATUS"

    if COL_HT not in df.columns:
        raise KeyError("Missing 'Evidence;Reference' column in mapped input.")

    # Progress setup
    total_rows = len(df.index)
    processed = 0
    label = "Scanning RIs for NEW HT evidences"

    # 4) Write outputs
    with open(output_file_path, "w", encoding="utf-8") as f_out, \
         open(report_output_file_path, "w", encoding="utf-8") as f_rep:

        base_header = "\t".join(df.columns.tolist())
        extra_name = "New (Evidence:reference)"     # WITHOUT ORIGIN
        f_out.write(base_header + "\t" + extra_name + "\n")
        f_rep.write(base_header + "\t" + extra_name + "\tNew Count\n")

        print("RIs Mapped shape")
        print(df.shape)

        # 3) Iterate rows
        for _, row in df.iterrows():
            # Strings for comparison
            tfrs_evidence = str(row.get(COL_TFRS, "") or "")
            ri_evidence   = str(row.get(COL_RI, "")   or "")
            ht_ev_str     = str(row.get(COL_HT, "")   or "")

            # Parse HT evidences
            ht_items = parse_ht_evidences(ht_ev_str)

            new_evs_out: List[str] = []  # WITHOUT ORIGIN -> "(EVIDENCE:PMID)"
            new_evs_rep: List[str] = []  # WITH ORIGIN    -> "(EVIDENCE:PMID:ORIGIN)"

            for item in ht_items:
                parts = [p.strip() for p in item.split(";")]
                code = parts[0] if parts else ""

                # "New" if evidence CODE not present in site/RI evidences
                if code and (code not in tfrs_evidence) and (code not in ri_evidence):
                    # report: keep ORIGIN (all segments), normalize ; -> :
                    new_evs_rep.append("(" + item.replace(";", ":") + ")")

                    # output: only EVIDENCE:PMID (first two segments)
                    if len(parts) >= 2:
                        new_evs_out.append("(" + parts[0] + ":" + parts[1] + ")")
                    else:
                        new_evs_out.append("(" + item.replace(";", ":") + ")")

            # Extend STATUS if applicable
            ri_line_row = [str(v) for v in row.values]
            if new_evs_rep:
                status_idx = df.columns.get_loc(COL_STATUS)
                prev_status = ri_line_row[status_idx]
                tag = "RI_WITH_NEW_EVIDENCE"
                if prev_status and prev_status.lower() != "nan":
                    if tag not in prev_status:
                        ri_line_row[status_idx] = f"{prev_status}, {tag}"
                else:
                    ri_line_row[status_idx] = tag

            ri_line = "\t".join(ri_line_row)

            # Write
            new_out_str = ", ".join(new_evs_out)  # WITHOUT ORIGIN
            new_rep_str = ", ".join(new_evs_rep)  # WITH ORIGIN
            new_count = str(len(new_evs_rep))

            f_out.write(ri_line + "\t" + new_out_str + "\n")
            f_rep.write(ri_line + "\t" + new_rep_str + "\t" + new_count + "\n")

            # ---- progress update (visual feedback only) ----
            processed += 1
            # actualiza en cada iteración; si quieres menos “ruido”, lo podemos hacer cada N filas
            print_progress(processed, total_rows, label)

    # finish progress line
    if total_rows:
        sys.stdout.write("\n")
        sys.stdout.flush()

    print("Finished")
    print(f"Output (without ORIGIN):  {output_file_path}")
    print(f"Report (with ORIGIN):    {report_output_file_path}")


if __name__ == "__main__":
    main()
