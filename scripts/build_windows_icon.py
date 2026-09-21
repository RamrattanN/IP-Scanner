"""Build a Windows icon from the Ramrattan logo."""

from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "src" / "network_scanner" / "ui" / "ramrattan-logo.png"
target = root / "build" / "windows-icon" / "IPScanner.ico"
target.parent.mkdir(parents=True, exist_ok=True)
logo = Image.open(source).convert("RGBA")
logo.thumbnail((210, 210), Image.Resampling.LANCZOS)
canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
canvas.alpha_composite(logo, ((256 - logo.width) // 2, (256 - logo.height) // 2))
canvas.save(target, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
