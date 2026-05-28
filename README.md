# The Infinite Context Window Is a Myth

**Context Engineering for AI Agents** — companion code samples for the talk by Morgan Willis (AWS).

## What is Context Engineering?

Giving the model the information it needs when it needs it. Curating the context window for optimal outcomes and token consumption.

## Samples

| # | File | Strategy | Description |
|---|------|----------|-------------|
| 01 | [Summarization](samples/01_summarization.py) | Compress | Custom summarization with control over what gets preserved |
| 02 | [AgentCore Memory](samples/02_agentcore_memory.py) | Externalize + Select | Tiered memory with short-term and long-term persistence |
| 03 | [Tool-Driven Context](samples/03_tool_driven_context.py) | Select | RAG, APIs, and database queries pulled on demand |
| 04 | [Skills](samples/04_skills.py) | Select | Progressive disclosure — instructions loaded on demand |
| 05 | [Isolated Subagents](samples/05_isolated_subagents.py) | Isolate | Scoped context per agent, conclusions only passed back |
| 06 | [RAG Knowledge Base](samples/06_rag_knowledge_base.py) | Select | Bedrock Knowledge Bases with the retrieve tool |
| 07 | [Custom Conversation Manager](samples/07_custom_conversation_manager.py) | Compress | Priority-based eviction — keep important messages forever |
| 08 | [Recitation Pattern](samples/08_recitation_pattern.py) | Attention | Exploit the U-curve by restating plans in recent context |

## Context Engineering Strategies

| Strategy | What it does | Implementation |
|----------|-------------|----------------|
| **Compress** | Reduce tokens, summarize, compact | Conversation managers |
| **Externalize** | Persist to storage outside the context window | AgentCore Memory, Mem0 |
| **Select** | Retrieve only what is relevant | Tools, RAG, Skills |
| **Isolate** | Separate context across agents | Multi-agent patterns |

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install strands-agents strands-agents-tools
```

For AgentCore Memory samples:
```bash
pip install bedrock-agentcore
```

## Built With

- [Strands Agents SDK](https://strandsagents.com)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/)
