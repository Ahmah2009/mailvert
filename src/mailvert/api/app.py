from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from mailvert import __version__
from mailvert.api.routes import router
from mailvert.config import settings
from mailvert.logging import configure_logging

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="mailvert",
        description="Async email address verification — syntax, MX, SMTP deliverability, catch-all & disposable detection.",
        version=__version__,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": f"internal error: {exc}"})

    return app


app = create_app()
