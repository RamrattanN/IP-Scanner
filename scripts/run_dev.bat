@echo off
set PYTHONIOENCODING=utf-8
uvicorn network_scanner.app:app --reload
