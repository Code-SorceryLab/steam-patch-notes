import json
from pathlib import Path

# Normalizes result_parts responses before merge/parsing.
RESULT_PARTS = Path(__file__).resolve().parents[1] / "jsonl" / "result_parts"

EMPTY_CANDIDATE = {
    "finishReason": "STOP",
    "index": 0,
    "content": {
        "parts": [{"text": "[]"}],
        "role": "model",
    },
}

EMPTY_RESPONSE = {
    "candidates": [EMPTY_CANDIDATE],
    "modelVersion": "hardcoded-empty",
    "usageMetadata": {
        "totalTokenCount": 0,
        "candidatesTokenCount": 0,
        "promptTokenCount": 0,
    },
    "responseId": "hardcoded",
}


def needs_normalization(entry: dict) -> bool:
    cands = entry["response"].get("candidates", [])
    if not cands:
        return True
    if "content" not in cands[0]:
        return True
    return False


def normalize_part(part_path: Path) -> int:
    with open(part_path, encoding="utf-8") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    fixed = 0
    out_lines = []
    for raw in raw_lines:
        entry = json.loads(raw)
        if needs_normalization(entry):
            entry["response"] = dict(EMPTY_RESPONSE)
            entry["response"]["candidates"] = [dict(EMPTY_CANDIDATE)]
            entry["response"]["candidates"][0]["content"] = {
                "parts": [{"text": "[]"}],
                "role": "model",
            }
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

    total_files_touched = 0
    total_fixed = 0

    for part in part_files:
        fixed = normalize_part(part)
        if fixed:
            total_files_touched += 1
            total_fixed += fixed
            print(f"  {part.name}: fixed {fixed} entries")

    print(f"\nDone. {total_fixed} entries normalized across {total_files_touched} files.")


if __name__ == "__main__":
    main()
