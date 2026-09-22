"""Cross-platform desktop controller for the local IP Scanner service."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
import webbrowser

from network_scanner import __version__

APP_NAME = "IP Scanner"
DEFAULT_PORT = 8000
DATA_DIR_ENV = "IP_SCANNER_DATA_DIR"
_SERVICE_LOG_HANDLE = None
logger = logging.getLogger(__name__)


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def available_port(preferred: int = DEFAULT_PORT) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            probe.bind(("127.0.0.1", 0))
            return int(probe.getsockname()[1])


def service_command(
    port: int,
    data_dir: Path,
    *,
    parent_pid: int | None = None,
) -> list[str]:
    args = ["--service", "--port", str(port), "--data-dir", str(data_dir)]
    if parent_pid is not None:
        args.extend(["--parent-pid", str(parent_pid)])
    if is_frozen():
        return [sys.executable, *args]
    return [sys.executable, "-m", "network_scanner.desktop", *args]


def service_is_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/api/ping", timeout=0.5) as response:
            return response.status == 200
    except Exception:
        return False


def ensure_service_output(data_dir: Path) -> None:
    global _SERVICE_LOG_HANDLE
    if sys.stdout is None:
        logs = data_dir / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        _SERVICE_LOG_HANDLE = (logs / "desktop.log").open("a", encoding="utf-8", buffering=1)
        sys.stdout = _SERVICE_LOG_HANDLE
    if sys.stderr is None:
        sys.stderr = sys.stdout


def ensure_file_descriptor_budget(minimum: int = 1024) -> None:
    """Raise a low Finder-launch descriptor limit when macOS permits it."""
    if os.name == "nt":
        return
    try:
        import resource

        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target = min(max(soft, minimum), hard)
        if target > soft:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
    except (ImportError, OSError, ValueError):
        logger.exception("Unable to raise the open-file limit")


async def _serve(port: int, parent_pid: int | None) -> None:
    import psutil
    import uvicorn
    from network_scanner.app import app

    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    )

    async def watch_parent() -> None:
        if parent_pid is None:
            return
        while not server.should_exit:
            await asyncio.sleep(1)
            if not psutil.pid_exists(parent_pid):
                logger.warning("Desktop controller %s exited; stopping service", parent_pid)
                server.should_exit = True
                return

    watcher = asyncio.create_task(watch_parent()) if parent_pid is not None else None
    try:
        await server.serve()
    finally:
        if watcher is not None:
            watcher.cancel()
            try:
                await watcher
            except asyncio.CancelledError:
                pass


def run_service(port: int, data_dir: Path, parent_pid: int | None = None) -> None:
    os.environ[DATA_DIR_ENV] = str(data_dir)
    ensure_service_output(data_dir)
    ensure_file_descriptor_budget()
    asyncio.run(_serve(port, parent_pid))


class InstanceLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write("0")
            self.handle.flush()
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.handle.close()
            self.handle = None
            return False
        return True

    def release(self) -> None:
        if not self.handle:
            return
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            self.handle = None


def existing_url(data_dir: Path) -> str | None:
    try:
        state = json.loads((data_dir / "instance.json").read_text(encoding="utf-8"))
        url = str(state["url"])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return url if service_is_ready(url) else None


def run_controller(requested_port: int, data_dir: Path) -> None:
    import tkinter as tk
    from tkinter import messagebox

    data_dir.mkdir(parents=True, exist_ok=True)
    lock = InstanceLock(data_dir / "instance.lock")
    if not lock.acquire():
        url = existing_url(data_dir)
        if url:
            webbrowser.open(url)
        else:
            messagebox.showinfo(APP_NAME, "IP Scanner is already starting or running.")
        return

    port = available_port(requested_port)
    url = f"http://127.0.0.1:{port}"
    state_path = data_dir / "instance.json"
    logs = data_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log_handle = (logs / "desktop.log").open("a", encoding="utf-8")
    child_env = os.environ.copy()
    child_env[DATA_DIR_ENV] = str(data_dir)
    popen_kwargs: dict[str, object] = {}
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    child = subprocess.Popen(
        service_command(port, data_dir, parent_pid=os.getpid()),
        env=child_env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        **popen_kwargs,
    )
    state_path.write_text(
        json.dumps(
            {
                "url": url,
                "controller_pid": os.getpid(),
                "service_pid": child.pid,
            }
        ),
        encoding="utf-8",
    )

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("560x310")
    root.resizable(False, False)
    root.configure(background="#F3F7FA")
    font = "Segoe UI" if os.name == "nt" else "Helvetica Neue"
    tk.Label(root, text=APP_NAME, font=(font, 24, "bold"), foreground="#173F63", background="#F3F7FA").pack(pady=(30, 6))
    tk.Label(root, text="Local network discovery with manual and automatic scans.", font=(font, 12), foreground="#425466", background="#F3F7FA").pack()
    status_text = tk.StringVar(value="Starting the local scanner...")
    tk.Label(root, textvariable=status_text, font=(font, 11), foreground="#2F78B8", background="#F3F7FA").pack(pady=(22, 16))
    buttons = tk.Frame(root, background="#F3F7FA")
    buttons.pack()
    open_button = tk.Button(buttons, text="Open IP Scanner", command=lambda: webbrowser.open(url), state="disabled", width=20, pady=8)
    open_button.grid(row=0, column=0, padx=8)

    def stop_child() -> None:
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
        log_handle.close()
        state_path.unlink(missing_ok=True)
        lock.release()

    def quit_app() -> None:
        if messagebox.askokcancel(APP_NAME, "Stop automatic scans and quit IP Scanner?"):
            stop_child()
            root.destroy()

    tk.Button(buttons, text="Quit IP Scanner", command=quit_app, width=20, pady=8).grid(row=0, column=1, padx=8)
    tk.Label(root, text=f"Version {__version__}  |  Data folder: {data_dir}", font=(font, 9), foreground="#66788A", background="#F3F7FA", wraplength=520).pack(pady=(24, 0))
    browser_opened = False

    def poll_service() -> None:
        nonlocal browser_opened
        if child.poll() is not None:
            status_text.set("The scanner stopped unexpectedly.  Review desktop.log for details.")
            return
        if service_is_ready(url):
            status_text.set("IP Scanner is running.  Automatic scans use the schedule in the dashboard.")
            open_button.configure(state="normal")
            if not browser_opened:
                browser_opened = True
                webbrowser.open(url)
        root.after(750, poll_service)

    root.protocol("WM_DELETE_WINDOW", quit_app)
    root.after(250, poll_service)
    try:
        root.mainloop()
    finally:
        if lock.handle:
            stop_child()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog=APP_NAME)
    parser.add_argument("--service", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--data-dir")
    parser.add_argument("--parent-pid", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else Path.home() / "Documents" / "Network Scanner"
    if args.service:
        run_service(args.port, data_dir, args.parent_pid)
    else:
        run_controller(args.port, data_dir)


if __name__ == "__main__":
    main()
