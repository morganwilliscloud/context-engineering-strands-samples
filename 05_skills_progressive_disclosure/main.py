"""Use AgentSkills to discover skill metadata and load instructions on demand."""

from pathlib import Path

from strands import Agent, AgentSkills
from strands.vended_tools import file_editor, shell

from sample_support import make_model, run_turns

SKILLS = Path(__file__).resolve().parent / "skills"


def create_agent(model=None):
    return Agent(
        model=model if model is not None else make_model(),
        context_manager="auto",
        plugins=[AgentSkills(skills=str(SKILLS))],
        tools=[file_editor, shell],
        system_prompt=(
            "Activate the relevant skill before starting a specialized task. "
            "For the demo, review the supplied code and propose changes without editing files."
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(
        create_agent(),
        [
            (
                "Review this code with the code-review skill:\n"
                "def get_user(user_id):\n"
                '    return db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()'
            )
        ],
    )
