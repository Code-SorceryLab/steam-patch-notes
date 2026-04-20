import json
from pathlib import Path

# Merges hardcoded [] results into the matching result_parts files.
# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
BATCH_PROCESS = SCRIPT_DIR.parent

FAILED_RESP = BATCH_PROCESS / "jsonl" / "failed_resp_results"
RESULT_PARTS = BATCH_PROCESS / "jsonl" / "result_parts"


def load_existing_keys(part_path: Path) -> set:
    keys = set()
    with open(part_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                keys.add(json.loads(line)["key"])
            except (json.JSONDecodeError, KeyError):
                pass
    return keys


def main():
    source_files = sorted(FAILED_RESP.glob("*.jsonl"))

    if not source_files:
        print("No files found in failed_resp_results/")
        return

    total_appended = 0
    total_skipped = 0
    files_touched = 0

    for src in source_files:
        dest = RESULT_PARTS / src.name
        if not dest.exists():
            print(f"  SKIP {src.name} — no matching file in result_parts/")
            continue

        # Load keys already in the destination to avoid duplicates
        existing_keys = load_existing_keys(dest)

        with open(src, encoding="utf-8") as sf:
            new_lines = [l.strip() for l in sf if l.strip()]

        to_append = []
        for line in new_lines:
            try:
                key = json.loads(line)["key"]
            except (json.JSONDecodeError, KeyError):
                continue
            if key in existing_keys:
                total_skipped += 1
            else:
                to_append.append(line)

        if not to_append:
            continue

        with open(dest, "a", encoding="utf-8") as df:
            for line in to_append:
                df.write(line + "\n")

        total_appended += len(to_append)
        files_touched += 1
        print(f"  {src.name}: appended {len(to_append)} lines ({len(new_lines) - len(to_append)} duplicates skipped)")

    print(f"\nDone. {files_touched} files updated, {total_appended} lines appended, {total_skipped} duplicates skipped.")


if __name__ == "__main__":
    main()
