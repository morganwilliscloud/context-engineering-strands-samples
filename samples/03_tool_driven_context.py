"""
Context Engineering Strategy: Select (Data)

Give the agent tools to pull data from knowledge bases (RAG),
APIs, and databases on demand. Each tool call brings focused,
relevant tokens at the moment they're needed.

Install:
    pip install strands-agents strands-agents-tools
"""

from strands import Agent, tool
from strands_tools import retrieve, http_request


@tool
def query_db(sql: str) -> str:
    """Run a read-only SQL query against the customer database.

    Args:
        sql: A SELECT query to run against the customers database.
    """
    # database lookup implementation
    ...


agent = Agent(
    system_prompt="You are a support agent.",
    tools=[retrieve, http_request, query_db],
)

# Relevant data pulled ON DEMAND
agent("Where's my order #12345?")
