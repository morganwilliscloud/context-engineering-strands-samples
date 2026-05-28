"""
Attention Manipulation: The Recitation Pattern

Exploit the attention U-curve by having the agent rewrite its plan
into recent context, keeping goals in the attention hot zone.

The problem: critical instructions in the system prompt (start of context)
get "lost in the middle" as conversation grows. The recitation pattern
forces the agent to periodically restate its plan, moving it to the END
of context where attention is highest.

Install:
    pip install strands-agents
"""

from strands import Agent

# --- The Recitation Pattern via System Prompt ---
# Instruct the agent to periodically restate its plan

agent = Agent(
    system_prompt="""You are a research analyst working on a multi-step report.

CRITICAL INSTRUCTION — RECITATION PATTERN:
Before EVERY response, restate your current plan in a <plan> block:
<plan>
- What is the overall goal
- What steps remain
- What you're doing right now
</plan>

This keeps your goals in your active attention as the conversation grows.
Do not skip this step, even if it feels redundant.

Your task: Research and compile a competitive analysis report.
Steps:
1. Identify the top 5 competitors
2. For each competitor, find their key differentiators
3. Summarize strengths and weaknesses
4. Write a final recommendation
""",
)

if __name__ == "__main__":
    # Turn 1: Agent restates plan before acting
    response = agent("Start the competitive analysis for our AI agent platform.")
    print(response)

    # Turn 10+: Even deep into the conversation, the plan is always
    # in recent context (end of the window) because the agent restates it.
    # Without recitation, the original instructions would be "lost in the middle."

    # --- Alternative: Hooks for Deterministic Recitation ---
    # Instead of relying on the model to remember to restate,
    # use a lifecycle hook to inject the plan before every model call.
    # This is "outside the prompt, outside the model's discretion."

    from strands.plugins import Plugin, hook
    from strands.hooks import BeforeModelCallEvent

    class RecitationPlugin(Plugin):
        """Inject the current plan into recent context before every model call."""

        name = "recitation"

        def __init__(self, plan: str):
            super().__init__()
            self.plan = plan

        @hook
        def inject_plan(self, event: BeforeModelCallEvent) -> None:
            """Add plan reminder to the end of messages (attention hot zone)."""
            reminder = {
                "role": "user",
                "content": [{"text": f"[SYSTEM REMINDER — Current plan:\n{self.plan}]"}],
            }
            # Inject as the last user message so it's at the END of context
            event.agent.messages.append(reminder)

    # Now the plan is ALWAYS in the attention hot zone,
    # regardless of whether the model "remembers" to restate it
    agent_with_hook = Agent(
        system_prompt="You are a research analyst.",
        plugins=[RecitationPlugin(plan="""
1. Identify top 5 competitors
2. Find key differentiators for each
3. Summarize strengths/weaknesses
4. Write final recommendation
""")],
    )
