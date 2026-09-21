"""Build a macOS icon source from the Ramrattan logo."""

from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "src" / "network_scanner" / "ui" / "ramrattan-logo.png"
target = root / "build" / "macos-icon" / "source.png"
target.parent.mkdir(parents=True, exist_ok=True)
logo = Image.open(source).convert("RGBA")
bounds = logo.getchannel("A").getbbox()
if bounds is None:
    raise ValueError("The Ramrattan logo contains no visible pixels.")
logo = logo.crop(bounds)
logo.thumbnail((860, 860), Image.Resampling.LANCZOS)
canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
canvas.alpha_composite(logo, ((1024 - logo.width) // 2, (1024 - logo.height) // 2))
canvas.save(target)
