"""The starting Agent: vended tools, with optional Exa search through MCP.

Run: python 00_coding_agent/main.py [--exa]
Web fetch reads a known URL. Exa adds search and receives the search queries.
"""

import argparse

from strands import Agent
from strands.tools.mcp import MCPClient
from strands.vended_tools import file_editor, shell, web_fetch

from sample_support import make_model, run_turns


def create_agent(model=None, *, exa=False):
    search = (
        MCPClient.load_servers({"mcpServers": {"exa": {"url": "https://mcp.exa.ai/mcp"}}})
        if exa
        else []
    )
    return Agent(
        model=model if model is not None else make_model(),
        system_prompt="You are a coding agent. Inspect evidence before proposing changes.",
        tools=[file_editor, shell, web_fetch, *search],
        callback_handler=None,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exa", action="store_true", help="Connect to Exa's hosted search MCP")
    args = parser.parse_args()
    prompt = (
        "Search for the Strands automatic context management documentation and explain its defaults."
        if args.exa
        else "Read https://strandsagents.com/docs/user-guide/sdk/context-management/built-in-modes/ "
        "and explain automatic context management. Do not change any files."
    )
    run_turns(create_agent(exa=args.exa), [prompt])
