import json
from pathlib import Path

from code_parser import extract_code_chunks


REPO_ROOT = Path("data/repos/langgraph")
OUTPUT_FILE = Path("data/langgraph_code_chunks.json")


def get_python_files():
    """Find all Python files that passed our filtering rules."""

    ignored_directories = {
        ".git",
        ".github",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "eggs",
        "site-packages",
        "tests",
        "test",
    }

    max_file_size = 200 * 1024

    python_files = []

    for file_path in REPO_ROOT.rglob("*.py"):

        if file_path.name.startswith("."):
            continue

        if any(
            part in ignored_directories
            for part in file_path.parts
        ):
            continue

        if file_path.stat().st_size > max_file_size:
            continue

        python_files.append(file_path)

    return python_files


def build_dataset():
    python_files = get_python_files()

    print(f"Python files found: {len(python_files)}")
    print("Parsing files...")

    all_chunks = []

    for index, file_path in enumerate(python_files, start=1):

        try:
            chunks = extract_code_chunks(
                file_path,
                REPO_ROOT,
            )

            for chunk in chunks:
                chunk["repository"] = "langgraph"

            all_chunks.extend(chunks)

        except SyntaxError as error:
            print(f"Skipping invalid Python file: {file_path}")
            print(f"Reason: {error}")

        if index % 25 == 0:
            print(
                f"Processed {index}/{len(python_files)} files..."
            )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            all_chunks,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("Dataset created successfully.")
    print(f"Total code chunks: {len(all_chunks)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_dataset()