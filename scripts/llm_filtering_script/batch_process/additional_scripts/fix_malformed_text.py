import json
from pathlib import Path

# Fixes malformed text values in result_parts before merge/parsing.
RESULT_PARTS = Path(__file__).resolve().parents[1] / "jsonl" / "result_parts"


def fix_part(part_path: Path) -> int:
    with open(part_path, encoding="utf-8") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    fixed = 0
    out_lines = []
    for raw in raw_lines:
        entry = json.loads(raw)
        text = entry["response"]["candidates"][0]["content"]["parts"][0]["text"]
        try:
            json.loads(text)
        except json.JSONDecodeError:
            entry["response"]["candidates"][0]["content"]["parts"][0]["text"] = "[]"
            fixed += 1
        out_lines.append(json.dumps(entry, ensure_ascii=False))

    if fixed:
        with open(part_path, "w", encoding="utf-8") as f:
            for line in out_lines:
                f.write(line + "\n")

    return fixed


def main():
    part_files = sorted(RESULT_PARTS.glob("*.jsonl"))
    if not part_files:
        print(f"No .jsonl files found in {RESULT_PARTS}")
        return

    total_files = 0
    total_fixed = 0

    for part in part_files:
        fixed = fix_part(part)
        if fixed:
            total_files += 1
            total_fixed += fixed
            print(f"  {part.name}: fixed {fixed} entries")

    print(f"\nDone. {total_fixed} entries fixed across {total_files} files.")


if __name__ == "__main__":
    main()
