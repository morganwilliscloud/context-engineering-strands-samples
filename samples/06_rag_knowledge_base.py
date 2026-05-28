"""
RAG with Amazon Bedrock Knowledge Bases

Use the built-in `retrieve` tool to search a Bedrock Knowledge Base
and inject relevant documents into the agent's context on demand.

The agent decides WHEN to search and WHAT to search for based on
the user's question — no pre-loading of documents into the prompt.

Prerequisites:
    - A Bedrock Knowledge Base with documents indexed
    - AWS credentials with bedrock:Retrieve permission

Install:
    pip install strands-agents strands-agents-tools
"""

import os
from strands import Agent
from strands_tools import retrieve

# The retrieve tool uses KNOWLEDGE_BASE_ID from the environment
# to know which knowledge base to search
os.environ["KNOWLEDGE_BASE_ID"] = "YOUR_KB_ID_HERE"

agent = Agent(
    system_prompt="""You are a technical support agent for Acme Cloud Platform.

When users ask questions:
1. Use the retrieve tool to search the knowledge base for relevant documentation
2. Answer based on what you find — cite the source documents
3. If the knowledge base doesn't have the answer, say so clearly

Never guess at technical details. Always retrieve first.
""",
    tools=[retrieve],
)

if __name__ == "__main__":
    # The agent searches the KB on demand — only relevant chunks
    # enter the context window, not the entire document corpus
    response = agent("How do I configure VPC peering between two accounts?")
    print(response)

    # Follow-up uses conversation history + new retrieval if needed
    response = agent("What about the security group rules for that?")
    print(response)

    # The key insight:
    # - Without RAG: you'd stuff docs into the system prompt (context stuffing anti-pattern)
    # - With RAG: the agent pulls only the relevant chunks when needed
    # - Token budget stays lean, answers stay grounded in real docs
