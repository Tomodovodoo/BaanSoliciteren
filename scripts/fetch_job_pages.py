import os
import json
import requests
from bs4 import BeautifulSoup
import time

SOLICITATIES_DIR = r"u:\Personal\BaanSoliciteren\Solicitaties"
ARCHIVE_DIR = "1.Archief"

def fetch_and_save_webpage():
    print(f"Scanning directories in {SOLICITATIES_DIR}...")
    
    count = 0
    skipped = 0
    errors = 0

    for item in os.listdir(SOLICITATIES_DIR):
        item_path = os.path.join(SOLICITATIES_DIR, item)
        
        # Skip if not a directory
        if not os.path.isdir(item_path):
            continue
            
        # Skip Archive
        if item == ARCHIVE_DIR:
            print(f"Skipping Archive directory: {item}")
            continue
            
        relevant_info_path = os.path.join(item_path, "relevant_info.json")
        webpage_txt_path = os.path.join(item_path, "webpage.txt")
        
        if not os.path.exists(relevant_info_path):
            print(f"Skipping {item}: relevant_info.json not found")
            skipped += 1
            continue
            
        # Check if webpage.txt already exists
        if os.path.exists(webpage_txt_path):
             # Check if it's empty or very small, if so, maybe retry? 
             # For now, let's assume if it exists, we skip it to avoid re-fetching everything every time.
             # User said "create", usually implies if missing.
             # But user also said "For all Solicitaties that are unsent", implying a batch job.
             # Let's check size.
             if os.path.getsize(webpage_txt_path) > 100:
                 print(f"Skipping {item}: webpage.txt already exists")
                 skipped += 1
                 continue
        
        try:
            with open(relevant_info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            link = data.get("Link")
            if not link:
                print(f"Skipping {item}: No Link in relevant_info.json")
                skipped += 1
                continue
                
            print(f"Fetching {link} for {item}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(link, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            with open(webpage_txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Source: {link}\n\n")
                f.write(text)
                
            print(f"Successfully saved webpage.txt for {item}")
            count += 1
            
            # Be nice to servers
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {item}: {e}")
            errors += 1

    print(f"\nFinished. Processed: {count}, Skipped: {skipped}, Errors: {errors}")

if __name__ == "__main__":
    fetch_and_save_webpage()
