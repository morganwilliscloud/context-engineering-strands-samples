"""Retrieve synthetic order data on demand. No database or external API is contacted."""

from strands import Agent, tool
from strands.vended_tools import web_fetch

from sample_support import make_model, run_turns


@tool
def lookup_order(order_id: str) -> str:
    """Look up an order in a synthetic fixture.

    Args:
        order_id: The fixture supports order 12345.
    """
    if order_id != "12345":
        return "Order not found in the demo fixture."
    return "SYNTHETIC ORDER 12345: shipped, estimated arrival 2026-10-03, carrier Example Delivery."


def create_agent(model=None):
    return Agent(
        model=model if model is not None else make_model(),
        context_manager="auto",
        tools=[lookup_order, web_fetch],
        system_prompt="Use tools to retrieve the requested information. Do not invent order details.",
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(create_agent(), ["Where is order 12345?"])
