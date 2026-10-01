"""Search an existing Bedrock Knowledge Base with a small custom tool.

Set KNOWLEDGE_BASE_ID and AWS_REGION. Requires bedrock:Retrieve permission.
The agent receives matching chunks and their source locations on demand.
"""

import json
import os

import boto3
from strands import Agent, tool

from sample_support import make_model, run_turns


def create_agent(model=None, *, client=None, knowledge_base_id=None):
    knowledge_base_id = knowledge_base_id or os.getenv("KNOWLEDGE_BASE_ID")
    if not knowledge_base_id:
        raise ValueError("Set KNOWLEDGE_BASE_ID to an existing indexed Bedrock Knowledge Base.")
    client = (
        client
        if client is not None
        else boto3.client("bedrock-agent-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    )

    @tool
    def retrieve_documents(query: str) -> str:
        """Retrieve relevant chunks and source locations from the configured knowledge base.

        Args:
            query: The question or topic to search for.
        """
        response = client.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
        )
        return json.dumps(
            [
                {
                    "content": result.get("content", {}),
                    "source": result.get("location", {}),
                    "score": result.get("score"),
                }
                for result in response.get("retrievalResults", [])
            ]
        )

    return Agent(
        model=model if model is not None else make_model(),
        context_manager="auto",
        tools=[retrieve_documents],
        system_prompt=(
            "Retrieve relevant documentation before answering. Cite returned sources. "
            "If the retrieved material does not answer the question, say so."
        ),
        callback_handler=None,
    )


if __name__ == "__main__":
    run_turns(create_agent(), ["What guidance does the knowledge base have for service timeouts?"])
