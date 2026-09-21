from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .api import router as api_router
from .storage import (
    ensure_history_file,
    ensure_inventory_file,
    get_app_data_dir,
    load_history,
    load_inventory,
    save_inventory,
)
from .inventory import seed_inventory_from_history
from .logging_config import setup_logging

app = FastAPI(title="Ramrattan IP Scanner", version="1.0.0")

# Prepare storage and logging on import
APP_DATA_DIR = get_app_data_dir()
ensure_history_file(APP_DATA_DIR)
ensure_inventory_file(APP_DATA_DIR)
inventory = load_inventory(APP_DATA_DIR)
seeded_inventory = seed_inventory_from_history(inventory, load_history(APP_DATA_DIR))
if seeded_inventory != inventory:
    save_inventory(APP_DATA_DIR, seeded_inventory)
setup_logging(APP_DATA_DIR)

# API
app.include_router(api_router, prefix="/api")

# Static UI
ui_dir = Path(__file__).parent / "ui"
app.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")
