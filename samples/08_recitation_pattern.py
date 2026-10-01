"""Optional prompt technique: keep a short working plan in recent responses.

Restating a plan consumes tokens and may help some tasks; it does not guarantee
accuracy or override a model's attention behavior. System instructions do not
move into the middle simply because conversation history grows.
"""

from strands import Agent

from sample_support import get_service_config, make_model, run_turns


def create_agent(model=None):
    return Agent(
        model=model if model is not None else make_model(),
        context_manager="auto",
        tools=[get_service_config],
        system_prompt=(
            "You are an incident analyst. For this demo, begin each response with a short "
            "working plan: the goal, remaining checks, and the next step. Update it as "
            "evidence changes. Keep this to two sentences, followed by your findings. "
            "Use configuration evidence rather than guessing."
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(
        create_agent(),
        [
            "Investigate the synthetic checkout timeout configuration.",
            "What would you verify before proposing a rollback?",
        ],
    )
