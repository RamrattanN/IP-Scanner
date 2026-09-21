from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .api import router as api_router
from .storage import get_app_data_dir, ensure_history_file
from .logging_config import setup_logging

app = FastAPI(title="Ramrattan IP Scanner", version="1.0.0")

# Prepare storage and logging on import
APP_DATA_DIR = get_app_data_dir()
ensure_history_file(APP_DATA_DIR)
setup_logging(APP_DATA_DIR)

# API
app.include_router(api_router, prefix="/api")

# Static UI
ui_dir = Path(__file__).parent / "ui"
app.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")
