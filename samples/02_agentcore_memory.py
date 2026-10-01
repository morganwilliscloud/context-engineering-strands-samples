"""Compatibility entry point for 08_agentcore_memory/main.py. Pass remember or recall as the CLI argument."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "08_agentcore_memory" / "main.py"),
        run_name="__main__",
    )
