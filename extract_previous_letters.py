"""
Extract all previous cover letters from archived job applications.
Creates a JSON file mapping folder names to letter content.
"""
import json
import os
from pathlib import Path

def extract_previous_letters():
    """Extract all cover letters from the archive folder."""
    archive_path = Path(__file__).parent / "Solicitaties" / "1.Archief"
    
    letters = {}
    
    # Iterate through all archived job folders
    for job_folder in sorted(archive_path.iterdir()):
        if not job_folder.is_dir():
            continue
        
        # Look for Motivatie.txt
        motivatie_file = job_folder / "Motivatie.txt"
        
        if motivatie_file.exists():
            # Read the letter content
            with open(motivatie_file, 'r', encoding='utf-8') as f:
                letter_content = f.read()
            
            # Store with folder name as key
            letters[job_folder.name] = letter_content
            print(f"✓ Found letter: {job_folder.name}")
        else:
            print(f"✗ No letter found: {job_folder.name}")
    
    return letters

def write_letters_json(letters):
    """Write letters to JSON file."""
    output_path = Path(__file__).parent / "Vorige solicitatie brieven.json"
    
    # Create JSON with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(letters, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Created '{output_path.name}' with {len(letters)} letters")
    return output_path

if __name__ == "__main__":
    print("Extracting previous cover letters from archive...\n")
    letters = extract_previous_letters()
    output_path = write_letters_json(letters)
    print(f"✓ Output written to: {output_path}")
