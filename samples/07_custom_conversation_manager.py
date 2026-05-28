"""
Building a Custom Conversation Manager

When the built-in sliding window and summarization aren't enough,
you can build your own eviction logic. This example shows a
priority-based manager that keeps messages tagged as important.

Install:
    pip install strands-agents
"""

from typing import Any
from strands import Agent
from strands.agent.conversation_manager import ConversationManager
from strands.types.content import Message


class PriorityConversationManager(ConversationManager):
    """Keep important messages regardless of age, evict the rest by recency.

    Messages containing tool results, decisions, or user-flagged info
    are marked as high-priority and never evicted. Everything else
    follows a sliding window.
    """

    def __init__(self, window_size: int = 20, priority_keywords: list[str] | None = None):
        self.window_size = window_size
        self.priority_keywords = priority_keywords or [
            "decision:", "important:", "remember:", "confirmed:",
        ]

    def is_priority(self, message: Message) -> bool:
        """Check if a message should be preserved regardless of age."""
        for content_block in message.get("content", []):
            if "text" in content_block:
                text = content_block["text"].lower()
                if any(kw in text for kw in self.priority_keywords):
                    return True
            # Always keep tool results (they contain retrieved data)
            if "toolResult" in content_block:
                return True
        return False

    def apply_management(self, agent: "Agent", **kwargs: Any) -> None:
        """Apply priority-aware eviction after each turn."""
        messages = agent.messages

        if len(messages) <= self.window_size:
            return

        # Split into priority and normal messages
        priority_messages = []
        normal_messages = []

        for msg in messages:
            if self.is_priority(msg):
                priority_messages.append(msg)
            else:
                normal_messages.append(msg)

        # Keep all priority messages + most recent normal messages
        remaining_slots = self.window_size - len(priority_messages)
        if remaining_slots > 0:
            kept_normal = normal_messages[-remaining_slots:]
        else:
            kept_normal = []

        # Rebuild message list preserving original order
        kept_set = set(id(m) for m in priority_messages + kept_normal)
        agent.messages[:] = [m for m in messages if id(m) in kept_set]

    def reduce_context(self, agent: "Agent", e: Exception | None = None, **kwargs: Any) -> None:
        """Emergency reduction — drop non-priority messages aggressively."""
        messages = agent.messages
        # Keep only priority messages + last 5 normal messages
        priority = [m for m in messages if self.is_priority(m)]
        normal = [m for m in messages if not self.is_priority(m)]
        agent.messages[:] = priority + normal[-5:]


# --- Usage ---
agent = Agent(
    system_prompt="You are a project manager assistant.",
    conversation_manager=PriorityConversationManager(
        window_size=30,
        priority_keywords=["decision:", "blocker:", "deadline:", "approved:"],
    ),
)

if __name__ == "__main__":
    # Normal messages get evicted after window fills up
    agent("Let's discuss the project timeline.")
    agent("How's the weather today?")

    # Priority messages survive eviction
    agent("Decision: we're going with microservices architecture.")
    agent("Deadline: MVP must ship by March 15.")
    agent("Blocker: waiting on security review from the platform team.")

    # Many turns later... the decisions and blockers are still in context
    # even though casual messages have been evicted
    response = agent("What are our current blockers and deadlines?")
    print(response)
