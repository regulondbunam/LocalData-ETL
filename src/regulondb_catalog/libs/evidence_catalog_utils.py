import pandas
import json
import re


def get_data_frame(
    filename: str,
    load_sheet: str = "Evidence Catalog",
    rows_to_skip: int = 0
) -> pandas.DataFrame:
    """
    Load an Excel sheet into a pandas DataFrame.

    Parameters
    ----------
    filename : str
        Path to the Excel file.
    load_sheet : str, optional
        Sheet name to be loaded. Default is "Evidence Catalog".
    rows_to_skip : int, optional
        Number of initial rows to skip when reading the sheet. Default is 0.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the content of the specified sheet.

    Notes
    -----
    - Rows containing "#" as comment markers will be ignored.
    - Cells with '-' will be interpreted as NaN.
    """
    evidence_df = pandas.read_excel(
        filename,
        sheet_name=load_sheet,
        skiprows=rows_to_skip,
        comment="#",
        na_values="-"
    )
    return evidence_df


def get_json_from_data_frame(data_frame: pandas.DataFrame) -> dict:
    """
    Convert a pandas DataFrame into a JSON-compatible Python dictionary.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing evidence catalog metadata.

    Returns
    -------
    dict
        A list-like dictionary representing the DataFrame rows.

    Notes
    -----
    - The JSON conversion uses `orient='records'`, meaning each row becomes
      a dictionary within a list.
    - Substrings of the form '(digit)' are removed using regex before JSON parsing.
    """
    string_json = data_frame.to_json(orient="records")
    string_json = re.sub(r"\([0-9]\)\s*", "", string_json)
    return json.loads(string_json)


def get_evidences_catalog(filename: str) -> dict:
    """
    Load the evidence catalog Excel file and convert it into a structured dictionary.

    Parameters
    ----------
    filename : str
        Path to the evidence catalog Excel file.

    Returns
    -------
    dict
        Evidence catalog represented as a list-like dictionary structure.

    Notes
    -----
    - Internally combines `get_data_frame()` and `get_json_from_data_frame()`.
    - No validation is performed on expected columns; the Excel sheet must have
      the correct structure used in RegulonDB evidence catalogs.
    """
    data_frame = get_data_frame(filename)
    data_frame_json = get_json_from_data_frame(data_frame)
    return data_frame_json
