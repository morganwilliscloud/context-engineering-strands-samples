"""Keep a bounded recent conversation with the traditional conversation manager.

This is an alternative to the new context-manager pipeline. Window reductions
respect message/tool boundaries, so the resulting count is not always exactly N.
"""

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager

from sample_support import make_model, run_turns


def create_agent(model=None):
    return Agent(
        model=model if model is not None else make_model(),
        context_manager=False,
        conversation_manager=SlidingWindowConversationManager(
            window_size=6,
            should_truncate_results=True,
            per_turn=True,
        ),
        system_prompt="You are an incident assistant. Reply to each update in one sentence.",
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(
        create_agent(),
        [
            "The checkout incident started at 12:03 UTC.",
            "Database connection pool utilization is normal.",
            "CPU utilization is also normal.",
            "Errors affect calls to payment-api.",
            "Payment API p95 latency is 620 milliseconds.",
            "The configured payment timeout was reduced to 200 milliseconds.",
            "What evidence is still in your conversation? Don't guess missing details.",
        ],
    )
