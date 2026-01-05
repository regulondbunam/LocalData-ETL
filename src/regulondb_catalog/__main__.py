import os
from typing import Any

from libs import utils
from libs import arguments as arguments_module
from libs import regulondb_catalog


def resolve_catalog_source(catalog: str) -> str:
    """
    Resolve the source of the catalog and always return a local file path.

    - If `catalog` is an existing path, it is returned as is.
    - Otherwise, a FileNotFoundError is raised.
    """
    if os.path.exists(catalog):
        return catalog

    raise FileNotFoundError(
        f"Catalog '{catalog}' does not exist or is not a valid path."
    )


def run(args: Any) -> None:
    """
    Run the RegulonDB evidence catalog extraction process.

    Parameters
    ----------
    args : Any
        Object containing the command-line arguments, typically the result
        of `arguments_module.load()`. It must include at least:
        - catalog
        - log
        - new
        - update
        - unknwon
        - rules
        - url
        - database
        - organism
    """
    utils.set_log(args.log, "regulondb_evidence_catalog.log")

    catalog_path = resolve_catalog_source(args.catalog)

    print(f"Reading:\n\t{catalog_path}")

    regulondb_catalog.extract_process(
        catalog_path,
        args.new,
        args.update,
        args.unknwon,
        args.rules,
        args.url,
        args.database,
        args.organism,
    )


def main() -> None:
    """Main entry point of the script."""
    cli_args = arguments_module.load()
    run(cli_args)


if __name__ == "__main__":
    main()
