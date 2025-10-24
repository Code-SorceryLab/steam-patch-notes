from pathlib import Path
import re

from game_data import GameData
from game_data import PatchNote
from file_handler import FileHandler

def strip_html(content: str) -> str:
    if not content:
        return ""
    import html
    content = html.unescape(content)
    content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)
    content = re.sub(r"<[^>]+>", "", content)  
    content = re.sub(r"\[/?(b|i|u|quote|list|\*|url|img|h[1-6])(?:=[^\]]+)?\]", "", content, flags=re.IGNORECASE)
    content = content.replace("[p]", "\n").replace("[/p]", "\n")
    return content.strip()

def main(input_path, output_path):
    handler = FileHandler(input_path, output_path)
        
    # loop over yeilded files
    for game, filename in handler.import_files():
        stripped_notes = []
        for note in game.notes:
            new_content = strip_html(note.content)
            new_note = PatchNote(
                title=note.title,
                date=note.date,
                url=note.url,
                content=new_content
            )
            stripped_notes.append(new_note)

        if stripped_notes:
            stripped_game = GameData(game.app_id, len(stripped_notes), stripped_notes)
            print(game.app_id)
            handler.export_file(stripped_game, filename)

if __name__ == "__main__":
    # define input and output directory to FileHandler
    input_path = "..."
    output_path = "..."
        
    main(input_path, output_path)