import json
from pathlib import Path

def load_batches(folder, batch_size):
    
    folder_path = Path(folder)
    batch = []
    
    # to track files for deletion
    fnames = []
    skipped_files = []

    for file in folder_path.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            appid = data.get("steam_appid")
            if appid is not None:
                batch.append(str(appid))
                fnames.append(file.name)
            else:
                skipped_files.append(file.name + " (appid not found)")
                print(f"Skipping {file.name}: 'appid' not found.")
        except Exception as e:
                skipped_files.append(file.name + f" ({e})")
                print(f"Skipping {file.name}: {e}")

        if len(batch) >= batch_size:
            yield batch, fnames
            batch = []
            fnames = []

            #debugging
            # print("\n"*10)
            
            print(f"{batch_size} Sent")

    # return leftovers
    if batch:
        yield batch, fnames

    # log skipped files
    if skipped_files:
        logs = Path("logs")
        logs.mkdir(parents=True, exist_ok=True)
        with open(logs / "skipped_files.txt", "a", encoding="utf-8") as f:
            for fname in skipped_files:
                f.write(fname + "\n")

# Delete processed files to track progress
def delete_files(filenames):
    
    folder_path = Path("appdetails_copy")
    for fname in filenames:
        try:
            file_path = folder_path / fname
            if file_path.exists():
                file_path.unlink()
                print(f"Deleted {fname}")
            else:
                print(f"File {fname} does not exist.")
        except Exception as e:
            print(f"Error deleting {fname}: {e}")

#debugging
# batches = load_batches(Path(__file__).resolve().parent.parent/"steamspy_dataset")

# for i, batch in enumerate(batches, 1):
#     print(f"Batch {i} (size {len(batch)}):")
#     print(batch)