import json
from datetime import datetime
    
def create_json_files(news_items, appid):
    if news_items is not None:
        patch_notes = []
        count = 0
        
        for item in news_items:
            count += 1
            title = item.get("title", "[NO TITLE]")
            content = item.get("contents", "[NO CONTENT]")
            patch_notes.append({
                    "title": title,
                    "date": datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "url": item.get("url", ""),
                    "content": content
                })
            
        data = {
            "appId": appid,
            "count": count,
            "notes": patch_notes
        }
        count = 0

        # patch notes are stored in patches folder
        with open(f"patches/{str(appid)}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"{appid} - JSON file created.")

            
