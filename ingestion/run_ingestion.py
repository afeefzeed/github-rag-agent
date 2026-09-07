import subprocess
import sys
from pathlib import Path


from ingestion.build_code_index import code_index_exists


def run_script(script_name: str):
    print()
    print("=" * 60)
    print(f"Running: {script_name}")
    print("=" * 60)

    subprocess.run(
        [sys.executable, f"ingestion/{script_name}"],
        check=True,
    )


def ensure_code_index():
    """Build the Code RAG index if it does not exist."""

    if code_index_exists():
        print("Code RAG index already exists.")
        return

    print("Code RAG index not found.")
    print("Building Code RAG index...")

    run_script("ingest_repo.py")
    run_script("build_dataset.py")
    run_script("build_code_index.py")

    print()
    print("=" * 60)
    print("Code RAG index created successfully.")
    print("=" * 60)


if __name__ == "__main__":
    ensure_code_index()