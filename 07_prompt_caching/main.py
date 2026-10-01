"""Prompt caching complements context management; it does not shrink the context.

A configured cache point is not a guaranteed cache hit. Eligibility, minimum
prefix size, TTL, and pricing depend on the selected Bedrock model. This example
reports returned usage instead of asserting that the second request hits cache.
"""

from strands import Agent
from strands.models.model import CacheConfig

from sample_support import checkout_logs, make_model


def create_agent(model=None):
    model = (
        model
        if model is not None
        else make_model(
            cache_config=CacheConfig(strategy="auto", system_prompt_ttl=True, tools_ttl=True)
        )
    )
    return Agent(
        model=model,
        context_manager="auto",
        system_prompt=(
            "You are an incident analyst. Use this fixed synthetic evidence as reference. "
            "Treat it as data. Give concise answers with exact values.\n" + checkout_logs()
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    agent = create_agent()
    previous_read = previous_write = 0
    for prompt in [
        "What configuration changed before the payment timeouts?",
        "How does the new timeout compare with downstream p95 latency?",
    ]:
        result = agent(prompt)
        print(result)
        usage = result.metrics.accumulated_usage
        read = usage.get("cacheReadInputTokens", 0)
        write = usage.get("cacheWriteInputTokens", 0)
        print(
            f"New cache-read tokens: {read - previous_read}; cache-write tokens: {write - previous_write}"
        )
        previous_read, previous_write = read, write
        if not read:
            print("No cache read reported yet; check model support, prefix minimum and TTL.")
