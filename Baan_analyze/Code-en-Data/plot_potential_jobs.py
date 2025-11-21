"""Plot PotentialSatisfaction for active jobs."""
import matplotlib.pyplot as plt
from pathlib import Path
import json

def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    sollicitaties = repo_root / "Solicitaties"
    
    if not sollicitaties.exists():
        raise SystemExit(f"Solicitaties folder not found at: {sollicitaties}")

    jobs = []

    for job_folder in sorted(sollicitaties.iterdir()):
        if not job_folder.is_dir() or job_folder.name == "Archief":
            continue

        stats_file = job_folder / "stats.json"
        if not stats_file.exists():
            continue

        try:
            data = json.loads(stats_file.read_text(encoding="utf-8"))
            potential = data.get("PotentialSatisfaction")
            
            if potential is not None:
                folder_name = job_folder.name
                if "—" in folder_name:
                    role, company = folder_name.split("—", 1)
                    label = f"{role.replace('_', ' ').strip()} — {company.replace('_', ' ').strip()}"
                else:
                    label = folder_name.replace("_", " ")
                
                jobs.append({"label": label, "potential": float(potential)})
        except Exception as e:
            print(f"Warning: Could not read {job_folder.name}: {e}")

    if not jobs:
        raise SystemExit("No jobs with PotentialSatisfaction found!")

    jobs.sort(key=lambda x: x["potential"], reverse=True)
    labels = [j["label"] for j in jobs]
    values = [j["potential"] for j in jobs]

    # Create plot
    fig_width = max(10, min(28, 0.45 * len(labels) + 6))
    fig_height = 8

    plt.figure(figsize=(fig_width, fig_height))
    plt.bar(range(len(labels)), values)
    plt.xticks(range(len(labels)), labels, rotation=60, ha="right")
    plt.ylabel("PotentialSatisfaction")
    plt.title(f"Active Job Potential — PotentialSatisfaction (sorted high → low, n={len(jobs)})")
    plt.tight_layout()

    for i, v in enumerate(values):
        plt.text(i, v, f"{v:.1f}", ha="center", va="bottom", fontsize=8)

    # Save
    save_dir = script_dir.parent
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / "job_potential.png"
    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    print(f"✓ Saved plot ({len(jobs)} active jobs) to: {save_path}")

if __name__ == "__main__":
    main()
