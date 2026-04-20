import json
from pathlib import Path
from typing import Generator, Tuple
from game_data import GameData
from dataclasses import asdict

class FileHandler:
    def __init__(self, input: str, output: str):
        self.input_path = Path(input)
        self.output_path = Path(output)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    # Generator that yields GameData instances one by one
    def import_games(self, batch_size = 1) -> Generator[Tuple[GameData, str], None, None]:
        batch = []
        for file in self.input_path.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            game = GameData.process_instance(raw_data)
            batch.append((game, file.name))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    # Exports filtered game data to output directory (Creates new files in output directory)     
    def export_games(self, game: GameData, filename: str):
        out_path = self.output_path / filename
        game.notes = [note for note in game.notes if note.tags]  # Only export notes that have tags
        if not game.notes:
            return
        data = {
            "appId": game.app_id,
            "count": len(game.notes),
            "notes": [asdict(note) for note in game.notes],
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    # Rewrites original game files with keys included (overwrites original files)
    def export_game_keys(self, game: GameData, filename: str):
        out_path = self.input_path / filename
        data = {
            "appId": game.app_id,
            "count": game.count,
            "notes": [asdict(note) for note in game.notes]
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    # Appends to batch.jsonl file
    def export_jsonl(self, lines: list, filename: str = "batch.jsonl", out_path: Path = None):
        out_path = out_path or (self.output_path / filename)
        if not out_path.exists():
            out_path.touch()

        with open(out_path, 'a', encoding='utf-8') as f:
            print(f"Exporting {len(lines)} lines")
            for line in lines:
                f.write(line + "\n")

    # Imports batch.jsonl file 
    def import_jsonl(self, filename: str = "batch.jsonl", in_path: Path = None) -> Path:
        in_path = in_path or (self.input_path / filename)
        return in_path
    
    # Exports results.jsonl file
    def export_download(self, bytes, filename: str):
        with open(self.output_path/ filename, 'wb') as f:
            f.write(bytes)