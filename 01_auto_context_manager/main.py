"""One-line automatic context management, introduced after custom strategies in the talk.

Auto offloads tool results above 1,500 tokens to a stash, retaining a 750-token
preview. It summarizes at 85% utilization and preserves four recent messages.
A short run may demonstrate offloading without reaching summarization pressure.
"""

from strands import Agent

from sample_support import get_service_logs, make_model, run_turns


def create_agent(model=None):
    return Agent(
        model=model if model is not None else make_model(),
        context_manager="auto",
        tools=[get_service_logs],
        system_prompt=(
            "Investigate the synthetic checkout incident. If a tool result is offloaded, "
            "retrieve the relevant evidence before drawing conclusions. Return a brief diagnosis."
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(
        create_agent(),
        [
            "Read checkout logs. What changed immediately before the payment timeouts?",
            "Which evidence supports that diagnosis, and what should an operator check first?",
        ],
    )
