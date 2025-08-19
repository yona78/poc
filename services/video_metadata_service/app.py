"""FastAPI application for video metadata management."""

from fastapi import FastAPI

from .controller import router
from .dependencies import init_app

app = FastAPI(title="Video Metadata Service")
app.include_router(router)


@app.on_event("startup")
def startup_event() -> None:
    """Wire dependencies and start background consumers."""
    init_app(app)
