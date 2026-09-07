import os

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),
)

vectorstore = Chroma(
    collection_name="code_chunks",
    embedding_function=embeddings,
    persist_directory=".chroma",
)

query = "StateGraph add_node"

results = vectorstore.similarity_search(
    query,
    k=3,
)

for i, document in enumerate(results, start=1):
    print("=" * 60)
    print(f"RESULT {i}")
    print(f"File: {document.metadata['file_path']}")
    print(f"Function: {document.metadata['name']}")
    print(f"Class: {document.metadata['class_name']}")
    print(
        f"Lines: "
        f"{document.metadata['start_line']}-"
        f"{document.metadata['end_line']}"
    )
    print()
    print(document.page_content[:1000])
    print()