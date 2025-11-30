"""Update stats.json files based on email responses and deadlines."""
import json
import shutil
import re
from pathlib import Path
from datetime import date

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

SOLICITATIES_DIR = PROJECT_ROOT / "Solicitaties"
ARCHIVE_DIR = PROJECT_ROOT / "Solicitaties" / "1.Archief"
EMAIL_ONGOING_DIR = PROJECT_ROOT / "Email" / "Ongoing"
EMAIL_ARCHIVE_DIR = PROJECT_ROOT / "Email" / "Archive"

# Response priority (lower number = higher priority)
RESPONSE_HIERARCHY = {
    "Hired": 1,
    "Offer": 2,
    "Interview Scheduled": 3,
    "Received": 4,
    "Pending": 5,
    "Called": 6,
    "Unsent": 7,
    "Rejected": 8,
    "Expired": 9,
    "Other": 10
}

def parse_deadline(s) -> date | None:
    """Parse date from string (YYYY-MM-DD or YYYY/MM/DD)."""
    if not s or str(s).strip().lower() in {"", "none", "null", "unknown", "onbekend"}:
        return None
    txt = re.sub(r"[./]", "-", str(s).strip())
    m = re.match(r"^\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*$", txt)
    if not m:
        return None
    y, mth, d = map(int, m.groups())
    try:
        return date(y, mth, d)
    except ValueError:
        return None

def get_highest_response(responses):
    """Determine highest priority response from list."""
    if not responses:
        return None
    
    valid_responses = [r for r in responses if r is not None]
    if not valid_responses:
        return None
    
    final_states = {"Rejected", "Expired", "Other", "Hired"}
    final_responses = [r for r in valid_responses if r in final_states]
    non_final_responses = [r for r in valid_responses if r not in final_states]
    
    if final_responses:
        return sorted(final_responses, key=lambda r: RESPONSE_HIERARCHY.get(r, 999))[0]
    
    return sorted(non_final_responses, key=lambda r: RESPONSE_HIERARCHY.get(r, 999))[0]

def should_update_response(current_response, new_response):
    """Check if new response should replace current."""
    if not current_response:
        return True
    
    final_states = {"Rejected", "Expired", "Other", "Hired"}
    
    current_priority = RESPONSE_HIERARCHY.get(current_response, 999)
    new_priority = RESPONSE_HIERARCHY.get(new_response, 999)
    
    if new_response in final_states and current_response not in final_states:
        return True
    
    if current_response in final_states and new_response not in final_states:
        return False
    
    return new_priority < current_priority

def move_emails_to_archive(job_name):
    """Move all emails from Ongoing to Archive."""
    ongoing_folder = EMAIL_ONGOING_DIR / job_name
    archive_folder = EMAIL_ARCHIVE_DIR / job_name
    
    if not ongoing_folder.exists():
        return 0
    
    archive_folder.mkdir(parents=True, exist_ok=True)
    
    email_files = list(ongoing_folder.glob("*.json"))
    moved_count = 0
    
    for email_file in email_files:
        dest_file = archive_folder / email_file.name
        try:
            shutil.move(str(email_file), str(dest_file))
            moved_count += 1
        except Exception as e:
            print(f"    Warning: Failed to move {email_file.name}: {e}")
    
    try:
        if ongoing_folder.exists() and not list(ongoing_folder.glob("*")):
            ongoing_folder.rmdir()
    except:
        pass
    
    return moved_count

def update_stats():
    """Update all stats.json files based on emails and deadlines."""
    if not SOLICITATIES_DIR.exists():
        print("No Solicitaties directory found.")
        return
    
    company_folders = []
    
    for f in SOLICITATIES_DIR.iterdir():
        if f.is_dir() and f.name != "Archief":
            company_folders.append(f)
    
    if ARCHIVE_DIR.exists():
        for f in ARCHIVE_DIR.iterdir():
            if f.is_dir():
                company_folders.append(f)
    
    active_count = len([f for f in company_folders if not str(f).startswith(str(ARCHIVE_DIR))])
    archived_count = len([f for f in company_folders if str(f).startswith(str(ARCHIVE_DIR))])
    
    print(f"Updating stats for {len(company_folders)} jobs ({active_count} active, {archived_count} archived)...\n")
    updated, archived, expired = 0, 0, 0
    
    current_date = date.today()
    
    for company_folder in company_folders:
        stats_file = company_folder / "stats.json"
        info_file = company_folder / "relevant_info.json"
        
        if not stats_file.exists():
            continue
        
        job_name = company_folder.name
        
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except Exception as e:
            print(f"  ✗ {job_name}: Error reading stats - {e}\n")
            continue
            
        deadline_date = None
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    deadline_date = parse_deadline(info.get("Deadline"))
            except Exception:
                pass

        # Check if expired
        current_response = stats.get('Response', 'Unknown')
        is_expired = False
        
        if current_response in ["Unsent", "Called"] and deadline_date:
            if deadline_date < current_date:
                is_expired = True

        # Handle manually rejected jobs
        if stats.get('Rejected', False):
            ongoing_folder = EMAIL_ONGOING_DIR / job_name
            if ongoing_folder.exists():
                moved = move_emails_to_archive(job_name)
                if moved > 0:
                    print(f"  ✓ {job_name}")
                    print(f"    Manually rejected - moved {moved} email(s) to Archive")
                    print()
                    archived += 1
        
        archive_folder = EMAIL_ARCHIVE_DIR / job_name
        is_archived = archive_folder.exists()
        
        # Collect all emails
        company_emails = []
        
        ongoing_folder = EMAIL_ONGOING_DIR / job_name
        if ongoing_folder.exists():
            for email_file in ongoing_folder.glob("*.json"):
                try:
                    with open(email_file, 'r', encoding='utf-8-sig') as f:
                        email_data = json.load(f)
                        company_emails.append(email_data)
                except Exception as e:
                    print(f"  Warning: Failed to read {email_file}: {e}")
        
        if archive_folder.exists():
            for email_file in archive_folder.glob("*.json"):
                try:
                    with open(email_file, 'r', encoding='utf-8-sig') as f:
                        email_data = json.load(f)
                        company_emails.append(email_data)
                except Exception as e:
                    print(f"  Warning: Failed to read {email_file}: {e}")
        
        highest_response = None
        
        if company_emails:
            responses = [email.get('response') for email in company_emails]
            highest_response = get_highest_response(responses)
        
        if is_archived:
            highest_response = "Rejected"
            
        if not highest_response and is_expired:
            highest_response = "Expired"
            
        if not highest_response:
            continue
        
        # Auto-archive if needed
        archive_worthy_states = {"Rejected", "Expired", "Other"}
        if highest_response in archive_worthy_states and not is_archived:
            ongoing_folder = EMAIL_ONGOING_DIR / job_name
            if ongoing_folder.exists() and list(ongoing_folder.glob("*.json")):
                moved = move_emails_to_archive(job_name)
                if moved > 0:
                    print(f"  ✓ {job_name}")
                    print(f"    Auto-archived {moved} email(s) (detected {highest_response} status)")
                    print()
                    archived += 1
                    is_archived = True
        
        # Update stats.json
        try:
            old_response = stats.get('Response', 'Unknown')
            
            if is_archived and old_response != "Rejected":
                stats['Response'] = highest_response
                stats['Rejected'] = True
                
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ {job_name}")
                print(f"    {old_response} → {highest_response}")
                print(f"    (Archived folder detected)")
                print()
                updated += 1
                continue
            
            allow_update = False
            if highest_response == "Expired" and old_response in ["Unsent", "Called"]:
                allow_update = True
            elif should_update_response(old_response, highest_response):
                allow_update = True
                
            if allow_update and old_response != highest_response:
                stats['Response'] = highest_response
                
                if highest_response == "Rejected":
                    stats['Rejected'] = True
                
                if highest_response == "Hired":
                    stats['Hired'] = True
                
                if highest_response in ["Interview Scheduled", "Offer", "Hired"]:
                    stats['Interviewed'] = True
                
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ {job_name}")
                print(f"    {old_response} → {highest_response}")
                if highest_response == "Expired":
                    print(f"    (Deadline {deadline_date} passed)")
                    expired += 1
                print()
                updated += 1
        
        except Exception as e:
            print(f"  ✗ {job_name}: Error updating stats - {e}\n")
    
    print(f"✓ Updated {updated} company stats.")
    if archived > 0:
        print(f"✓ Auto-archived emails for {archived} manually rejected applications.")
    if expired > 0:
        print(f"✓ Marked {expired} applications as Expired.")

if __name__ == "__main__":
    try:
        update_stats()
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
