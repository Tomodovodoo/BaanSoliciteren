"""
Generate deadlines.txt from ongoing job applications in Solicitaties/
"""
import json
import os
from pathlib import Path

def get_ongoing_deadlines():
    """Extract deadlines from ongoing job applications."""
    base_path = Path(__file__).parent / "Solicitaties"
    
    # Response values that indicate rejection or non-ongoing status
    NOT_ONGOING = {"Rejected"}
    
    deadlines = []
    
    # Iterate through all job folders
    for job_folder in base_path.iterdir():
        if not job_folder.is_dir() or job_folder.name == "1.Archief":
            continue
        
        stats_file = job_folder / "stats.json"
        relevant_info_file = job_folder / "relevant_info.json"
        
        if not stats_file.exists() or not relevant_info_file.exists():
            continue
        
        # Load stats to check if ongoing
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        # Load relevant_info to get deadline
        with open(relevant_info_file, 'r', encoding='utf-8') as f:
            relevant_info = json.load(f)
        
        response = stats.get("Response", "Unknown")
        rejected = stats.get("Rejected", False)
        deadline = relevant_info.get("Deadline", None)
        
        # Only include ongoing jobs with actual deadlines
        if not rejected and response not in NOT_ONGOING and deadline and deadline not in [None, "", "null", "Rolling / None"]:
            deadlines.append({
                "job": job_folder.name,
                "response": response,
                "deadline": deadline
            })
    
    # Sort by deadline (soonest first)
    deadlines.sort(key=lambda x: x["deadline"])
    
    return deadlines

def write_deadlines_file(deadlines):
    """Write deadlines to deadlines.txt."""
    output_path = Path(__file__).parent / "deadlines.txt"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("ONGOING JOB APPLICATION DEADLINES\n")
        f.write("=" * 80 + "\n\n")
        
        if not deadlines:
            f.write("No ongoing jobs with deadlines found.\n")
        else:
            for item in deadlines:
                f.write(f"Job:      {item['job']}\n")
                f.write(f"Response: {item['response']}\n")
                f.write(f"Deadline: {item['deadline']}\n")
                f.write("-" * 80 + "\n")
        
        f.write(f"\nTotal: {len(deadlines)} ongoing job(s) with deadlines\n")
    
    print(f"Created deadlines.txt with {len(deadlines)} ongoing job(s)")
    return output_path

if __name__ == "__main__":
    deadlines = get_ongoing_deadlines()
    output_path = write_deadlines_file(deadlines)
    print(f"Output written to: {output_path}")
