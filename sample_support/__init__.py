"""Shared, synthetic evidence for the talk. No production services are contacted."""

import os
from pathlib import Path

from strands import tool
from strands.models import BedrockModel

ROOT = Path(__file__).resolve().parents[1]


def make_model(**options):
    """Use the same Bedrock model across examples; optionally set BEDROCK_MODEL_ID."""
    if model_id := os.getenv("BEDROCK_MODEL_ID"):
        options["model_id"] = model_id
    if region := os.getenv("AWS_REGION"):
        options["region_name"] = region
    return BedrockModel(**options)


def checkout_logs() -> str:
    """A fixed large result, with the diagnostic evidence beyond a short preview."""
    lines = ["SYNTHETIC DEMO DATA: checkout service, 2026-09-30, timestamps UTC."]
    for i in range(360):
        timestamp = f"2026-09-30T12:{i // 60:02d}:{i % 60:02d}Z"
        if i == 180:
            message = "WARN config_changed payment_timeout_ms=2000 -> 200 revision=demo-42"
        elif i > 180 and i % 4 == 0:
            message = (
                "ERROR payment-api timeout elapsed_ms=201 configured_timeout_ms=200 "
                "payment-api_p95_ms=620 result=checkout_504 revision=demo-42"
            )
        else:
            message = (
                "INFO request_completed status=200 latency_ms=85 db_pool=12/50 "
                "queue_depth=0 memory_percent=42 cpu_percent=18 route=/checkout"
            )
        lines.append(f"{timestamp} request_id=synthetic-{i:04d} {message}")
    return "\n".join(lines)


@tool
def get_service_logs(service_name: str = "checkout") -> str:
    """Read the fixed synthetic checkout service logs.

    Args:
        service_name: The demo supports only checkout.
    """
    if service_name != "checkout":
        return "No fixture for this service. Available service: checkout."
    return checkout_logs()


@tool
def get_service_config(service_name: str = "checkout") -> str:
    """Read the synthetic current and previous configuration.

    Args:
        service_name: The demo supports only checkout.
    """
    if service_name != "checkout":
        return "No fixture for this service. Available service: checkout."
    return (
        "SYNTHETIC CONFIG: revision demo-42 changed payment_timeout_ms from 2000 to 200. "
        "Payment API p95 latency is 620 ms. Database pool and CPU are normal. "
        "A rollback requires operator approval; this demo has no deployment tool."
    )


def run_turns(agent, prompts):
    for number, prompt in enumerate(prompts, 1):
        print(f"\nTurn {number}: {prompt}\n")
        result = agent(prompt)
        print(result)
        print(f"\nMessages currently retained: {len(agent.messages)}")
