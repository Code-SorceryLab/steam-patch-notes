from pathlib import Path
import json
from game_data import GameData

class FileHandler:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def get_files(self):
        # Iterate over all files
        for filename in Path(self.input_path).iterdir():
            game = GameData.from_file(file_path=filename)   # create GameData instance
            yield game, filename
        
    def process_is_patch_notes(self):
        for game, filename in self.get_files():
            game.filter_notes()
            self.export_files(game, filename.name)
        
    def process_html_to_text(self):
        for game, filename in self.get_files():
            game.html_to_text()
            self.export_files(game, filename.name)

    def export_files(self, game, filename):
        output_path = self.output_path / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(game.data, f, ensure_ascii=False, indent=4)
        
    
