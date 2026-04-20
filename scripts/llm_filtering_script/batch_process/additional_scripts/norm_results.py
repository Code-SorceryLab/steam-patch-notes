import json
from collections import OrderedDict

def canonicalize(x):
    if isinstance(x, dict):
        # sort keys for stable, readable structure
        return OrderedDict((k, canonicalize(x[k])) for k in sorted(x.keys()))
    if isinstance(x, list):
        return [canonicalize(v) for v in x]
    return x

def normalize_jsonl(in_path: str, out_path: str) -> None:
    with open(in_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
        for lineno, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # keep even bad lines as readable records (still "all info" you have)
                out = OrderedDict([
                    ("key", None),
                    ("response", None),
                    ("_error", "invalid_json"),
                    ("_lineno", lineno),
                    ("_raw", line),
                ])
                fout.write(json.dumps(out, ensure_ascii=False) + "\n")
                continue

            if not isinstance(obj, dict):
                # if a line is not an object, wrap it so format stays consistent
                out = OrderedDict([
                    ("key", None),
                    ("response", None),
                    ("value", canonicalize(obj)),
                ])
                fout.write(json.dumps(out, ensure_ascii=False) + "\n")
                continue

            # canonicalize everything first (deep sort)
            obj_c = canonicalize(obj)

            # force top-level order: key, response, then the rest
            out = OrderedDict()
            out["key"] = obj_c.get("key", None)
            out["response"] = obj_c.get("response", None)

            for k in obj_c.keys():
                if k not in ("key", "response"):
                    out[k] = obj_c[k]

            fout.write(json.dumps(out, ensure_ascii=False) + "\n")

# Example:
normalize_jsonl("scripts/llm_filtering/batch_process/jsonl/results.jsonl", "scripts/llm_filtering/batch_process/jsonl/norm.jsonl")
