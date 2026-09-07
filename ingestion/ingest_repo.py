import subprocess
from pathlib import Path


REPO_URL = "https://github.com/langchain-ai/langgraph.git"
REPO_DIR = Path("data/repos/langgraph")

ALLOWED_EXTENSIONS = {
    ".py",
    ".md",
    ".mdx",
}

IGNORED_DIRECTORIES = {
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

MAX_FILE_SIZE = 200 * 1024  # 200 KB


def clone_repository():
    """Clone LangGraph if it is not already available."""

    REPO_DIR.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if REPO_DIR.exists():
        print(f"Repository already exists: {REPO_DIR}")
        return

    print(f"Cloning {REPO_URL}...")

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            REPO_URL,
            str(REPO_DIR),
        ],
        check=True,
    )

    print(
        f"Repository cloned successfully: {REPO_DIR}"
    )


def should_include_file(file_path: Path) -> bool:
    """Determine whether a file should be included in Code RAG."""

    if file_path.name.startswith("."):
        return False

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False

    if file_path.stat().st_size > MAX_FILE_SIZE:
        return False

    if any(
        part in IGNORED_DIRECTORIES
        for part in file_path.parts
    ):
        return False

    return True


def get_source_files() -> list[Path]:
    """Return source files suitable for Code RAG."""

    source_files = []

    for file_path in REPO_DIR.rglob("*"):
        if (
            file_path.is_file()
            and should_include_file(file_path)
        ):
            source_files.append(file_path)

    return source_files


if __name__ == "__main__":
    clone_repository()

    files = get_source_files()

    python_files = [
        file_path
        for file_path in files
        if file_path.suffix.lower() == ".py"
    ]

    documentation_files = [
        file_path
        for file_path in files
        if file_path.suffix.lower() in {".md", ".mdx"}
    ]

    print(f"Repository: {REPO_DIR}")
    print(f"Total selected files: {len(files)}")
    print(f"Python files: {len(python_files)}")
    print(
        f"Documentation files: "
        f"{len(documentation_files)}"
    )