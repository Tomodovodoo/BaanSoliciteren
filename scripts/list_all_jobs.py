"""List all jobs (active and archived) to JSON file."""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR.parent / "Solicitaties").exists() else SCRIPT_DIR
SOLICITATIES_DIR = PROJECT_ROOT / "Solicitaties"
ARCHIVE_DIR = SOLICITATIES_DIR / "Archief"
OUTPUT_FILE = PROJECT_ROOT / "all_jobs_list.json"

def extract_job_info(folder_path):
    """Extract job info from folder name and relevant_info.json."""
    folder_name = folder_path.name
    
    parts = folder_name.split("_—_")
    if len(parts) == 2:
        role = parts[0].replace("_", " ")
        company = parts[1].replace("_", " ")
    else:
        role = folder_name.replace("_", " ")
        company = "Unknown"
    
    info_file = folder_path / "relevant_info.json"
    link = None
    if info_file.exists():
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                link = info.get("Link")
        except:
            pass
    
    return {
        "folder_name": folder_name,
        "role": role,
        "company": company,
        "application_link": link,
        "location": "Active" if not str(folder_path).startswith(str(ARCHIVE_DIR)) else "Archived"
    }

def main():
    jobs = []
    
    for folder in SOLICITATIES_DIR.iterdir():
        if folder.is_dir() and folder.name != "Archief":
            jobs.append(extract_job_info(folder))
    
    if ARCHIVE_DIR.exists():
        for folder in ARCHIVE_DIR.iterdir():
            if folder.is_dir():
                jobs.append(extract_job_info(folder))
    
    jobs.sort(key=lambda x: (x["location"], x["role"]))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"jobs": jobs, "total_count": len(jobs)}, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {OUTPUT_FILE}")
    print(f"  Total jobs: {len(jobs)}")
    print(f"  Active: {sum(1 for j in jobs if j['location'] == 'Active')}")
    print(f"  Archived: {sum(1 for j in jobs if j['location'] == 'Archived')}")

if __name__ == "__main__":
    main()
