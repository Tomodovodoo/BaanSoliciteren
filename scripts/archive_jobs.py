"""Move jobs with Rejected or Expired status to Archive."""
import json
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR.parent / "Solicitaties").exists() else SCRIPT_DIR

SOLICITATIES_DIR = PROJECT_ROOT / "Solicitaties"
ARCHIVE_DIR = SOLICITATIES_DIR / "1.Archief"
ARCHIVE_STATES = {"Rejected", "Expired"}

def archive_jobs():
    """Move jobs with Rejected or Expired status to Archive folder."""
    if not SOLICITATIES_DIR.exists():
        print("No Solicitaties directory found.")
        return
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    job_folders = [
        f for f in SOLICITATIES_DIR.iterdir() 
        if f.is_dir() and f.name != "Archief"
    ]
    
    print(f"Checking {len(job_folders)} jobs for archiving...\n")
    
    archived, skipped, errors = 0, 0, 0
    
    for job_folder in job_folders:
        stats_file = job_folder / "stats.json"
        
        if not stats_file.exists():
            skipped += 1
            continue
        
        job_name = job_folder.name
        
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except Exception as e:
            print(f"  ✗ {job_name}: Error reading stats - {e}")
            errors += 1
            continue
        
        response = stats.get('Response', '')
        
        if response in ARCHIVE_STATES:
            archive_dest = ARCHIVE_DIR / job_name
            
            if archive_dest.exists():
                print(f"  ⚠ {job_name}: Already exists in archive, skipping")
                skipped += 1
                continue
            
            try:
                shutil.move(str(job_folder), str(archive_dest))
                print(f"  ✓ Archived: {job_name}")
                print(f"    Status: {response}")
                print(f"    Next Action: {stats.get('NextAction', 'N/A')[:60]}")
                print()
                archived += 1
            except Exception as e:
                print(f"  ✗ {job_name}: Error moving to archive - {e}")
                errors += 1
    
    print(f"\n{'='*60}")
    print(f"✓ Archiving Complete!")
    print(f"  Archived: {archived}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print(f"\nArchive location: {ARCHIVE_DIR.absolute()}")

if __name__ == "__main__":
    try:
        archive_jobs()
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
