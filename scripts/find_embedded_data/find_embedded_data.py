from bs4 import BeautifulSoup
from pathlib import Path

from game_data import GameData
from file_handler import FileHandler

def flag_notes(html: str) -> bool:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(strip=True)
    anchors = soup.find_all("a")
    images = soup.find_all("img")
    return len(text) < 30 and (len(anchors) > 0 or len(images) > 0) # returns true if text is less than 30 characters and contains at least one link or image

def main(input_path, output_path):
    handler = FileHandler(input_path, output_path)
    list_ids = set() #store ids for logging
    count = 0 #store total count of flagged notes

    # loop over yeilded files
    for game, filename in handler.import_files():
        flagged_notes = []
        for note in game.notes:
            if flag_notes(note.content):
                flagged_notes.append(note)                

        if flagged_notes:
            list_ids.add(game.app_id)
            count += len(flagged_notes)
            
            flagged_game = GameData(game.app_id, game.count, flagged_notes)
            handler.export_file(flagged_game, filename)

        logs_dir = Path(output_path) / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)  

        # Export app IDs
        with open(logs_dir / "flagged_app_ids.txt", "w", encoding="utf-8") as f:
            for app_id in sorted(list_ids):
                f.write(app_id + "\n")

        # Export total flagged note count
        with open(logs_dir / "total_flagged_notes.txt", "w", encoding="utf-8") as f:
            f.write(f"{count}\n")

if __name__ == "__main__":
    # define input and output directory to FileHandler
    input_path = "filtered_patches"
    output_path = "flagged_patches"
    
    main(input_path, output_path)
