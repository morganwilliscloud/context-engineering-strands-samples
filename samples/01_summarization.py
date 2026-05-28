"""
Context Engineering Strategy: Compress

Summarization with a custom prompt — you control what gets preserved
and what gets dropped. This is where the context engineering decision lives.

Install:
    pip install strands-agents
"""

from strands import Agent
from strands.agent.conversation_manager import SummarizingConversationManager

agent = Agent(
    conversation_manager=SummarizingConversationManager(
        summary_ratio=0.4,
        preserve_recent_messages=10,
        summarization_system_prompt="""
Summarize this conversation. Preserve:
- User preferences and constraints
- Decisions that were made
- Key facts (names, dates, numbers)

Drop:
- Greetings and filler
- Repeated explanations
- Abandoned ideas
""",
    ),
)
