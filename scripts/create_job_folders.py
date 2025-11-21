"""Parse overview JSON files and create individual job folders with proper naming convention."""
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR.parent / "Solicitaties").exists() else SCRIPT_DIR
SOLICITATIES_DIR = PROJECT_ROOT / "Solicitaties"
OVERVIEW_DIR = PROJECT_ROOT / "Overviews"  # Folder containing overview JSON files

def sanitize_folder_name(text):
    """Convert text to valid folder name format."""
    # Replace spaces with underscores
    text = text.strip().replace(" ", "_")
    # Remove invalid characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    return text

def create_job_folder(job_data, overview_file):
    """Create a job folder from overview JSON data."""
    try:
        job_title = job_data.get("job", "Unknown_Job")
        company = job_data.get("company", "Unknown_Company")
        
        # Create folder name: Job_—_Company
        folder_name = f"{sanitize_folder_name(job_title)}_—_{sanitize_folder_name(company)}"
        job_folder = SOLICITATIES_DIR / folder_name
        
        # Skip if folder already exists
        if job_folder.exists():
            print(f"  ⚠ Skipping: {folder_name} (already exists)")
            return False
        
        # Create folder
        job_folder.mkdir(parents=True, exist_ok=True)
        
        # Create relevant_info.json
        relevant_info = {
            "Location": job_data.get("location", ""),
            "Deadline": job_data.get("deadline", ""),
            "Notes": job_data.get("notes", ""),
            "Link": job_data.get("link", ""),
            "Salary": job_data.get("salary", ""),
            "Fit": job_data.get("fit", ""),
            "Preference": job_data.get("preference", ""),
            "ContactNaam": job_data.get("contact_name", ""),
            "ContactPhone": job_data.get("contact_phone", ""),
            "ContactJob": job_data.get("contact_job", "")
        }
        
        with open(job_folder / "relevant_info.json", 'w', encoding='utf-8') as f:
            json.dump(relevant_info, f, indent=2, ensure_ascii=False)
        
        # Create stats.json
        stats = {
            "PotentialSatisfaction": None,
            "NextAction": job_data.get("next_action", "Research and apply"),
            "Response": "Unsent",
            "Rejected": False,
            "Interviewed": False,
            "Hired": False
        }
        
        with open(job_folder / "stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Created: {folder_name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error creating folder for {job_data.get('job', 'Unknown')}: {e}")
        return False

def process_overview_file(overview_path):
    """Process a single overview JSON file."""
    print(f"\nProcessing: {overview_path.name}")
    
    try:
        with open(overview_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = data.get("jobs", [])
        print(f"  Found {len(jobs)} jobs")
        
        created = 0
        for job in jobs:
            if create_job_folder(job, overview_path):
                created += 1
        
        print(f"  Created {created} new folders")
        return created
        
    except Exception as e:
        print(f"  ✗ Error processing {overview_path.name}: {e}")
        return 0

def main():
    """Process all overview JSON files and create job folders."""
    print("Creating job folders from overview JSON files...\n")
    
    if not OVERVIEW_DIR.exists():
        print(f"Overview directory not found: {OVERVIEW_DIR}")
        print("Please create the 'Overviews' folder and add your overview JSON files.")
        return
    
    SOLICITATIES_DIR.mkdir(parents=True, exist_ok=True)
    
    overview_files = list(OVERVIEW_DIR.glob("*.json"))
    
    if not overview_files:
        print(f"No JSON files found in {OVERVIEW_DIR}")
        return
    
    total_created = 0
    for overview_file in overview_files:
        total_created += process_overview_file(overview_file)
    
    print(f"\n{'='*60}")
    print(f"✓ Complete! Created {total_created} new job folders")
    print(f"  Location: {SOLICITATIES_DIR.absolute()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
