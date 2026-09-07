import json
from pathlib import Path
from collections import Counter

DATASET_FILE = Path("data/langgraph_code_chunks.json")


def analyze_dataset():
    with DATASET_FILE.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"Total chunks: {len(chunks)}")
    print()

    # Chunk type distribution
    type_counts = Counter(chunk["chunk_type"] for chunk in chunks)

    print("Chunk types:")
    for chunk_type, count in type_counts.items():
        print(f"  {chunk_type}: {count}")

    print()

    # Calculate code sizes
    for chunk in chunks:
        chunk["line_count"] = (
            chunk["end_line"] - chunk["start_line"] + 1
        )
        chunk["char_count"] = len(chunk["code"])

    line_counts = [chunk["line_count"] for chunk in chunks]

    average_lines = sum(line_counts) / len(line_counts)

    print(f"Average lines per chunk: {average_lines:.2f}")
    print()

    # Largest chunks
    largest_chunks = sorted(
        chunks,
        key=lambda chunk: chunk["line_count"],
        reverse=True
    )[:10]

    print("Largest 10 chunks:")
    print()

    for index, chunk in enumerate(largest_chunks, start=1):
        print(
            f"{index}. "
            f"{chunk['chunk_type']} "
            f"{chunk['class_name']}.{chunk['name']} "
            f"→ {chunk['line_count']} lines "
            f"({chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']})"
        )

    print()

    # Very large chunks
    large_chunks = [
        chunk for chunk in chunks
        if chunk["line_count"] > 100
    ]

    print(f"Chunks larger than 100 lines: {len(large_chunks)}")


if __name__ == "__main__":
    analyze_dataset()