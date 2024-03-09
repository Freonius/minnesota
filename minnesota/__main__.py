"""Minnesota"""

from fastapi.routing import APIRouter
from uvicorn import run as uvicorn_run
from .api import get_app
from .utils import get_args, load_types
from .logs import logger


def main() -> None:
    """Main."""
    try:
        routes, cwd, host, port, is_mock = get_args()
        app = get_app()
        for route in routes:
            logger.info(f"Loading routes from {route}")
            api_routes = load_types(
                APIRouter, instance=True, folder_name=str(route), cwd=str(cwd)
            )
            logger.info(f"Found {len(api_routes)} routes")
            for api_route in api_routes:
                app.include_router(api_route)
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Is mock: {is_mock}")
        uvicorn_run(app, host=host, port=port)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(exc)


if __name__ == "__main__":
    main()
