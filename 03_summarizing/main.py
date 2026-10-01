"""Summarize older context with the experimental Offload strategy API.

The default is the slide's 85% threshold. --demo-pressure uses a small local
context budget and a fixed long transcript to exercise summarization sooner.
It changes the SDK's budget, not the underlying model's actual context capacity.
"""

import argparse

from strands import Agent
from strands.experimental.context_manager import Offload

from sample_support import checkout_logs, make_model, run_turns


def create_agent(model=None, *, demo_pressure=False):
    model = (
        model
        if model is not None
        else make_model(
            **({"context_window_limit": 12000, "max_tokens": 1024} if demo_pressure else {})
        )
    )
    return Agent(
        model=model,
        context_manager={
            "strategies": [Offload.summarize("*").when(utilization=0.85, preserve_recent=4)],
            "stash": False,
        },
        system_prompt="Summarize incident evidence concisely. Preserve exact configuration values.",
        callback_handler=None,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-pressure", action="store_true")
    args = parser.parse_args()
    agent = create_agent(demo_pressure=args.demo_pressure)
    if args.demo_pressure:
        # Seed older messages so they are eligible for compression, outside the recent tail.
        agent.messages.extend(
            [
                {
                    "role": "user",
                    "content": [{"text": "Investigate the archived checkout incident."}],
                },
                {"role": "assistant", "content": [{"text": "Please provide the logs."}]},
                {"role": "user", "content": [{"text": checkout_logs()}]},
                {
                    "role": "assistant",
                    "content": [{"text": "The timeout changed from 2000 to 200 ms."}],
                },
                {"role": "user", "content": [{"text": "Check the downstream latency."}]},
                {"role": "assistant", "content": [{"text": "Payment API p95 latency is 620 ms."}]},
                {"role": "user", "content": [{"text": "Check database utilization."}]},
                {"role": "assistant", "content": [{"text": "Database utilization is normal."}]},
            ]
        )
    run_turns(
        agent,
        [
            "The payment timeout is 200 ms and downstream p95 is 620 ms. Explain the mismatch.",
            "Give the operator a concise incident handoff, using only the evidence you have.",
        ],
    )
    print("Inspect the retained messages to see whether summarization occurred in this run.")
