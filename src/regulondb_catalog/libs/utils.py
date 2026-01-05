import os
import logging
import json


def set_log(log_path: str, log_name: str = "evidence.log") -> str:
    """
    Configure the logging output file for the evidence processing pipeline.

    Parameters
    ----------
    log_path : str
        Directory where the log file will be created. Must already exist.
    log_name : str, optional
        Name of the log file to generate. Default is "evidence.log".

    Returns
    -------
    str
        Full path to the generated log file.

    Raises
    ------
    IOError
        If `log_path` is not an existing directory.

    Notes
    -----
    - Logging is configured using `logging.basicConfig()` in write mode.
    - Log format includes level, timestamp, and message.
    - Subsequent calls to `basicConfig` will not override configuration unless
      the Python session is restarted.
    """
    if not os.path.isdir(log_path):
        raise IOError(
            f"{log_path} directory does not exist, please edit your log argument value"
        )

    log_path = os.path.join(log_path, log_name)

    logging.basicConfig(
        filename=log_path,
        format="%(levelname)s - %(asctime)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    return log_path


def create_json(data: dict, filename: str) -> None:
    """
    Write a Python object to a JSON file.

    Parameters
    ----------
    data : dict
        Python dictionary to serialize into JSON format.
    filename : str
        Output filename. If it does not end with '.json', the extension is appended automatically.

    Returns
    -------
    None

    Notes
    -----
    - JSON is written with an indentation of 2 spaces for readability.
    - A console message is printed with the final file path.
    """
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    with open(filename, "w") as fn:
        json.dump(data, fn, indent=2)

    print(f"JSON file created at:\n\t{filename}")
