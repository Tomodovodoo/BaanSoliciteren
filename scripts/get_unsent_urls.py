import os
import json

SOLICITATIES_DIR = r"u:\Personal\BaanSoliciteren\Solicitaties"

def get_unsent_jobs():
    unsent_jobs = []
    
    if not os.path.exists(SOLICITATIES_DIR):
        print(f"Directory not found: {SOLICITATIES_DIR}")
        return

    for item in os.listdir(SOLICITATIES_DIR):
        job_dir = os.path.join(SOLICITATIES_DIR, item)
        
        # Skip archives and non-directories
        if not os.path.isdir(job_dir):
            continue
        if item.startswith("1.Archief") or item.startswith("1. Archief"):
            continue
            
        stats_path = os.path.join(job_dir, "stats.json")
        info_path = os.path.join(job_dir, "relevant_info.json")
        
        if not os.path.exists(stats_path):
            continue
            
        try:
            with open(stats_path, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            if stats.get("Response") == "Unsent":
                link = None
                if os.path.exists(info_path):
                    with open(info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        link = info.get("Link")
                
                unsent_jobs.append({
                    "folder": item,
                    "link": link
                })
        except Exception as e:
            print(f"Error processing {item}: {e}")

    print(json.dumps(unsent_jobs, indent=2))

if __name__ == "__main__":
    get_unsent_jobs()
