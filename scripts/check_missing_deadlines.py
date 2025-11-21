"""Check which active jobs are missing deadlines."""
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOLICITATIES_DIR = PROJECT_ROOT / "Solicitaties"

active_jobs = []
missing_deadlines = []

for job_folder in sorted(SOLICITATIES_DIR.iterdir()):
    if not job_folder.is_dir() or job_folder.name == "Archief":
        continue
    
    rel_info_file = job_folder / "relevant_info.json"
    if not rel_info_file.exists():
        continue
    
    try:
        data = json.loads(rel_info_file.read_text(encoding="utf-8"))
        deadline = data.get("Deadline")
        
        active_jobs.append(job_folder.name)
        
        if not deadline or deadline == "" or deadline is None:
            missing_deadlines.append({
                "folder": job_folder.name,
                "link": data.get("Link", "N/A")
            })
    except Exception as e:
        print(f"Error reading {job_folder.name}: {e}")

print(f"Total active jobs: {len(active_jobs)}")
print(f"Jobs with missing deadlines: {len(missing_deadlines)}\n")

if missing_deadlines:
    print("=" * 80)
    print("ACTIVE JOBS MISSING DEADLINES:")
    print("=" * 80)
    for job in missing_deadlines:
        print(f"\n{job['folder']}")
        print(f"  Link: {job['link']}")
