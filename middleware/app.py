import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import nest_asyncio
import uvicorn
from dotenv import load_dotenv

from middleware.api.factory import create_app
from middleware.common.app_constants import APP_NAME

load_dotenv()
nest_asyncio.apply()

app = create_app()


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Run the {APP_NAME} API")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    args = parser.parse_args()
    uvicorn.run("middleware.app:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
