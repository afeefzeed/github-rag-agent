from pathlib import Path


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


def should_include_file(file_path: Path) -> bool:
    # Ignore hidden files
    if file_path.name.startswith("."):
        return False

    # Only process supported file types
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False

    # Ignore very large files
    if file_path.stat().st_size > MAX_FILE_SIZE:
        return False

    # Ignore files inside excluded directories
    if any(part in IGNORED_DIRECTORIES for part in file_path.parts):
        return False

    return True


def get_source_files() -> list[Path]:
    source_files = []

    for file_path in REPO_DIR.rglob("*"):
        if file_path.is_file() and should_include_file(file_path):
            source_files.append(file_path)

    return source_files


if __name__ == "__main__":
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
    print(f"Documentation files: {len(documentation_files)}")