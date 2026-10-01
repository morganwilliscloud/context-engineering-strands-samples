"""Compatibility entry point for 03_summarizing/main.py."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "03_summarizing" / "main.py"), run_name="__main__"
    )
