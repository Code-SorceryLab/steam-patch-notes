import json
from file_handler import FileHandler
from pathlib import Path

class ResultParser:
    def __init__(self, results_path: str, notes_path: str, filtered_notes_path: str, filename: str = "results.jsonl"):

        self.results_handler = FileHandler(results_path, filtered_notes_path)
        self.notes_handler = FileHandler(notes_path, filtered_notes_path)
        self.results_path = Path(results_path)
        self.filename = filename

    def merge_results(self, part_filenames: list):
        final_path = self.results_path.parent / self.filename
        with open(final_path, 'wb') as out:
            for part_file in sorted(part_filenames):
                part_path = self.results_path / part_file
                if part_path.exists():
                    with open(part_path, 'rb') as pf:
                        out.write(pf.read())
        print(f"Merged {len(part_filenames)} parts into {self.filename}")

    def parse_results(self):
        results = {}
        for line in (self.results_path.parent / self.filename).open("r", encoding="utf-8"):
            line = json.loads(line)
            appid = line["key"].split("::")[0]
            text = line["response"]["candidates"][0]["content"]["parts"][0]["text"]
            tags = json.loads(text)
            if not tags:  # skip []
                continue
            results.setdefault(appid, {})[line["key"]] = tags

        return results

    def apply_tags(self, results):
        for batch in self.notes_handler.import_games(5):
            for game, fname in batch:
                for note in game.notes:
                    if note.key in results.get(game.app_id, {}):
                        note.tags = results[game.app_id][note.key]
                self.notes_handler.export_games(game, fname)
                print(f"Applied tags to id: {game.app_id}")
        print("All tags applied")
        




