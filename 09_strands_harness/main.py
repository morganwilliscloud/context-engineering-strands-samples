"""Final talk demo: assemble the investigation agent with Strands Harness.

Run from this sample directory so built-in file tools have a clear workspace.
The evidence tools return synthetic data. Session and memory files stay local.
"""

import argparse
from pathlib import Path

from strands_harness import create_harness

from sample_support import get_service_config, get_service_logs, make_model, run_turns

HERE = Path(__file__).resolve().parent


def create_agent(model=None, *, state_dir=None, session_id=None):
    state_dir = Path(state_dir) if state_dir else HERE / ".agent"
    session = {"dir": str(state_dir / "sessions")}
    if session_id:
        session["id"] = session_id
    return create_harness(
        model=model if model is not None else make_model(),
        instructions=(
            "Investigate the synthetic checkout incident using the supplied evidence tools. "
            "Return a concise diagnosis, evidence, and a proposed next step. "
            "Do not change configuration, execute a rollback, or write files for this demo."
        ),
        tools=[get_service_logs, get_service_config],
        session=session,
        memory={"dir": str(state_dir / "memory")},
        callback_handler=None,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", help="Reuse this ID to resume a saved conversation")
    parser.add_argument(
        "--state-dir", type=Path, help="Separate local session and memory directory"
    )
    args = parser.parse_args()
    run_turns(
        create_agent(session_id=args.session_id, state_dir=args.state_dir),
        [
            (
                "Checkout is returning payment timeouts. Investigate the logs and configuration. "
                "Use a subagent for the log investigation, then give me a concise operator handoff."
            ),
            "What exact change should an operator consider, and how should they verify recovery?",
        ],
    )
