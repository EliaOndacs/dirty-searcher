import click
from db import db_exists, getFiles, useDatabase, AbstractTable  # pack: ignore
import os, logging
import fuzzyfinder  # type: ignore


@click.group()
def main():
    "a cli tool for indexing files in a directory and searching in them"
    pass


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@main.command
def index():
    "Index all the text files in cwd"
    db = useDatabase()
    tb_files: AbstractTable = db["files"]
    tb_files.delete()

    entries_to_insert = []

    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename == "index.db":
                continue

            path = os.path.join(dirpath, filename)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                content = ""
                logger.warning(
                    f"Failed to read the content of {path!r}: {e}. Using an empty string instead."
                )

            entries_to_insert.append((path, filename, content))
            print(f"[+] Added {path!r} to the index")

    # Insert all entries at once if the insert method supports it
    if entries_to_insert:
        tb_files.insertmany(
            entries_to_insert
        )  # Assuming insert_many is a method that handles batch inserts


@main.command
@click.option(
    "--raw", is_flag=True, help="only show the path of where the query was found."
)
@click.argument("query")
def query(query: str, raw: bool):
    "search for a query in the index"
    if not db_exists():
        print("no database found, run `index` first")
        return

    db = useDatabase()
    files = getFiles(db)
    for file in files:
        if (query in file[1]) or (query in file[2]):
            if not raw:
                print("[+] found {file[0]} with query {query!r}")
            else:
                print(file[0])


@main.command
def list():
    "list all the indexed queries (warning: only recommended for small indexes)"
    if not db_exists():
        print("no database found, run `index` first")
        return
    db = useDatabase()
    files = getFiles(db)
    for index, file in enumerate(files):
        print(f"[{index}] {file[0]!r} - {file[1]!r} - '{file[2][:10]}...'")


@main.command
@click.option(
    "--raw", is_flag=True, help="only show the path of where the query was found."
)
@click.argument("filename")
def query_filename(filename: str, raw: bool):
    "fuzzy find in the filenames only"
    if not db_exists():
        print("no database found, run `index` first")
        return
    db = useDatabase()
    files = getFiles(db)
    filenames = []
    for file in files:
        filenames.append(file[1])
    result = fuzzyfinder.main.fuzzyfinder(filename, filenames)
    for index, _ in enumerate(result):
        path = files[index][0]
        if not raw:
            print(f"- {path!r}")
        else:
            print(path)


if __name__ == "__main__":
    main()
# end main
