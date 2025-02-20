import os
import sqllex as sql  # type: ignore
from sqllex.core.entities.abc.sql_database import AbstractTable  # type: ignore


def db_exists():
    return os.path.exists("index.db")


def useDatabase() -> sql.SQLite3x:
    "get the database or create it if it doesn't exist"
    return sql.SQLite3x(
        "index.db",
        {"files": {"path": sql.PATH, "title": sql.TEXT, "content": sql.TEXT}},
    )


def getFiles(db: sql.SQLite3x):
    "get all the files and their necessary information from the database"
    files = db["files"]
    data = files.select("*")
    return data
