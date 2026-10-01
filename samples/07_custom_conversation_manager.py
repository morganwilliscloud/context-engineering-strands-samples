"""Compatibility entry point for 04_context_offloading/main.py. The earlier hand-written eviction manager is replaced by SDK strategies that preserve valid message structure."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "04_context_offloading" / "main.py"),
        run_name="__main__",
    )
