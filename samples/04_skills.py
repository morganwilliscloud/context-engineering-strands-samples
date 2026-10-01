"""Compatibility entry point for 05_skills_progressive_disclosure/main.py."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "05_skills_progressive_disclosure" / "main.py"),
        run_name="__main__",
    )
