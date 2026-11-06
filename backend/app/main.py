"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title="Document Copilot API",
    version="0.1.0",
    debug=settings.app_env == "development",
)
