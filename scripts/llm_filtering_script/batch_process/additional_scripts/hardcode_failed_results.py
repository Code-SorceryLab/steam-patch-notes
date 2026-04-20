import json
from pathlib import Path

# Creates hardcoded [] result files for failed batch requests.
# --- Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
BATCH_PROCESS = SCRIPT_DIR.parent
TEMP_SINGLE = BATCH_PROCESS / "temp_single_calls"

FAILED_DIRS = [
    TEMP_SINGLE / "failed",
    TEMP_SINGLE / "failed-3",
]

OUTPUT_DIR = BATCH_PROCESS / "jsonl" / "failed_resp_results"

# Hardcoded response template
EMPTY_RESPONSE = {
    "response": {
        "candidates": [
            {
                "finishReason": "STOP",
                "index": 0,
                "content": {
                    "parts": [{"text": "[]"}],
                    "role": "model",
                },
            }
        ],
        "modelVersion": "hardcoded-empty",
        "usageMetadata": {
            "totalTokenCount": 0,
            "candidatesTokenCount": 0,
            "promptTokenCount": 0,
        },
        "responseId": "hardcoded",
    }
}


def process_failed_dir(failed_dir: Path, output_dir: Path) -> tuple[int, int]:
    files_written = 0
    total_requests = 0

    for part_file in sorted(failed_dir.glob("*.jsonl")):
        with open(part_file, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        if not lines:
            continue

        # Extract the numeric part id by stripping all "failed_" prefixes then "part_"
        stem = part_file.stem
        while stem.startswith("failed_"):
            stem = stem[len("failed_"):]
        # stem is now e.g. "part_1258"
        part_id = stem  # e.g. "part_1258"
        out_name = f"results_{part_id}.jsonl"
        out_path = output_dir / out_name

        with open(out_path, "w", encoding="utf-8") as out:
            for line in lines:
                data = json.loads(line)
                key = data["key"]
                result = {"key": key, **EMPTY_RESPONSE}
                # Deep copy response so each line gets its own dict
                result = {
                    "key": key,
                    "response": {
                        "candidates": [
                            {
                                "finishReason": "STOP",
                                "index": 0,
                                "content": {
                                    "parts": [{"text": "[]"}],
                                    "role": "model",
                                },
                            }
                        ],
                        "modelVersion": "hardcoded-empty",
                        "usageMetadata": {
                            "totalTokenCount": 0,
                            "candidatesTokenCount": 0,
                            "promptTokenCount": 0,
                        },
                        "responseId": "hardcoded",
                    },
                }
                out.write(json.dumps(result, ensure_ascii=False) + "\n")
                total_requests += 1

        files_written += 1
        print(f"  {part_file.name} -> {out_name} ({len(lines)} requests)")

    return files_written, total_requests


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_requests = 0

    for failed_dir in FAILED_DIRS:
        if not failed_dir.exists():
            print(f"Skipping {failed_dir.name}/ (not found)")
            continue

        print(f"\nProcessing {failed_dir.name}/")
        files, requests = process_failed_dir(failed_dir, OUTPUT_DIR)
        total_files += files
        total_requests += requests
        print(f"  -> {files} files, {requests} requests")

    print(f"\nDone. {total_files} result files written to {OUTPUT_DIR}")
    print(f"Total hardcoded responses: {total_requests}")


if __name__ == "__main__":
    main()
