"""Get the app"""

from os import environ
from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from ..aws import load_secrets
from ..logs import logger


def get_app() -> FastAPI:
    """Get the app"""
    if environ.get("SECRET_NAME"):
        load_secrets()
    app: FastAPI = FastAPI()

    if __debug__:

        @app.exception_handler(StarletteHTTPException)
        async def starlette_http_exception_handler(
            request: Request, exc: StarletteHTTPException
        ) -> Response:
            """Handle starlette exceptions"""
            logger.error(request.url)
            return Response(content=str(exc), status_code=exc.status_code)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
        """Handle http exceptions"""
        logger.error(request.url)
        return Response(content=str(exc), status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception) -> Response:
        """Handle exceptions"""
        logger.error(request.url)
        logger.exception(exc)
        return Response(content="Internal Server Error", status_code=500)

    @app.get("/alive", response_model=str, tags=["healthcheck"])
    async def alive() -> Response:
        """Alive"""
        return Response(status_code=200, content="OK")

    if environ.get("VERSION_NAME"):

        @app.get("/version", response_model=str, tags=["healthcheck"])
        async def version() -> Response:
            """Version"""
            return Response(status_code=200, content=environ["VERSION_NAME"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            orig.strip() for orig in environ.get("ALLOWED_ORIGINS", "*").split(",")
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


__all__ = ["get_app"]
