import json
from pathlib import Path

# Deletes files with 0 notes from llm_filtered_patches/.
LLM_FILTERED = Path(__file__).resolve().parents[4] / "patches" / "llm_filtered_patches"


def main():
    files = list(LLM_FILTERED.glob("*.json"))
    if not files:
        print(f"No files found in {LLM_FILTERED}")
        return

    deleted = 0
    for p in files:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not data.get("notes"):
            p.unlink()
            deleted += 1

    print(f"Deleted {deleted} empty files. {len(files) - deleted} files remain.")


if __name__ == "__main__":
    main()
