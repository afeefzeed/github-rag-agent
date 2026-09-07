import json
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from chromadb import PersistentClient

DATASET_FILE = Path("data/langgraph_code_chunks.json")

COLLECTION_NAME = "code_chunks"

def code_index_exists() -> bool:
    """Check whether the Code RAG collection already exists."""

    from chromadb import PersistentClient

    client = PersistentClient(
        path=".chroma"
    )

    try:
        client.get_collection(
            name=COLLECTION_NAME
        )
        return True
    except Exception:
        return False

def build_code_index():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set."
        )

    with DATASET_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    print(f"Loaded {len(chunks)} code chunks.")

    documents = []

    for chunk in chunks:

        breadcrumb = (
            f"# Repository: {chunk['repository']}\n"
            f"# File: {chunk['file_path']}\n"
            f"# Class: {chunk['class_name']}\n"
            f"# Function: {chunk['name']}\n"
            f"# Type: {chunk['chunk_type']}\n"
        )

        if chunk.get("parent_function"):
            breadcrumb += (
                f"# Parent Function: "
                f"{chunk['parent_function']}\n"
            )

        if chunk.get("part"):
            breadcrumb += (
                f"# Part: "
                f"{chunk['part']}/"
                f"{chunk['total_parts']}\n"
            )

        content = (
            breadcrumb
            + "\n"
            + chunk["code"]
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "repository": chunk["repository"],
                    "file_path": chunk["file_path"],
                    "class_name": chunk["class_name"] or "",
                    "name": chunk["name"],
                    "chunk_type": chunk["chunk_type"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "parent_function": (
                        chunk["parent_function"] or ""
                    ),
                    "part": chunk["part"] or 0,
                    "total_parts": (
                        chunk["total_parts"] or 0
                    ),
                },
            )
        )

    print(f"Prepared {len(documents)} documents.")
    print("Creating embeddings and storing in ChromaDB...")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )

    client = PersistentClient(
    path=".chroma"
    )

    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        print(f"No existing collection found: {COLLECTION_NAME}")

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=".chroma",
    )

    vectorstore.add_documents(documents)

    print()
    print("Code index created successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents indexed: {len(documents)}")


if __name__ == "__main__":
    build_code_index()