"""Offload large tool results and summarize under pressure, matching slide 15.

Original results go to a local stash. The SDK adds retrieve_context so the agent
can read relevant content later. The 2,500/500 thresholds here are custom values;
auto mode uses 1,500/750. The strategy API remains experimental.
"""

from strands import Agent
from strands.experimental.context_manager import Offload
from strands.storage import LocalFileStorage

from sample_support import ROOT, get_service_logs, make_model, run_turns


def create_agent(model=None, *, stash_dir=None):
    storage = LocalFileStorage(str(stash_dir or ROOT / "artifacts" / "stash"))
    return Agent(
        model=model if model is not None else make_model(),
        context_manager={
            "strategies": [
                Offload.truncate("tool_results", {"preview_tokens": 500}).when(threshold=2500),
                Offload.summarize("*").when(utilization=0.85, preserve_recent=4),
            ],
            "stash": {"storage": storage},
        },
        tools=[get_service_logs],
        system_prompt=(
            "Investigate the synthetic checkout incident. Retrieve offloaded content "
            "when the preview does not contain the evidence needed for a diagnosis."
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(
        create_agent(),
        [
            "Read checkout logs and identify the configuration change before the payment failures.",
            "Retrieve evidence of the downstream latency and compare it with the configured timeout.",
        ],
    )
    print(f"Inspect offloaded artifacts in {ROOT / 'artifacts' / 'stash'}")
