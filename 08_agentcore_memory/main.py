"""AgentCore long-term memory through the Python MemoryStore integration.

Requires an EXISTING memory resource and a semantic strategy whose namespace
matches AGENTCORE_MEMORY_NAMESPACE (default /facts/{actorId}/). This example
writes conversation events and enables server-side extraction; it provisions
nothing. Extraction is asynchronous and a new fact may not be searchable yet.
"""

import argparse
import os
from uuid import uuid4

from bedrock_agentcore.memory.integrations.strands.memorystore import AgentCoreMemoryStore
from strands import Agent
from strands.memory import MemoryManager

from sample_support import make_model, run_turns


def create_agent(model=None, *, client=None, memory_id=None, session_id=None, writable=True):
    memory_id = memory_id or os.getenv("AGENTCORE_MEMORY_ID")
    if not memory_id:
        raise ValueError("Set AGENTCORE_MEMORY_ID to an existing AgentCore Memory resource ID.")
    store = AgentCoreMemoryStore(
        memory_id=memory_id,
        actor_id=os.getenv("AGENTCORE_ACTOR_ID", "demo-user"),
        session_id=session_id or os.getenv("AGENTCORE_SESSION_ID") or str(uuid4()),
        namespace=os.getenv("AGENTCORE_MEMORY_NAMESPACE", "/facts/{actorId}/"),
        writable=writable,
        extraction=writable,
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        client=client,
    )
    return Agent(
        model=model if model is not None else make_model(),
        memory_manager=MemoryManager(stores=[store]),
        system_prompt=(
            "Use memory to recall established service facts. If a fact is unavailable, say so. "
            "Only claim what the recalled evidence supports."
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["remember", "recall"])
    args = parser.parse_args()
    prompt = (
        "Remember this synthetic service fact: checkout's normal payment timeout is 2000 ms."
        if args.mode == "remember"
        else "What is checkout's normal payment timeout? Look it up in memory."
    )
    run_turns(create_agent(writable=args.mode == "remember"), [prompt])
    if args.mode == "remember":
        print(
            "Extraction is eventually consistent. Run recall separately after extraction completes."
        )
