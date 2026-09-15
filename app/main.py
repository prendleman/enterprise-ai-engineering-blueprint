"""ASGI entrypoint."""

import uvicorn

from app.api import app
from app.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)


if __name__ == "__main__":
    main()
