# standard

# thirdparty
import pandas as pd

# local


def load_dataframe(path, sheet_name="DATASET", comment='#', header=0):
    try:
        loaded_dataframe = pd.read_excel(
            path,
            sheet_name=sheet_name,
            comment=comment,
            header=header
        )
    except FileNotFoundError:
        return None
    return loaded_dataframe
