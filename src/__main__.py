"""Main entry point for Meta MCP Server."""

import asyncio

from .logging_config import logger
from .server import run_server


def main() -> None:
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
