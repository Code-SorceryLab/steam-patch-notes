import sys
from pathlib import Path
from logger import Tee

# ---- stdout tee logging -------------
log_file = Path("temp/logs/seq_llm_filter.log")
log_file.parent.mkdir(parents=True, exist_ok=True)
sys.stdout = Tee(sys.stdout, log_file.open("w", encoding="utf-8"))
# -------------------------------------

from file_handler import FileHandler
from game_data import GameData, PatchNote
from gpt_api import call_llm
from prompts import get_system_prompt, build_prompt

NOTE_COUNTER = 0

def is_patch_note(title: str, content: str) -> bool:
    system_prompt = get_system_prompt()
    user_prompt = build_prompt(title, content)
    tags = call_llm(system_prompt, user_prompt)
    if tags != []:
        return True, tags
    return False, []

def main(input_path: str, output_path: str):
    handler = FileHandler(input_path, output_path)

    for game, filename in handler.import_files():
        print(f"Processing App ID: {game.app_id}")
        filtered_notes = []

        for note in game.notes:
            global NOTE_COUNTER
            NOTE_COUNTER += 1
            print(f"  Evaluating Note: {note.title}")
            is_filtered, tags = is_patch_note(note.title, note.content)
            if is_filtered:
                filtered_note = PatchNote(
                    title=note.title,
                    date=note.date,
                    url=note.url,
                    content=note.content,
                    tags=tags
                )
                filtered_notes.append(filtered_note)

        if filtered_notes:
            filtered_game = GameData(
                game.app_id,
                len(filtered_notes),
                filtered_notes,
            )
            print(game.app_id)
            handler.export_file(filtered_game, filename)
        NOTE_COUNTER += len(game.notes)

if __name__ == "__main__":
    import sys
    import time

    # Define the paths for filtered notes by regex and to save the LLM filtered notes
    filtered_notes_path = "..."
    llm_filtered_path = "..."

    start_time = time.perf_counter()
    main(filtered_notes_path, llm_filtered_path)
    end_time = time.perf_counter()
    print(f"Execution time: {end_time - start_time:.2f} seconds for {NOTE_COUNTER} notes.")
