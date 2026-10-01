"""Exercise the real SDK with scripted model output and no external services."""

import asyncio
import copy
import importlib.util
import json
import re
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from strands.models import Model

from sample_support import ROOT, checkout_logs


class ScriptedModel(Model):
    def __init__(self, responses=(), **config):
        self.responses = list(responses)
        self.config = {"context_window_limit": 200000, **config}
        self.calls = []

    def update_config(self, **config):
        self.config.update(config)

    def get_config(self):
        return self.config

    async def structured_output(self, *args, **kwargs):
        raise NotImplementedError
        yield  # pragma: no cover

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls.append(copy.deepcopy(messages))
        response = self.responses.pop(0) if self.responses else "Scripted answer."
        yield {"messageStart": {"role": "assistant"}}
        if isinstance(response, tuple):
            name, arguments = response
            yield {
                "contentBlockStart": {
                    "contentBlockIndex": 0,
                    "start": {"toolUse": {"toolUseId": f"call-{len(self.calls)}", "name": name}},
                }
            }
            yield {
                "contentBlockDelta": {
                    "contentBlockIndex": 0,
                    "delta": {"toolUse": {"input": json.dumps(arguments)}},
                }
            }
            reason = "tool_use"
        else:
            yield {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": response}}}
            reason = "end_turn"
        yield {"contentBlockStop": {"contentBlockIndex": 0}}
        yield {"messageStop": {"stopReason": reason}}
        yield {
            "metadata": {
                "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
                "metrics": {"latencyMs": 1},
            }
        }


def load(prefix):
    path = next(ROOT.glob(f"{prefix}_*/main.py"))
    spec = importlib.util.spec_from_file_location(f"sample_{prefix}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "offline-test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "offline-test")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    monkeypatch.delenv("AGENTCORE_MEMORY_ID", raising=False)


@pytest.mark.parametrize("prefix", ["00", "01", "02", "03", "04", "05", "06", "07", "09"])
def test_builds_with_released_sdk(prefix, tmp_path):
    module = load(prefix)
    options = {}
    if prefix == "04":
        options["stash_dir"] = tmp_path / "stash"
    if prefix == "09":
        options["state_dir"] = tmp_path / "harness"
    agent = module.create_agent(model=ScriptedModel(), **options)
    assert agent is not None


def test_auto_and_custom_offload_real_tool_result(tmp_path):
    for prefix in ("01", "04"):
        model = ScriptedModel([("get_service_logs", {"service_name": "checkout"}), "Diagnosis."])
        options = {"stash_dir": tmp_path / "stash"} if prefix == "04" else {}
        agent = load(prefix).create_agent(model=model, **options)
        agent("Investigate checkout.")
        assert "retrieve_context" in agent.tool_names
        assert len(json.dumps(model.calls[-1])) < len(checkout_logs()) / 2
        assert "payment_timeout_ms=2000 -> 200" not in json.dumps(model.calls[-1])
        reference = re.search(r"\[ref: ([^\]]+)\]", json.dumps(model.calls[-1])).group(1)
        retrieved = agent.tool.retrieve_context(reference=reference, pattern="config_changed")
        assert "payment_timeout_ms=2000 -> 200" in json.dumps(retrieved)
        if prefix == "04":
            files = [p for p in (tmp_path / "stash").rglob("*") if p.is_file()]
            assert files
            assert any("payment_timeout_ms=2000 -> 200" in p.read_text() for p in files)


def test_sliding_window_drops_older_turns():
    agent = load("02").create_agent(model=ScriptedModel())
    for i in range(9):
        agent(f"Update {i}")
    history = json.dumps(agent.messages)
    assert "Update 0" not in history
    assert "Update 8" in history
    assert len(agent.messages) <= 8  # Reduction occurs before the new assistant response.


def test_summarization_under_pressure():
    model = ScriptedModel(
        ["Summary: timeout changed from 2000 to 200 ms.", "Handoff."], context_window_limit=12000
    )
    agent = load("03").create_agent(model=model)
    agent.messages.extend(
        [
            {"role": "user", "content": [{"text": "Investigate the archived checkout incident."}]},
            {"role": "assistant", "content": [{"text": "Please provide the logs."}]},
            {"role": "user", "content": [{"text": checkout_logs()}]},
            {"role": "assistant", "content": [{"text": "Old diagnosis."}]},
            {"role": "user", "content": [{"text": "Recent question 1"}]},
            {"role": "assistant", "content": [{"text": "Recent answer 1"}]},
            {"role": "user", "content": [{"text": "Recent question 2"}]},
            {"role": "assistant", "content": [{"text": "Recent answer 2"}]},
        ]
    )
    agent("Give a handoff.")
    assert len(model.calls) >= 2
    history = json.dumps(agent.messages)
    assert "Summary: timeout" in history
    assert "Recent answer 2" in history
    assert "synthetic-0359" not in history


def test_subagent_returns_summary_without_bulk_logs():
    model = ScriptedModel(
        [
            ("analyze_logs", {"input": "Investigate checkout."}),
            ("get_service_logs", {"service_name": "checkout"}),
            "Child diagnosis: payment timeout too low.",
            "Parent handoff.",
        ]
    )
    agent = load("06").create_agent(model=model)
    agent("Investigate checkout.")
    history = json.dumps(agent.messages)
    assert "Child diagnosis" in history
    assert "synthetic-0359" not in history
    assert "SYNTHETIC DEMO DATA" not in history


def test_skill_discovery_and_activation():
    model = ScriptedModel([("skills", {"skill_name": "code-review"}), "Review complete."])
    agent = load("05").create_agent(model=model)
    agent("Review the supplied code using the code-review skill.")
    assert "skills" in agent.tool_names
    assert "placeholder" in json.dumps(model.calls[-1])
    assert "parameter" in json.dumps(model.calls[-1])


def test_agentcore_requires_existing_resource():
    with pytest.raises(ValueError, match="AGENTCORE_MEMORY_ID"):
        load("08").create_agent(model=ScriptedModel())


def test_agentcore_builds_without_provisioning():
    client = SimpleNamespace(gmdp_client=Mock())
    agent = load("08").create_agent(
        model=ScriptedModel(), client=client, memory_id="demo-memory", session_id="demo-session"
    )
    assert agent.memory_manager is not None
    assert client.gmdp_client.mock_calls == []


def test_agentcore_recall_and_event_write():
    from bedrock_agentcore.memory.integrations.strands.memorystore import AgentCoreMemoryStore

    transport = Mock()
    transport.retrieve_memory_records.return_value = {
        "memoryRecordSummaries": [
            {
                "memoryRecordId": "fact-1",
                "content": {"text": "Normal timeout is 2000 ms."},
                "score": 0.9,
            }
        ]
    }
    transport.create_event.return_value = {"event": {"eventId": "demo-event"}}
    store = AgentCoreMemoryStore(
        memory_id="demo-memory",
        actor_id="demo-user",
        session_id="demo-session",
        namespace="/facts/{actorId}/",
        writable=True,
        extraction=True,
        client=SimpleNamespace(gmdp_client=transport),
    )
    entries = asyncio.run(store.search("payment timeout"))
    assert entries
    assert transport.retrieve_memory_records.call_args.kwargs["namespace"] == "/facts/demo-user/"
    asyncio.run(
        store.add_messages(
            [
                {"role": "user", "content": [{"text": "Normal timeout is 2000 ms."}]},
                {"role": "assistant", "content": [{"text": "Understood."}]},
            ]
        )
    )
    transport.create_event.assert_called_once()
    assert transport.create_event.call_args.kwargs["memoryId"] == "demo-memory"


def load_legacy(filename):
    path = ROOT / "samples" / filename
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_order_lookup_returns_fixture_evidence():
    model = ScriptedModel([("lookup_order", {"order_id": "12345"}), "Order is shipped."])
    agent = load_legacy("03_tool_driven_context.py").create_agent(model=model)
    agent("Where is order 12345?")
    assert "SYNTHETIC ORDER 12345" in json.dumps(model.calls[-1])


def test_knowledge_base_retrieval_keeps_sources():
    client = Mock()
    client.retrieve.return_value = {
        "retrievalResults": [
            {
                "content": {"text": "Use a 2000 ms timeout."},
                "location": {"type": "S3", "s3Location": {"uri": "s3://demo/runbook.md"}},
                "score": 0.9,
            }
        ]
    }
    model = ScriptedModel([("retrieve_documents", {"query": "checkout timeout"}), "Answer."])
    agent = load_legacy("06_rag_knowledge_base.py").create_agent(
        model=model, client=client, knowledge_base_id="DEMO123456"
    )
    agent("What timeout should checkout use?")
    assert client.retrieve.call_args.kwargs["knowledgeBaseId"] == "DEMO123456"
    assert "s3://demo/runbook.md" in json.dumps(model.calls[-1])
    assert "2000 ms" in json.dumps(model.calls[-1])


def test_recitation_example_runs_without_import_side_effects():
    model = ScriptedModel(["Plan: check configuration."])
    agent = load_legacy("08_recitation_pattern.py").create_agent(model=model)
    assert not model.calls
    assert "Plan:" in str(agent("Begin the investigation."))
