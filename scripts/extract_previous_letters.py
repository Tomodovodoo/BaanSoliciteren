"""
Extract all previous cover letters from archived job applications.
Updates 'data/Vorige solicitatie brieven.json' by appending/updating letters for rejected jobs.
"""
import json
import os
from pathlib import Path

def load_existing_letters(output_path):
    """Load existing letters from JSON file."""
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠ Warning: Could not decode {output_path.name}, starting fresh.")
                return {}
    return {}

def extract_previous_letters():
    """Extract cover letters from the archive folder, filtering for rejected jobs."""
    project_root = Path(__file__).parent.parent
    archive_path = project_root / "Solicitaties" / "1.Archief"
    output_path = project_root / "data" / "Vorige solicitatie brieven.json"
    
    # Load existing data to append/update instead of overwrite
    letters = load_existing_letters(output_path)
    initial_count = len(letters)
    
    print(f"Loaded {initial_count} existing letters.")
    
    # Iterate through all archived job folders
    if not archive_path.exists():
        print(f"Archive folder not found: {archive_path}")
        return letters

    for job_folder in sorted(archive_path.iterdir()):
        if not job_folder.is_dir():
            continue
            
        # Check for Motivatie.txt
        motivatie_file = job_folder / "Motivatie.txt"
        stats_file = job_folder / "stats.json"
        
        if not motivatie_file.exists():
            continue

        # Check status in stats.json
        is_rejected = False
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    # We want 'Rejected' jobs (implies sent)
                    # Exclude 'Expired', 'Unsent', etc.
                    if stats.get("Response") == "Rejected":
                        is_rejected = True
                    # Also include if explicitly marked as Rejected boolean?
                    elif stats.get("Rejected") is True:
                         is_rejected = True
            except Exception as e:
                print(f"  ⚠ Error reading stats for {job_folder.name}: {e}")
        
        if is_rejected:
            # Read the letter content
            with open(motivatie_file, 'r', encoding='utf-8') as f:
                letter_content = f.read()
            
            # Store/Update with folder name as key
            if job_folder.name not in letters:
                print(f"  ✓ Added: {job_folder.name}")
            else:
                # Optional: Check if content changed? For now just overwrite entry.
                pass 
            
            letters[job_folder.name] = letter_content
        else:
            # print(f"  ✗ Skipped (not rejected): {job_folder.name}")
            pass

    return letters, output_path

def write_letters_json(letters, output_path):
    """Write updated letters to JSON file."""
    # Create JSON with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(letters, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Updated '{output_path.name}' with {len(letters)} letters")

def main():
    print("Extracting previous cover letters for rejected jobs...\n")
    letters, output_path = extract_previous_letters()
    write_letters_json(letters, output_path)

if __name__ == "__main__":
    main()
