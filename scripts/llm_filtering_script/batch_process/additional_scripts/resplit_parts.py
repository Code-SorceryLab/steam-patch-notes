import json
from pathlib import Path

BATCH_PARTS = Path("scripts/llm_filtering/batch_process/jsonl/batch_parts")
JOB_ID_PATH = Path("scripts/llm_filtering/batch_process/job_id/job_ids.json")
UPLOAD_ID_PATH = Path("scripts/llm_filtering/batch_process/job_id/upload_ids.json")


def load_json(path: Path) -> dict:
    if path.exists():
        content = path.read_text().strip()
        if content:
            return json.loads(content)
    return {}


def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2))


def resplit(lines_per_part: int, start_num: int):
    old_parts = sorted(BATCH_PARTS.glob("*.jsonl"))
    if not old_parts:
        print("No parts found in batch_parts/")
        return

    print(f"Found {len(old_parts)} old parts to re-split into {lines_per_part}-line chunks")

    # Collect all lines
    all_lines = []
    old_filenames = set()

    for part in old_parts:
        old_filenames.add(part.name)
        with part.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.rstrip("\n")
                if stripped:
                    all_lines.append(stripped)

    total_lines = len(all_lines)
    print(f"Total lines: {total_lines}")

    # Split
    part_num = start_num
    new_filenames = []

    for i in range(0, total_lines, lines_per_part):
        chunk = all_lines[i:i + lines_per_part]
        filename = f"part_{part_num:04d}.jsonl"
        out_path = BATCH_PARTS / filename

        out_path.write_text("\n".join(chunk) + "\n", encoding="utf-8")

        new_filenames.append(filename)
        part_num += 1

    print(f"Created {len(new_filenames)} new parts: {new_filenames[0]} ... {new_filenames[-1]}")

    # Delete old parts
    new_set = set(new_filenames)
    deleted = 0
    for part in old_parts:
        if part.name not in new_set:
            part.unlink()
            deleted += 1

    print(f"Deleted {deleted} old part files")

    # Clean stale entries
    for tracking_path, label in [(JOB_ID_PATH, "job_ids"), (UPLOAD_ID_PATH, "upload_ids")]:
        data = load_json(tracking_path)
        if not data:
            continue

        stale = [k for k in data if k in old_filenames and k not in new_set]

        for k in stale:
            del data[k]

        save_json(tracking_path, data)

        if stale:
            print(f"Cleaned {len(stale)} stale entries from {label}.json")


if __name__ == "__main__":
    resplit(lines_per_part=3000, start_num=25)