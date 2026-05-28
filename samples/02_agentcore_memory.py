"""
Context Engineering Strategy: Externalize + Select

Tiered memory with Amazon Bedrock AgentCore Memory.
Short-term (conversation persistence) and long-term (fact/preference extraction)
handled by a single managed service.

Install:
    pip install bedrock-agentcore strands-agents
"""

from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")
memory = client.create_memory_and_wait(
    name="SupportAgentMemory",
    description="Memory for a customer support agent",
    strategies=[
        # Extracts user preferences automatically
        {"userPreferenceMemoryStrategy": {
            "name": "PreferenceLearner",
            "namespaceTemplates": ["/preferences/{actorId}/"],
        }},
        # Extracts factual information (account IDs, names, etc.)
        {"semanticMemoryStrategy": {
            "name": "FactExtractor",
            "namespaceTemplates": ["/facts/{actorId}/"],
        }},
        # Summarizes sessions for future context
        {"summaryMemoryStrategy": {
            "name": "SessionSummarizer",
            "namespaceTemplates": ["/summaries/{actorId}/{sessionId}/"],
        }},
    ],
)

# --- Wire it into a Strands agent with conversation management ---

from strands import Agent
from strands.agent.conversation_manager import SummarizingConversationManager
from bedrock_agentcore.memory.integrations.strands import (
    AgentCoreMemoryConfig, AgentCoreMemorySessionManager, RetrievalConfig,
)

MEMORY_ID = memory["id"]

# Configure memory with long-term retrieval namespaces
# This tells AgentCore Memory WHICH extracted facts/preferences
# to retrieve and inject into context on each turn
agentcore_memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id="session_123",
    actor_id="user_456",
    retrieval_config={
        "/preferences/{actorId}/": RetrievalConfig(),
        "/facts/{actorId}/": RetrievalConfig(),
    },
)

agent = Agent(
    system_prompt="You are a helpful support agent.",
    conversation_manager=SummarizingConversationManager(
        preserve_recent_messages=10,
        summarization_system_prompt="Preserve preferences, decisions, and facts.",
    ),
    session_manager=AgentCoreMemorySessionManager(
        agentcore_memory_config=agentcore_memory_config,
        region_name="us-east-1",
    ),
)

agent("I prefer email over phone.")  # → stored as preference
agent("My account ID is 7891011.")   # → stored as fact
