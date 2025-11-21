"""Organize emails from Processing into job-specific folders."""
import json
from pathlib import Path
import shutil

PROCESSING_DIR = Path("Email/Processing")
ONGOING_DIR = Path("Email/Ongoing")
ARCHIVE_DIR = Path("Email/Archive")
SOLICITATIES_DIR = Path("Solicitaties")
UNRELATED_SENDERS_FILE = PROCESSING_DIR / "unrelated_email_senders.json"
REJECTED_COMPANIES_FILE = PROCESSING_DIR / "rejected_companies.json"

# Mapping from company field to Solicitaties folder name
COMPANY_TO_FOLDER = {
    "UMCG": ["Analist_Genoomdiagnostiek_—_UMCG", "Analist_HLO_kwaliteitszorg_—_UMCG", "Statistisch_Biologist_—_UMCG"],
    "DUO": ["Junior_Test_Engineer_—_DUO", "Kwaliteit_en_Servicemanagement_—_Duo"],
    "Specialist_Datatactiek_Team_Opsporing_—_Politie": ["Specialist_Datatactiek_Team_Opsporing_—_Politie"],
    "Data_Scientist_Team_Cybercrime_—_Politie": ["Data_Scientist_Team_Cybercrime_—_Politie"],
    "DataNorth": ["AI_Consultant_—_DataNorth"],
    "Ilionx": ["AI_ML_Engineer_—_Ilionx"],
    "Sopra Steria": ["Data_Scientist_—_Sopra_Steria", "Data_Engineer_—_Sopra_Steria"],
    "Teijin Aramid": ["Chemisch_Analist_—_Teijin_Aramid"],
}

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

def get_job_folder(company, subject):
    """Determine the correct job folder based on company and subject."""
    if company not in COMPANY_TO_FOLDER:
        return None
    
    folders = COMPANY_TO_FOLDER[company]
    
    if len(folders) == 1:
        return folders[0]
    
    if company == "UMCG":
        subject_lower = subject.lower()
        if "genoom" in subject_lower:
            return "Analist_Genoomdiagnostiek_—_UMCG"
        elif "kwaliteit" in subject_lower or "hlo" in subject_lower:
            return "Analist_HLO_kwaliteitszorg_—_UMCG"
        elif "statist" in subject_lower or "biolog" in subject_lower:
            return "Statistisch_Biologist_—_UMCG"
        else:
            return folders[0]
    
    if company == "DUO":
        subject_lower = subject.lower()
        if "test engineer" in subject_lower or "junior" in subject_lower:
            return "Junior_Test_Engineer_—_DUO"
        elif "kwaliteit" in subject_lower or "service" in subject_lower:
            return "Kwaliteit_en_Servicemanagement_—_Duo"
        else:
            return folders[0]
    
    if company == "Sopra Steria":
        subject_lower = subject.lower()
        if "scientist" in subject_lower:
            return "Data_Scientist_—_Sopra_Steria"
        elif "engineer" in subject_lower:
            return "Data_Engineer_—_Sopra_Steria"
        else:
            return folders[0]
    
    return folders[0]

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
            with open(email_file, 'r', encoding='utf-8') as f:
                email_data = json.load(f)
            
            company = email_data.get('company')
            response = email_data.get('response')
            email_from = email_data.get('from', '')
            subject = email_data.get('subject', '')
            
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
            
            job_folder = get_job_folder(company, subject)
            
            if not job_folder:
                print(f"  ⚠ {email_file.name}: Unknown company '{company}', skipping")
                skipped += 1
                continue
            
            if response in ["Rejected", "Expired"]:
                dest_base = ARCHIVE_DIR
                dest_folder = dest_base / job_folder
                dest_file = dest_folder / email_file.name
                
                if company and company not in rejected_companies:
                    rejected_companies.append(company)
                
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.move(str(email_file), str(dest_file))
                archived += 1
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
