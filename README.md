# Context Engineering with Strands

Companion examples for **Quit Tokenmaxxing** and the context engineering talk.
The examples build individual techniques with `Agent`, then finish with
`create_harness`. The checkout incident is synthetic and identical across demos.

## Talk slides

- [PowerPoint deck](presentation/context-engineering-talk.pptx)
- [PDF slides](presentation/context-engineering-talk.pdf)

The PowerPoint includes speaker notes and hidden backup slides. The PDF is a
slide-only export of the visible presentation.

## Setup

Python 3.10+ and AWS credentials with Bedrock model access are required for live runs.
Install from this directory into a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Use an existing AWS profile, such as one authenticated through AWS IAM Identity Center.
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
# Optional: choose a Bedrock model ID or inference profile available in your account.
export BEDROCK_MODEL_ID=your-model-or-inference-profile-id
```

Omit `BEDROCK_MODEL_ID` to use the SDK's default Bedrock model. The scripts share
this model configuration so the final Harness demo uses the same model as the
individual examples. Live invocations incur provider charges. The optional Exa
mode also sends search queries to Exa's hosted MCP service.

Dependencies are pinned to the releases used for local validation:
`strands-agents[web-fetch]` 1.57.2, `strands-harness` 0.1.2, and `bedrock-agentcore`
1.24.0. SDK tools come from `strands.vended_tools`.

## Examples and talk order

Existing directory numbers are preserved. For the talk, use this order:
**00 → 02 → 03 → 08 → 05 → 04 → 01 → 06 → 09**.
Prompt caching (07) is an optional extra.

| Directory | Technique | What to look for |
|---|---|---|
| [00_coding_agent](00_coding_agent/main.py) | Starting Agent | Vended `file_editor`, `shell`, `web_fetch`; optional Exa MCP search |
| [02_sliding_window](02_sliding_window/main.py) | Compress | Old messages leave a small conversation window |
| [03_summarizing](03_summarizing/main.py) | Compress | `Offload.summarize("*")` at 85% utilization, preserving four recent messages |
| [08_agentcore_memory](08_agentcore_memory/main.py) | Externalize + select | Long-term knowledge through `AgentCoreMemoryStore` + `MemoryManager` |
| [05_skills_progressive_disclosure](05_skills_progressive_disclosure/main.py) | Select | `AgentSkills` discovers a real `SKILL.md` and loads instructions on demand |
| [04_context_offloading](04_context_offloading/main.py) | Externalize + select | Custom `Offload.truncate` + summarization pipeline with a local stash |
| [01_auto_context_manager](01_auto_context_manager/main.py) | Compress + externalize + select | Wrap the context pipeline into `context_manager="auto"` |
| [06_subagents](06_subagents/main.py) | Isolate | A named Agent passed directly as a tool, with its own context |
| [09_strands_harness](09_strands_harness/main.py) | Assembled agent | `create_harness`, built-in tools, sessions, local memory and delegation |
| [07_prompt_caching](07_prompt_caching/main.py) | Cost optimization | Configure `CacheConfig` and report actual cache usage |

```bash
python 00_coding_agent/main.py
python 00_coding_agent/main.py --exa
python 02_sliding_window/main.py
python 03_summarizing/main.py --demo-pressure
python 04_context_offloading/main.py
python 01_auto_context_manager/main.py
python 05_skills_progressive_disclosure/main.py
python 06_subagents/main.py
python 07_prompt_caching/main.py
```

The starting and skills agents expose file and shell tools. The supplied demo
prompts ask for inspection only. Run them in the intended demo workspace.

## Existing sample links

The original `samples/` paths remain available. Summarization, AgentCore memory,
skills, subagents, and custom context management now forward to the updated
examples above. The old custom eviction algorithm is replaced by the SDK's
strategy pipeline to preserve valid tool-call/result structure.

Additional examples remain under `samples/`:

- [Tool-driven context](samples/03_tool_driven_context.py): a runnable synthetic order lookup.
- [Knowledge Base retrieval](samples/06_rag_knowledge_base.py): set `KNOWLEDGE_BASE_ID` for an existing indexed Bedrock Knowledge Base.
- [Recitation](samples/08_recitation_pattern.py): an optional prompt technique, without guarantees about attention or accuracy.

## What auto does

```python
from strands import Agent

agent = Agent(context_manager="auto")
```

Auto truncates tool results above **1,500 tokens**, keeps a **750-token preview**,
and provides retrieval of the original content from a stash. At **85% context
utilization**, it summarizes older messages and preserves the **four most recent**.
Sample 04 deliberately uses custom **2,500/500** thresholds instead.

Auto does not add long-term memory, skills, or subagents. Those are separate
capabilities. The Context Manager strategy API remains experimental.

The large fixture encourages offloading, but a short conversation need not reach
the summarization threshold. Sample 03's `--demo-pressure` sets a smaller SDK
context budget and seeds older messages to exercise that path. It does not change
the provider's context capacity. Check the retained messages rather than assuming
compression occurred. Sliding-window eviction and summarization both lose detail;
a summary is not a lossless copy of the conversation.

## AgentCore long-term memory

Sample 08 uses the Python integration shipped in `bedrock-agentcore`. It requires
an **existing AgentCore Memory resource with a semantic extraction strategy**.
The strategy's namespace must match the store's configured namespace.

```bash
export AGENTCORE_MEMORY_ID=your-existing-memory-id
export AGENTCORE_ACTOR_ID=demo-user
export AGENTCORE_MEMORY_NAMESPACE='/facts/{actorId}/'
export AWS_REGION=us-east-1  # Must match the resource's region.

python 08_agentcore_memory/main.py remember
# After server-side extraction has completed:
python 08_agentcore_memory/main.py recall
```

`remember` sets both `writable=True` and `extraction=True`. It sends conversation
events for AgentCore's server-side long-term extraction. `recall` uses a read-only
store in a fresh session and searches the same actor's facts namespace. Keep the
actor consistent across these runs. The SDK fills `{actorId}` in the namespace.

Extraction is eventually consistent. An immediate recall can return no records;
it is not proof the write failed. The example does not create resources or
strategies, restore an earlier full conversation, or search other namespaces.
Preferences or summaries stored under another namespace need a corresponding
read store. AWS permissions for the write/read operations are required.

## Four-minute Harness demo

From the repository root:

```bash
cd 09_strands_harness
python main.py --session-id talk-demo
```

The first turn requests a delegated log investigation and checks configuration.
The second asks for the proposed corrective action. The supplied tools return a
fixed synthetic incident: revision `demo-42` reduced the payment timeout from
2,000 ms to 200 ms while downstream p95 latency was 620 ms. The evidence is beyond
the initial short log preview, giving the agent a reason to retrieve more context.

Watch for evidence retrieval and a concise parent diagnosis. Tool selection and
wording depend on the model; rehearse with your chosen model. The tools do not
operate a real service or deploy a rollback.

Harness enables its built-in capabilities through `create_harness`; domain tools
and instructions customize the investigation. Local sessions and memory are under
`09_strands_harness/.agent/`. Reusing `--session-id` resumes that conversation.
Omitting it starts a fresh conversation; local memory remains shared. Use a new
`--state-dir ./rehearsal-2` when you need a completely clean rehearsal. This final example
uses local Harness memory; sample 08 separately demonstrates AgentCore memory.

## Override Harness defaults: personal assistant

The closing slides show two separate configurations:

- [10_harness_personal_assistant](10_harness_personal_assistant/main.py): direct OpenAI model, Mem0 long-term memory, and `context_manager="agentic"`.
- [11_harness_custom_context](11_harness_custom_context/main.py): GPT-5.4 for the assistant, GPT-5 mini for summaries, a task-specific summary prompt, and explicit context thresholds.

```bash
pip install -e '.[personal]'
# Configure OPENAI_API_KEY and, for sample 10, MEM0_API_KEY in your environment.
python 10_harness_personal_assistant/main.py
python 11_harness_custom_context/main.py
```

These examples call OpenAI directly; they do not require Bedrock access. Sample 10
also sends conversation content to hosted Mem0 for extraction and uses `alex` as a
synthetic user ID. Use the appropriate user scope in an actual application.

Agentic mode supplies context usage information and the `summarize_context`,
`truncate_context`, and `pin_context` tools. The agent decides what to retain or
compress, with additional telemetry and tool-call overhead. Automatic truncation
and overflow summarization remain safety nets. The custom pipeline in sample 11
is an alternative to agentic mode: truncate tool results above 2,000 tokens, then
summarize at 80% utilization while retaining six recent messages. Mem0 is omitted
from that slide for clarity and can be supplied alongside a custom strategy.
The context-manager strategy API remains experimental.

The benchmark slide reports the published launch evaluation: 28% lower token cost
using the same Claude or GPT models across six benchmarks, with nearly equal
benchmark scores. Those results do not establish performance for these custom
configurations. Source: [Strands Harness launch evaluation](https://strandsagents.com/blog/introducing-strands-harness/).

Both configurations were constructed successfully with networking disabled and a
mock Mem0 client. No paid OpenAI or Mem0 calls were run.

## Validation

```bash
pytest -q
ruff check .
```

The tests use the installed SDK with scripted model responses and mocked AgentCore
transport. They exercise imports, agent construction, context reduction/retrieval,
subagent result separation, skill loading and memory integration without paid
model calls. They do not establish model answer quality, real AWS permissions,
AgentCore extraction completion, or live Exa availability. Cache hits are reported
from provider usage during sample 07; configuring caching alone does not prove a hit.

## Sources

- [Context engineering blog and code](https://builder.aws.com/content/3J36U47bvNh8qnt6KgNPUVP08q1/quit-tokenmaxxing-4-tips-for-context-engineering-with-code-samples)
- [Strands Harness blog](https://builder.aws.com/content/3JgWF0T6PorfoRq7EdgkwO3F96P/stop-starting-from-scratch-build-agents-with-strands-harness)
- [Built-in context modes](https://strandsagents.com/docs/user-guide/sdk/context-management/built-in-modes/)
- [Custom strategies](https://strandsagents.com/docs/user-guide/sdk/context-management/custom-strategies/)
- [Memory management](https://strandsagents.com/docs/user-guide/sdk/memory/managing-memory/)
- [AgentCore Python MemoryStore integration](https://github.com/aws/bedrock-agentcore-sdk-python/tree/main/src/bedrock_agentcore/memory/integrations/strands/memorystore)
- [Harness quickstart](https://strandsagents.com/docs/user-guide/harness/quickstart/)

## License

MIT
