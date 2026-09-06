import argparse
import os

import nest_asyncio
import uvicorn
from dotenv import load_dotenv

from api.factory import create_app
from common.app_constants import APP_NAME

load_dotenv()
nest_asyncio.apply()

app = create_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run the {APP_NAME} API")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    args = parser.parse_args()
    uvicorn.run("app:app", host=args.host, port=args.port, reload=True)
