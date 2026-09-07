import os

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import StructuredTool

COLLECTION_NAME = "code_chunks"


def search_code(query: str, top_k: int = 3):
    """Search for relevant code and collect related chunks."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=".chroma",
    )

    # First: semantic search
    results = vectorstore.similarity_search(
        query,
        k=top_k,
    )

    if not results:
        return []

    # Use the strongest result to identify the code entity.
    primary = results[0]

    file_path = primary.metadata["file_path"]
    function_name = primary.metadata["name"]
    class_name = primary.metadata["class_name"]

    # Retrieve all chunks belonging to the same function/class.
    filters = {
    "$and": [
        {"file_path": file_path},
        {"name": function_name},
    ]
              }

    related = vectorstore.get(
        where=filters,
        include=["documents", "metadatas"],
    )

    documents = []

    for document, metadata in zip(
        related["documents"],
        related["metadatas"],
    ):
        documents.append({
            "code": document,
            "metadata": metadata,
        })

    # Sort chunks by source-code order.
    documents.sort(
        key=lambda item: (
            item["metadata"]["start_line"]
        )
    )

    return documents

search_code_tool = StructuredTool.from_function(
    func=search_code,
    name="search_code",
    description=(
        "Search the LangGraph source code for relevant functions, "
        "classes, and implementation details. Use this when the user "
        "asks for actual code or asks where a feature is implemented."
    ),
)


if __name__ == "__main__":
    results = search_code(
        "create_react_agent function"
    )

    print(f"Total related chunks: {len(results)}")

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print("=" * 60)
        print(f"CHUNK {i}")
        print(f"File: {metadata['file_path']}")
        print(f"Function: {metadata['name']}")
        print(f"Class: {metadata['class_name']}")
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
        print(result["code"][:500])
        print()