import ast
from pathlib import Path

MAX_CHUNK_LINES = 100
LARGE_CHUNK_LIMIT = 200


def extract_code_chunks(file_path: Path, repo_root: Path) -> list[dict]:
    """Extract Python code into retrieval-friendly AST chunks."""

    source = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    tree = ast.parse(source)

    relative_path = file_path.relative_to(repo_root)
    lines = source.splitlines()

    chunks = []

    def get_code(node):
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        code = "\n".join(
            lines[start_line - 1:end_line]
        )

        return start_line, end_line, code

    def add_chunk(
        node,
        chunk_type,
        name,
        class_name=None,
        parent_function=None,
        part=None,
        total_parts=None,
    ):
        start_line, end_line, code = get_code(node)

        chunks.append({
            "chunk_type": chunk_type,
            "name": name,
            "class_name": class_name,
            "parent_function": parent_function,
            "file_path": str(relative_path),
            "start_line": start_line,
            "end_line": end_line,
            "part": part,
            "total_parts": total_parts,
            "code": code,
        })

    def split_large_function(
        node,
        chunk_type,
        name,
        class_name=None,
        parent_function=None,
    ):
        """
        Split a large function using its top-level AST statements.

        Nested functions are recursively split instead of being
        treated as one huge statement.
        """

        body = list(node.body)

        # Remove the function docstring.
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]

        if not body:
            return

        groups = []
        current_group = []
        current_start = None

        def flush_group():
            nonlocal current_group, current_start

            if current_group:
                groups.append(current_group)

            current_group = []
            current_start = None

        for statement in body:
            statement_start = statement.lineno
            statement_end = getattr(
                statement,
                "end_lineno",
                statement_start
            )

            statement_lines = (
                statement_end - statement_start + 1
            )

            # Nested function/class: process it separately.
            if isinstance(
                statement,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                flush_group()

                nested_type = (
                    "nested_async_function"
                    if isinstance(
                        statement,
                        ast.AsyncFunctionDef
                    )
                    else "nested_function"
                )

                process_function(
                    statement,
                    nested_type,
                    statement.name,
                    class_name,
                    parent_function=name,
                )

                continue

            # If this statement would make the current group
            # larger than the target size, start a new group.
            if current_group:
                proposed_lines = (
                    statement_end - current_start + 1
                )

                if proposed_lines > MAX_CHUNK_LINES:
                    flush_group()

            if not current_group:
                current_start = statement_start

            current_group.append(statement)

        flush_group()

        total_parts = len(groups)

        for part_number, group in enumerate(
            groups,
            start=1
        ):
            start_line = group[0].lineno
            end_line = getattr(
                group[-1],
                "end_lineno",
                group[-1].lineno
            )

            code = "\n".join(
                lines[start_line - 1:end_line]
            )

            chunks.append({
                "chunk_type": f"{chunk_type}_part",
                "name": name,
                "class_name": class_name,
                "parent_function": parent_function,
                "file_path": str(relative_path),
                "start_line": start_line,
                "end_line": end_line,
                "part": part_number,
                "total_parts": total_parts,
                "code": code,
            })

    def process_function(
        node,
        chunk_type,
        name,
        class_name=None,
        parent_function=None,
    ):
        start_line, end_line, _ = get_code(node)

        line_count = end_line - start_line + 1

        if line_count > LARGE_CHUNK_LIMIT:
            split_large_function(
                node,
                chunk_type,
                name,
                class_name,
                parent_function,
            )
        else:
            add_chunk(
                node,
                chunk_type,
                name,
                class_name,
                parent_function,
            )

    for node in tree.body:

        # Classes
        if isinstance(node, ast.ClassDef):

            class_start, class_end, _ = get_code(node)
            class_lines = class_end - class_start + 1

            # Only keep reasonably sized classes.
            if class_lines <= MAX_CHUNK_LINES:
                add_chunk(
                    node,
                    "class",
                    node.name,
                    node.name
                )

            # Extract methods separately.
            for child in node.body:

                if isinstance(
                    child,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    method_type = (
                        "async_method"
                        if isinstance(
                            child,
                            ast.AsyncFunctionDef
                        )
                        else "method"
                    )

                    process_function(
                        child,
                        method_type,
                        child.name,
                        node.name,
                    )

        # Top-level functions
        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            function_type = (
                "async_function"
                if isinstance(
                    node,
                    ast.AsyncFunctionDef
                )
                else "function"
            )

            process_function(
                node,
                function_type,
                node.name,
            )

    return chunks


if __name__ == "__main__":
    repo_root = Path("data/repos/langgraph")

    test_file = (
        repo_root
        / "libs"
        / "langgraph"
        / "langgraph"
        / "pregel"
        / "main.py"
    )

    chunks = extract_code_chunks(
        test_file,
        repo_root
    )

    for chunk in chunks:
        if chunk["name"] == "bulk_update_state":
            print("=" * 60)
            print(f"Type: {chunk['chunk_type']}")
            print(f"Name: {chunk['name']}")
            print(f"Class: {chunk['class_name']}")
            print(f"Parent: {chunk['parent_function']}")
            print(
                f"Lines: "
                f"{chunk['start_line']} - "
                f"{chunk['end_line']}"
            )
            print(
                f"Part: "
                f"{chunk['part']} / "
                f"{chunk['total_parts']}"
            )
            print(
                f"Size: "
                f"{chunk['end_line'] - chunk['start_line'] + 1} lines"
            )
            print()