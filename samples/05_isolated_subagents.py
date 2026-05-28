"""
Context Engineering Strategy: Isolate

Each sub-agent has its own scoped context — no cross-contamination.
The orchestrator passes only relevant context down and gets back
conclusions only. Each agent gets a focused context window.

Install:
    pip install strands-agents
"""

from strands import Agent

# Each agent has its own scoped context — no cross-contamination
research_agent = Agent(
    system_prompt="You are a research agent. Find sources and summarize findings.",
)

analysis_agent = Agent(
    system_prompt="You are a data analyst. Work only with the data provided.",
)

writer_agent = Agent(
    system_prompt="You are a technical writer. Use only the findings given to you.",
)

# Orchestrator passes scoped context, gets back conclusions only
orchestrator = Agent(
    system_prompt="Route tasks to specialized agents. Pass only relevant context.",
    tools=[research_agent, analysis_agent, writer_agent],
)

orchestrator("Write a report on the latest AI agent frameworks")
