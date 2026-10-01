"""Pass a named Agent directly as a tool, with its own context manager.

The parent gets the subagent's final answer, so keep that answer concise. This
is context separation, not a security boundary. The SDK's default Agent-as-tool
adapter starts each call from the child's initial conversation state.
"""

from strands import Agent

from sample_support import get_service_logs, make_model, run_turns


def create_agent(model=None):
    model = model if model is not None else make_model()
    log_analyzer = Agent(
        model=model,
        name="analyze_logs",
        description="Investigate checkout service logs and return a concise diagnosis.",
        context_manager="auto",
        tools=[get_service_logs],
        system_prompt=(
            "Read the logs, retrieving offloaded evidence when needed. Return a short "
            "diagnosis with key evidence. Keep bulk logs out of your final answer."
        ),
        callback_handler=None,
    )
    return Agent(
        model=model,
        context_manager="auto",
        tools=[log_analyzer],
        system_prompt="Delegate log investigation, then turn the diagnosis into an operator handoff.",
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(
        create_agent(),
        [
            "Investigate checkout payment errors using analyze_logs.",
            "Based on the findings, what should an operator verify before rolling back?",
        ],
    )
