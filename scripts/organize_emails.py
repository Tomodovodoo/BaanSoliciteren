"""Organize emails from Processing into job-specific folders."""
import json
import re
from pathlib import Path
import shutil

SCRIPT_DIR = Path(__file__).parent
PROCESSING_DIR = SCRIPT_DIR.parent / "Email" / "Processing"
ONGOING_DIR = SCRIPT_DIR.parent / "Email" / "Ongoing"
ARCHIVE_DIR = SCRIPT_DIR.parent / "Email" / "Archive"
SOLICITATIES_DIR = SCRIPT_DIR.parent / "Solicitaties"
UNRELATED_SENDERS_FILE = PROCESSING_DIR / "unrelated_email_senders.json"
REJECTED_COMPANIES_FILE = PROCESSING_DIR / "rejected_companies.json"

def load_json_file(file_path):
    """Load JSON file or return empty list if doesn't exist."""
    if not file_path.exists():
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path, data):
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_sender_domain(email_from):
    """Extract domain from email sender."""
    # Extract email from "Name <email@domain.com>" format
    match = re.search(r'<([^>]+)>', email_from)
    if match:
        email = match.group(1)
    else:
        email = email_from
    
    # Extract domain
    if '@' in email:
        return email.split('@')[-1].lower()
    return None

def get_active_job_folders():
    """Get list of active (non-archived) job folders."""
    active_jobs = []
    
    if not SOLICITATIES_DIR.exists():
        return active_jobs
    
    for folder in SOLICITATIES_DIR.iterdir():
        if folder.is_dir() and folder.name != "1.Archief":
            active_jobs.append(folder.name)
    
    return active_jobs

def is_job_archived(job_folder_name):
    """Check if a job folder exists in the archive."""
    archive_path = SOLICITATIES_DIR / "1.Archief" / job_folder_name
    return archive_path.exists()

def parse_job_folder_name(folder_name):
    """Parse job folder name to extract job title and company."""
    # Format: JobTitle_—_Company
    parts = folder_name.split('_—_')
    if len(parts) == 2:
        job_title = parts[0].replace('_', ' ').lower()
        company = parts[1].replace('_', ' ').lower()
        return job_title, company
    return None, None

def calculate_match_score(folder_name, sender_email, subject, body):
    """Calculate how well an email matches a job folder."""
    job_title, company = parse_job_folder_name(folder_name)
    if not job_title or not company:
        return 0
    
    score = 0
    sender_domain = extract_sender_domain(sender_email)
    subject_lower = (subject or '').lower()
    body_lower = (body or '').lower()[:500]  # Check first 500 chars of body
    
    # Check if sender domain matches company
    if sender_domain:
        company_parts = company.split()
        for part in company_parts:
            if len(part) > 3 and part in sender_domain:
                score += 50  # Strong match on sender domain
    
    # Check for company name in subject/body
    company_keywords = company.split()
    for keyword in company_keywords:
        if len(keyword) > 2:  # Skip very short words
            if keyword in subject_lower:
                score += 20
            if keyword in body_lower:
                score += 10
    
    # Check for job title keywords in subject/body
    job_keywords = job_title.split()
    for keyword in job_keywords:
        if len(keyword) > 2:  # Skip very short words like "2a"
            if keyword in subject_lower:
                score += 15
            if keyword in body_lower:
                score += 5
    
    # Special handling for specific identifiers (like vacancy numbers)
    # Extract potential vacancy numbers from folder name
    vacancy_matches = re.findall(r'\d{5,}', folder_name)
    for vacancy in vacancy_matches:
        if vacancy in subject_lower or vacancy in body_lower:
            score += 100  # Very strong match on vacancy number
    
    return score

def get_job_folder(company, subject, email_from, body=""):
    """Determine the correct job folder based on email content."""
    # Get active job folders
    active_jobs = get_active_job_folders()
    
    if not active_jobs:
        return None
    
    # If company is specified, filter to matching companies first
    if company and company != "DISCARD":
        company_lower = company.lower()
        matching_jobs = []
        
        for folder in active_jobs:
            _, folder_company = parse_job_folder_name(folder)
            if folder_company and company_lower in folder_company:
                matching_jobs.append(folder)
        
        # If we have company matches, use those; otherwise use all active jobs
        candidate_jobs = matching_jobs if matching_jobs else active_jobs
    else:
        candidate_jobs = active_jobs
    
    # Score each candidate job
    best_match = None
    best_score = 0
    
    for folder in candidate_jobs:
        score = calculate_match_score(folder, email_from, subject, body)
        if score > best_score:
            best_score = score
            best_match = folder
    
    # Only return a match if we have reasonable confidence (score > 10)
    if best_score > 10:
        return best_match
    
    # Fallback: if company specified, return first matching folder
    if company and company != "DISCARD" and candidate_jobs:
        return candidate_jobs[0]
    
    return None

def organize_emails():
    """Process emails in Processing folder and organize into job-specific folders."""
    if not PROCESSING_DIR.exists():
        print("No Processing directory found.")
        return
    
    unrelated_senders = load_json_file(UNRELATED_SENDERS_FILE)
    rejected_companies = load_json_file(REJECTED_COMPANIES_FILE)
    
    ONGOING_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    email_files = list(PROCESSING_DIR.glob("*.json"))
    email_files = [f for f in email_files if f.name not in ['unrelated_email_senders.json', 'rejected_companies.json']]
    
    print(f"Processing {len(email_files)} emails...\n")
    
    discarded, archived, moved_ongoing, skipped = 0, 0, 0, 0
    
    for email_file in email_files:
        try:
            with open(email_file, 'r', encoding='utf-8-sig') as f:
                email_data = json.load(f)
            
            company = email_data.get('company')
            response = email_data.get('response')
            email_from = email_data.get('from', '')
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            if company is None and response is None:
                skipped += 1
                continue
            
            if company == "DISCARD":
                sender_email = email_from.split('<')[-1].split('>')[0] if '<' in email_from else email_from
                if sender_email and sender_email not in unrelated_senders:
                    unrelated_senders.append(sender_email)
                
                email_file.unlink()
                discarded += 1
                print(f"  ✓ Discarded: {subject[:50]}")
                continue
            
            job_folder = get_job_folder(company, subject, email_from, body)
            
            if not job_folder:
                print(f"  ⚠ {email_file.name}: Unknown company '{company}', skipping")
                skipped += 1
                continue
            
            # Check if job is archived - if so, always route to Archive
            job_is_archived = is_job_archived(job_folder)
            
            if response in ["Rejected", "Expired"] or job_is_archived:
                dest_base = ARCHIVE_DIR
                dest_folder = dest_base / job_folder
                dest_file = dest_folder / email_file.name
                
                if company and company not in rejected_companies:
                    rejected_companies.append(company)
                
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.move(str(email_file), str(dest_file))
                archived += 1
                
                if job_is_archived:
                    print(f"  ✓ Archived (Job Archived): {job_folder}")
                else:
                    print(f"  ✓ Archived ({response}): {job_folder}")
                print(f"    {subject[:60]}\n")
            else:
                dest_base = ONGOING_DIR
                dest_folder = dest_base / job_folder
                dest_file = dest_folder / email_file.name
                
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.move(str(email_file), str(dest_file))
                moved_ongoing += 1
                print(f"  ✓ Ongoing: {job_folder} ({response or 'No response'})")
                print(f"    {subject[:60]}\n")
            
        except Exception as e:
            print(f"  ✗ Error processing {email_file.name}: {e}\n")
            continue
    
    save_json_file(UNRELATED_SENDERS_FILE, unrelated_senders)
    save_json_file(REJECTED_COMPANIES_FILE, rejected_companies)
    
    print(f"✓ Complete!")
    print(f"  Discarded: {discarded}")
    print(f"  Archived: {archived}")
    print(f"  Moved to Ongoing: {moved_ongoing}")
    print(f"  Skipped (unassigned): {skipped}")
    print(f"\n  Tracking {len(unrelated_senders)} unrelated senders")
    print(f"  Tracking {len(rejected_companies)} rejected companies")

if __name__ == "__main__":
    try:
        organize_emails()
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
