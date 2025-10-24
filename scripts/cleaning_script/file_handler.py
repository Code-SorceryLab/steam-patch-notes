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

    # def get_files(self):
    #     # Iterate over all files
    #     for filename in Path(self.input_path).iterdir():
    #         game = GameData.from_file(file_path=filename)   # create GameData instance
    #         yield game, filename
        
    # def process_is_patch_notes(self):
    #     for game, filename in self.get_files():
    #         game.filter_notes()
    #         self.export_files(game, filename.name)
        
    # def process_html_to_text(self):
    #     for game, filename in self.get_files():
    #         game.html_to_text()
    #         self.export_files(game, filename.name)

    # def export_files(self, game, filename):
    #     output_path = self.output_path / filename
    #     output_path.parent.mkdir(parents=True, exist_ok=True)
    #     with output_path.open("w", encoding="utf-8") as f:
    #         json.dump(game.data, f, ensure_ascii=False, indent=4)
        
    
    def import_files(self) -> Generator[Tuple[GameData, str], None, None]:
        for file in self.input_path.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            game = GameData.process_instance(raw_data)
            yield game, file.name

    def export_file(self, game: GameData, filename: str):
        out_path = self.output_path / filename
        data = {
            "appId": game.app_id,
            "count": game.count,
            "notes": [asdict(note) for note in game.notes]
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)