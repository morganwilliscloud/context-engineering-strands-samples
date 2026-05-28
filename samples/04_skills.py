"""
Context Engineering Strategy: Select (Instructions)

Skills use progressive disclosure — only metadata is in the prompt upfront
(~100 tokens per skill). Full instructions are loaded on demand when the
agent decides it needs them.

Install:
    pip install strands-agents
"""

from strands import Agent
from strands.vended_plugins.skills import AgentSkills

agent = Agent(
    system_prompt="You are a helpful assistant.",
    plugins=[AgentSkills(skills=["./skills/"])],
)

# Metadata injected into prompt
# Full instructions loaded on demand
agent("Deploy the staging environment to production")
