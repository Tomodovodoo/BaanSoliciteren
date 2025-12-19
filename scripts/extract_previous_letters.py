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
    """Extract cover letters from all job folders in active and archived paths."""
    project_root = Path(__file__).parent.parent
    active_path = project_root / "Solicitaties"
    archive_path = active_path / "1.Archief"
    output_path = project_root / "data" / "Vorige solicitatie brieven.json"
    
    # Load existing data to append/update
    letters = load_existing_letters(output_path)
    initial_count = len(letters)
    
    print(f"Loaded {initial_count} existing letters from {output_path.name}")
    
    # Paths to scan (active and archive)
    scan_paths = [active_path, archive_path]
    
    for base_path in scan_paths:
        if not base_path.exists():
            print(f"⚠ Directory not found: {base_path}")
            continue
            
        print(f"Scanning directory: {base_path.relative_to(project_root)}")
            
        for job_folder in sorted(base_path.iterdir()):
            # Skip non-directories and the 1.Archief folder itself when scanning Solicitaties
            if not job_folder.is_dir() or job_folder.name == "1.Archief":
                continue
                
            # Check for Motivatie.txt
            motivatie_file = job_folder / "Motivatie.txt"
            
            if not motivatie_file.exists():
                continue

            # Read the letter content
            try:
                with open(motivatie_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    continue
                    
                # Add or update letter
                if job_folder.name not in letters:
                    print(f"  ✓ Added: {job_folder.name}")
                
                letters[job_folder.name] = content
            except Exception as e:
                print(f"  ⚠ Error reading {job_folder.name}: {e}")

    return letters, output_path

def write_letters_json(letters, output_path):
    """Write updated letters to JSON file."""
    # Create directory if missing
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(letters, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Updated '{output_path.name}' with total {len(letters)} letters")

def main():
    print("Gathering all cover letters (Motivatie.txt) from active and archived jobs...\n")
    letters, output_path = extract_previous_letters()
    write_letters_json(letters, output_path)

if __name__ == "__main__":
    main()
