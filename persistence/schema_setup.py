from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from common.log import get_logger
from persistence.settings import REPO_ROOT, database_url, is_sqlite, sqlite_path

logger = get_logger("persistence.schema")


def _alembic_config() -> Config:
    ini_path = REPO_ROOT / "persistence" / "alembic.ini"
    config = Config(str(ini_path))
    config.set_main_option("script_location", str(REPO_ROOT / "persistence"))
    config.set_main_option("sqlalchemy.url", database_url())
    return config


def upgrade_schema() -> str:
    url = database_url()
    if is_sqlite(url):
        Path(sqlite_path(url)).parent.mkdir(parents=True, exist_ok=True)
    config = _alembic_config()
    command.upgrade(config, "head")
    head = current_revision()
    logger.info("schema upgraded url=%s revision=%s", url, head)
    return head


def current_revision() -> str:
    engine = create_engine(database_url())
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current = context.get_current_revision()
    script = ScriptDirectory.from_config(_alembic_config())
    heads = script.get_heads()
    return current or (heads[0] if heads else "empty")


def main() -> None:
    revision = upgrade_schema()
    print(f"Your Next Travel schema is ready (revision={revision})")


if __name__ == "__main__":
    main()
