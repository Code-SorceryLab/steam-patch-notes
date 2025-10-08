import time
import certifi
import random
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path
from create_json_files import create_json_files
from load_batches import load_batches
from load_batches import delete_files
from session import SESSION

# Fetching from Steam Api
def fetch_patchnotes(appid, limit):
    
    time.sleep(random.uniform(0.05, 0.2))
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    params = {"appid": appid, "count": limit} 
    
    # headers to mimic browser
    header={
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                       "Chrome/124.0.0.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    # SESSION is custom request
    resp = SESSION.get(url, params=params, headers=header, timeout=15, verify=certifi.where())
    
    # if appid causes 403  
    if resp.status_code == 403:
        print(f"App {appid} returned 403 — skipping.")
        
        # logging skipped appids
        with open("logs/skipped_files.txt", "a", encoding="utf-8") as f:
                f.write(appid +" Skipped at 403 "+"\n")
        return None
    
    resp.raise_for_status()
    data = resp.json()

    # get items from response
    items = data.get("appnews", {}).get("newsitems", [])
    
    return items

def main():
    steam_max_limit = 99999999999
    #loading batches of appids
    batch = load_batches("raw_metadata_dataset",40)

    for appid_lists, filenames in batch:
        processed_files = []
        for appid, fname in zip(appid_lists, filenames):
            news = fetch_patchnotes(appid,steam_max_limit)
            create_json_files(news, appid)
            processed_files.append(fname)

        delete_files(processed_files)
        print("==="*40)
        print("PAUSED")
        print("==="*40)
        time.sleep(10)

    # debugging
    # for n in notes:
    #     print("="*80)
    #     print(f"\n{n['title']}")
    #     print(f"({n['date']})")
    #     print(f"URL: {n['url']}")
    #     print(f"Notes:\n{n['notes']}\n")
    #     print("="*80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error occurred:", e)
