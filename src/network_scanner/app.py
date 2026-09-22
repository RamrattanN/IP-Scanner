from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .api import router as api_router
from .storage import get_app_data_dir, ensure_history_file
from .logging_config import setup_logging
from .scan_coordinator import coordinator

# Prepare storage and logging on import
APP_DATA_DIR = get_app_data_dir()
ensure_history_file(APP_DATA_DIR)
setup_logging(APP_DATA_DIR)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await coordinator.start_scheduler(APP_DATA_DIR)
    try:
        yield
    finally:
        await coordinator.stop_scheduler()


app = FastAPI(title="Ramrattan IP Scanner", version="1.1.1", lifespan=lifespan)

# API
app.include_router(api_router, prefix="/api")

# Static UI
ui_dir = Path(__file__).parent / "ui"
app.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")
