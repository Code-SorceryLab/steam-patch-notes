from pathlib import Path
import re

from game_data import GameData
from file_handler import FileHandler

# def is_patch_note(title, content):
#     if not content or content.strip() == "":
#         return False
    
#     keywords = re.compile(r"\b(patch|update|hotfix|release|version|release notes?|changelog|changes|bug\s*fix(es)?)\b",re.IGNORECASE)
                
#     if keywords.search(title or ""):
#         return True
#     return bool(keywords.search(content) or re.search(r"(^|\n)\s*(?:- |\* |• )", content))

def is_patch_note(title: str, content: str) -> bool:
    if not content or content.strip() == "":
        return False

    title_keywords = re.compile(
        r"\b("
        r"patch\s*(notes?)?|"
        r"(?:update|hotfix|changelog|release\s*notes?)"
        r")\b"
        r"(?:\s*v?\d+(\.\d+)*|\s*[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})?",
        re.IGNORECASE
    )

    # Detect structured bulleted formatting or changelog patterns in body
    body_keywords = re.compile(
        r"(^|\n)\s*(?:- |\* |\• |\[list\]|\[h\d\]|\d+\.)", re.IGNORECASE
    )

    if title_keywords.search(title or ""):
        return True

    if body_keywords.search(content):
        return True

    if re.search(r"(^|\n)\s*(fixed|added|changed|removed|improved)\b", content, re.IGNORECASE):
        return True

    return False

def main(input_path, output_path):
    handler = FileHandler(input_path, output_path)

    # loop over yeilded files
    for game, filename in handler.import_files():
        filtered_notes = []
        for note in game.notes:
            if is_patch_note(note.title, note.content):
                filtered_notes.append(note)
    
        if filtered_notes:
            filtered_game = GameData(game.app_id, len(filtered_notes), filtered_notes)
            print(game.app_id)
            handler.export_file(filtered_game, filename)

if __name__ == "__main__":
    # define input and output directory to FileHandler
    input_path = "..."
    output_path = "..."
        
    main(input_path, output_path)