import hashlib
import json
import os
from file_handler import FileHandler
from pathlib import Path
import prompts

LINES = []

class JSONLConverter:
    def __init__(self, input_path: str, output_path: str, filename: str = "batch.jsonl"):
        self.handler = FileHandler(input_path, output_path)
        self.filename = filename

        Path(output_path).mkdir(parents=True, exist_ok=True)
        (Path(output_path) / filename).write_text("") 

        batch_parts_path = Path(output_path) / "batch_parts"
        batch_parts_path.mkdir(parents=True, exist_ok=True)
        for file in batch_parts_path.glob("*.jsonl"):
            print(file.name+" removed from output directory.")
            file.unlink()

    def _get_keys(self, app_id: str, url: str):
        return f"{app_id}::{hashlib.sha1(url.encode('utf-8')).hexdigest()}"
    
    def _create_line(self, key: str, user_prompt: str, system_prompt: str):
        line = {
            "key": key,
            "request": {
                "contents": [
                    {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                    }
                ],
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "generationConfig": {
                    "temperature": 0.0,
                    "thinking_config": {
                        "include_thoughts": False,
                        "thinking_budget": 0
                    },
                    "responseMimeType": "application/json",
                    "responseSchema": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "bug": {"type": "STRING"},
                                "feature": {"type": "STRING"},
                                "balance_change": {"type": "STRING"}
                            }
                        }
                    }
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            }
        }

        return json.dumps(line, ensure_ascii=False)

    def generate_jsonl(self):
        limit = 25000
        count = 0

        games = []
        for batch in self.handler.import_games(5):
            
            # Pass 1: Assign keys and save source files first
            for game, filename in batch:
                for note in game.notes:
                    note.key = self._get_keys(game.app_id, note.url)
                self.handler.export_game_keys(game, filename)
                games.append(game)

                # Pass 2: Generate JSONL (source files already have keys)
                for game in games:
                    print(f"Processing App ID: {game.app_id} with {len(game.notes)} notes")
                    for note in game.notes:
                        user_prompt = prompts.build_prompt(note.title, note.content)
                        system_prompt = prompts.get_system_prompt()
                        line = self._create_line(note.key, user_prompt, system_prompt)
                        if count >= limit:
                            self.handler.export_jsonl(LINES, self.filename)
                            LINES.clear()
                            count = 0
                            continue
                        LINES.append(line)
                        count += 1
                    self.handler.export_jsonl(LINES, self.filename)
                games.clear()
                LINES.clear()

    # Split JSONL into parts of 2000 lines each for batch processing
    def split_jsonl(self, max_lines=2000):
        full_jsonl = self.handler.import_jsonl(self.filename, in_path=Path(self.handler.output_path) / self.filename)
        output_dir = full_jsonl.parent / "batch_parts"
        output_dir.mkdir(parents=True, exist_ok=True)

        part_num = 1
        lines = []
        filenames = []

        with full_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                lines.append(line)

                if len(lines) >= max_lines:
                    self.handler.export_jsonl(
                        lines=lines,
                        filename=f"part_{part_num:03d}.jsonl",
                        out_path=output_dir / f"part_{part_num:03d}.jsonl"
                    )
                    filenames.append(f"part_{part_num:03d}.jsonl")
                    part_num += 1
                    lines = []

        if lines:
            self.handler.export_jsonl(
                lines=lines,
                filename=f"part_{part_num:03d}.jsonl",
                out_path=output_dir / f"part_{part_num:03d}.jsonl"
            )
            filenames.append(f"part_{part_num:03d}.jsonl")

        return filenames

    def generate_jsonl_parts(self,):
        self.generate_jsonl()
        self.split_jsonl()

# Test--------------------------------------------------------------
def test():
    filtered_patches_path = "patches/filtered_patches"
    batch_jsonl_path = "scripts/llm_filtering/batch_process/jsonl"
    response_jsonl_path = "scripts/llm_filtering/batch_process/jsonl"
    llm_filtered_path = "patches/llm_filtered_patches"
    jsonl_filename = "batch.jsonl"
    results_filename = "results.jsonl"

    converter = JSONLConverter(filtered_patches_path, batch_jsonl_path, jsonl_filename)
    # converter.generate_jsonl()
    converter.split_jsonl()

if __name__ == "__main__":
    test()