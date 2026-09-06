import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() and (parent / "package.json").exists():
            return parent
    return here.parents[2]


REPO_ROOT = _repo_root()
LOCAL_DEPLOY_DIR = REPO_ROOT / "runtime-data" / "local-deploy"
DEFAULT_SQLITE_URL = f"sqlite:///{(LOCAL_DEPLOY_DIR / 'your_next_travel.db').as_posix()}"


def database_url() -> str:
    raw = (os.getenv("DATABASE_URL") or "").strip()
    if not raw:
        return DEFAULT_SQLITE_URL
    if raw.startswith("postgres://"):
        return "postgresql+psycopg://" + raw[len("postgres://") :]
    if raw.startswith("postgresql://") and "+psycopg" not in raw:
        return "postgresql+psycopg://" + raw[len("postgresql://") :]
    if raw.startswith("sqlite:///"):
        path = raw[len("sqlite:///") :]
        if path.startswith("./") or not path.startswith("/"):
            return f"sqlite:///{(REPO_ROOT / path.lstrip('./')).as_posix()}"
    return raw


def is_sqlite(url: str | None = None) -> bool:
    return (url or database_url()).startswith("sqlite")


def sqlite_path(url: str | None = None) -> str:
    resolved = url or database_url()
    if not resolved.startswith("sqlite:///"):
        raise ValueError("Not a SQLite URL")
    return resolved[len("sqlite:///") :]
