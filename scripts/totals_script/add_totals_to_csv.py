import csv
from pathlib import Path
import json

# Create a mapping of appId to total count from JSON files in the specified path
def get_totals(path):
    id_to_total = {}    
    for filename in Path(path).iterdir():
         if filename.is_file():
             try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    id_to_total[data.get('appId')] = (data.get('count'))
                    print(data.get('count'))
             except Exception as e:
                print(f"Error reading {filename.name}: {e}")    
         else:
            print(f"{filename.name} is not a file") 
    
    print(f"Total IDs processed: {sum(id_to_total.values())}")
    return id_to_total

# Add totals to the CSV file based on the mapping
def add_totals_csv(path, id_to_total):
    
    reader = csv.reader(open(path,"r", encoding="utf-8", newline=""))
    writer = csv.writer(open('data.csv', "w", encoding="utf-8", newline=""))

    header = next(reader)
    writer.writerow(header)

    for row in reader:
        if row:
            app_id = str(row[1]).strip()
            total = id_to_total.get(app_id)
            row.append(total)
            writer.writerow(row)
        else:
            continue

if __name__ == "__main__":
    add_totals_csv('games_metadata_totals.csv', get_totals('filtered_patches'))