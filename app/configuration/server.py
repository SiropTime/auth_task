"""Server configuration."""
import logging
from typing import TypeVar

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_prometheus import PrometheusMiddleware, metrics

from app.internal.pkg.middlewares.handle_http_exceptions import handle_api_exceptions
from app.internal.routes import __routes__
from app.pkg.models.base import BaseException

from .events import on_startup
from .logger import EndpointFilter

__all__ = ["Server"]

from app.pkg.jwt import JWT

FastAPIInstance = TypeVar("FastAPIInstance", bound="FastAPI")


class Server:
    """Register all requirements for correct work of server instance."""

    def __init__(self, app: FastAPI):
        self.__app = app
        self._register_containers(app)
        self._register_routes(app)
        self._register_events(app)
        self._register_middlewares(app)
        self._register_http_exceptions(app)
        self._register_jwt(app)

    def get_app(self) -> FastAPIInstance:
        """Get current application instance.

        Returns: ``FastAPI`` application instance.
        """
        return self.__app

    @staticmethod
    def _register_events(app: FastAPIInstance):
        """Register on startup events.

        Args:
            app: ``FastAPI`` application instance.

        Returns: None
        """

        app.on_event("startup")(on_startup)

    @staticmethod
    def _register_routes(app: FastAPIInstance) -> None:
        """Include routers in ``FastAPI`` instance from ``__routes__``.

        Args:
            app: ``FastAPI`` application instance.

        Returns: None
        """

        __routes__.register_routes(app)

    @staticmethod
    def _register_containers(app: FastAPIInstance):
        """Register services __service__ using dependency injection pattern.

        Args:
            app: ``FastAPI`` application instance.

        Returns: None
        """
        ...

    @staticmethod
    def _register_http_exceptions(app: FastAPIInstance):
        """Register http exceptions.

        FastAPIInstance handle BaseApiExceptions raises inside functions.

        Args:
            app: ``FastAPI`` application instance

        Returns: None
        """

        app.add_exception_handler(BaseException, handle_api_exceptions)

    @staticmethod
    def __register_cors_origins(app: FastAPIInstance):
        """Register cors origins."""

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def __register_prometheus(self, app: FastAPIInstance):
        """Register prometheus middleware."""

        metrics_endpoint = "/metrics"
        app.add_middleware(PrometheusMiddleware)
        app.add_route(metrics_endpoint, metrics)
        self.__filter_logs(metrics_endpoint)

    @staticmethod
    def _register_jwt(app: FastAPIInstance):
        """Register jwt handler to fast api context.

        Args:
            app: ``FastAPI`` application instance

        Returns: None
        """
        jwt = JWT()
        jwt.wire(
            packages=[
                "app.internal.routes",
                "app.pkg.jwt",
                "app.pkg.settings",
            ],
        )
        app.jwt = jwt

    def _register_middlewares(self, app):
        """Apply routes middlewares."""

        self.__register_cors_origins(app)
        self.__register_prometheus(app)

    @staticmethod
    def __filter_logs(endpoint: str):
        """Filter ignore /metrics in uvicorn logs."""
        logging.getLogger("uvicorn.access").addFilter(EndpointFilter(endpoint=endpoint))
