from strands.experimental.context_manager import Offload
from strands.models.openai import OpenAIModel
from strands_harness import create_harness


def main():
    summary = Offload.summarize("*", {
        "model": OpenAIModel(model_id="gpt-5-mini"),
        "system_prompt": (
            "Preserve preferences, commitments, dates, "
            "and open tasks. Remove repeated discussion."
        ),
    }).when(utilization=0.80, preserve_recent=6)

    agent = create_harness(
        model="openai/gpt-5.4",
        instructions="You are a personal assistant.",
        context_manager={"strategies": [
            Offload.truncate("tool_results").when(threshold=2000),
            summary,
        ]},
    )

    agent("Help me plan my week around my priorities.")


if __name__ == "__main__":
    main()
