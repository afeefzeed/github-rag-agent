import os
from collections import defaultdict

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import StructuredTool


COLLECTION_NAME = "code_chunks"

RETRIEVAL_K = 15
FINAL_ENTITIES = 2


def structural_multiplier(metadata: dict) -> float:
    """Return a moderate structural relevance multiplier."""

    file_path = metadata.get("file_path", "").lower()
    function_name = metadata.get("name", "").lower()
    class_name = metadata.get("class_name", "").lower()
    chunk_type = metadata.get("chunk_type", "").lower()

    combined_text = (
        f"{file_path} {function_name} {class_name}"
    )

    multiplier = 1.0

    # Penalize obvious test/mock/fake implementations.
    if any(
        term in combined_text
        for term in [
            "test",
            "tests",
            "mock",
            "fake",
            "dummy",
        ]
    ):
        multiplier *= 0.75

    # Small bonus for important production areas.
    if any(
        term in file_path
        for term in [
            "langgraph/prebuilt",
            "langgraph/graph",
            "langgraph/pregel",
        ]
    ):
        multiplier *= 1.15

    # Small bonus for top-level functions/classes.
    if chunk_type in {
        "class",
        "function",
        "async_function",
    }:
        multiplier *= 1.10

    return multiplier


def search_code(
    query: str,
    top_k: int = RETRIEVAL_K,
):
    """Search the LangGraph source code using semantic retrieval and structural reranking."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set."
        )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=".chroma",
    )

    # Retrieve a larger candidate pool together with
    # Chroma similarity distances.
    results = vectorstore.similarity_search_with_score(
        query,
        k=top_k,
    )

    if not results:
        return []

    # Group retrieved chunks into logical entities.
    entities = defaultdict(list)

    for rank, (document, distance) in enumerate(results):
        metadata = document.metadata

        file_path = metadata.get(
            "file_path",
            "",
        )

        class_name = metadata.get(
            "class_name",
            "",
        )

        function_name = metadata.get(
            "name",
            "",
        )

        entity_key = (
            file_path,
            class_name,
            function_name,
        )

        entities[entity_key].append(
            {
                "document": document,
                "distance": distance,
                "rank": rank,
                "metadata": metadata,
            }
        )

    ranked_entities = []

    for entity_key, chunks in entities.items():

        # The best semantic distance for this entity.
        best_chunk = min(
            chunks,
            key=lambda item: item["distance"],
        )

        distance = best_chunk["distance"]

        # Convert distance into a base relevance score.
        # Lower distance = higher relevance.
        base_score = 1.0 / (1.0 + distance)

        multiplier = structural_multiplier(
            best_chunk["metadata"]
        )

        final_score = (
            base_score * multiplier
        )

        ranked_entities.append(
            {
                "entity_key": entity_key,
                "score": final_score,
                "best_distance": distance,
                "chunks": chunks,
            }
        )

    # Rank logical entities.
    ranked_entities.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # Select the best distinct entities.
    selected_entities = ranked_entities[
        :FINAL_ENTITIES
    ]

    final_documents = []

    for entity in selected_entities:

        file_path, class_name, function_name = (
            entity["entity_key"]
        )

        filters = {
            "$and": [
                {
                    "file_path": file_path
                },
                {
                    "name": function_name
                },
            ]
        }

        related = vectorstore.get(
            where=filters,
            include=[
                "documents",
                "metadatas",
            ],
        )

        related_documents = []

        for document, metadata in zip(
            related["documents"],
            related["metadatas"],
        ):
            related_documents.append(
                {
                    "code": document,
                    "metadata": metadata,
                }
            )

        # Restore original source-code order.
        related_documents.sort(
            key=lambda item: item[
                "metadata"
            ].get(
                "start_line",
                0,
            )
        )

        final_documents.extend(
            related_documents
        )

    return final_documents


search_code_tool = StructuredTool.from_function(
    func=search_code,
    name="search_code",
    description=(
        "Search the LangGraph source code for relevant "
        "functions, classes, and implementation details. "
        "Use this when the user asks for actual code or "
        "asks where a feature is implemented."
    ),
)


if __name__ == "__main__":

    results = search_code(
        "How does LangGraph connect an AI agent to tools?"
    )

    print(
        f"Total returned chunks: "
        f"{len(results)}"
    )

    for i, result in enumerate(
        results,
        start=1,
    ):
        metadata = result["metadata"]

        print("=" * 60)
        print(f"CHUNK {i}")
        print(
            f"File: "
            f"{metadata['file_path']}"
        )
        print(
            f"Function: "
            f"{metadata['name']}"
        )
        print(
            f"Class: "
            f"{metadata['class_name']}"
        )
        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )
        print(
            f"Part: "
            f"{metadata['part']}/"
            f"{metadata['total_parts']}"
        )
        print()
        print(
            result["code"][:500]
        )
        print()