import json
from pathlib import Path

def sum_total_notes(folder):
    folder_path = Path(folder)  
    total = 0

    for file in folder_path.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            total += data.get("total_notes", 0)
        except Exception as e:
            print(f"Skipping {file.name}: {e}")

    print(f"Total notes across all files: {total}")

# Specify the path to the folder 
sum_total_notes("patches_filtered")  
