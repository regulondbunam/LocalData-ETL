import pandas
import json
import re


def get_data_frame(filename: str, load_sheet: str = "Evidence Catalog", rows_to_skip: int = 0) -> pandas.DataFrame:
    evidence_df = pandas.read_excel(
        filename, sheet_name=load_sheet, skiprows=rows_to_skip, comment='#', na_values='-')
    return evidence_df


def get_json_from_data_frame(data_frame: pandas.DataFrame) -> dict:
    string_json = data_frame.to_json(orient='records')
    string_json = re.sub(r'\([0-9]\)\s*', '', string_json)
    return json.loads(string_json)


def get_evidences_catalog(filename: str) -> dict:
    data_frame = get_data_frame(filename)
    data_frame_json = get_json_from_data_frame(data_frame)
    # print(data_frame_json)
    return data_frame_json
