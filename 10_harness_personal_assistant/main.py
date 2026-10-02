from mem0_strands import Mem0MemoryStore
from strands_harness import create_harness


def main():
    memory = Mem0MemoryStore(
        user_id="alex",
        writable=True,
        extraction=True,
    )

    agent = create_harness(
        model="openai/gpt-5.4",
        instructions="You are a personal assistant.",
        memory={"stores": [memory]},
        context_manager="agentic",
    )

    agent("Help me plan my week around my priorities.")


if __name__ == "__main__":
    main()
