import sqlite3
from pathlib import Path

from middleware.persistence.settings import database_url, is_sqlite, sqlite_path


def build_checkpointer():
    url = database_url()
    if is_sqlite(url):
        from langgraph.checkpoint.sqlite import SqliteSaver

        db_path = sqlite_path(url)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(connection)
        checkpointer.setup()
        return checkpointer

    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg import Connection
    from psycopg.rows import dict_row

    raw = url.replace("postgresql+psycopg://", "postgresql://", 1)
    connection = Connection.connect(raw, autocommit=True, row_factory=dict_row)
    checkpointer = PostgresSaver(connection)
    checkpointer.setup()
    return checkpointer
