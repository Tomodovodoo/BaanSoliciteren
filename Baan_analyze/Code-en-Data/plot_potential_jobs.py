import argparse
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()

    BASEPATH = Path(__file__).resolve().parent
    csv_path = Path(str(BASEPATH) + "/CalculatedJobPotential.csv")
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Colommen van de dataset
    title_col = "Job" if "Job" in df.columns else None
    company_col = "Company" if "Company" in df.columns else None
    sat_col = "PotentialSatisfaction" if "PotentialSatisfaction" in df.columns else None

    if not title_col or not sat_col:
        raise SystemExit("Required columns not found. Need at least 'Job' (or your title col) and 'PotentialSatisfaction'.")

    df_plot = df[[title_col, sat_col] + ([company_col] if company_col else [])].copy()
    df_plot = df_plot.dropna(subset=[sat_col])
    df_plot[sat_col] = pd.to_numeric(df_plot[sat_col], errors="coerce")
    df_plot = df_plot.dropna(subset=[sat_col])

    # Labels
    if company_col:
        df_plot["Label"] = df_plot.apply(
            lambda r: f"{str(r[title_col]).strip()} — {str(r[company_col]).strip()}" if pd.notna(r[company_col]) and str(r[company_col]).strip() != "" else str(r[title_col]).strip(),
            axis=1
        )
    else:
        df_plot["Label"] = df_plot[title_col].astype(str)

    # Sorteren en limits
    df_plot = df_plot.sort_values(sat_col, ascending=False)
    if args.top and len(df_plot) > args.top:
        df_plot = df_plot.head(args.top)

    labels = df_plot["Label"].tolist()
    values = df_plot[sat_col].tolist()

    # Plot + Opslaan
    fig_width = max(10, min(28, 0.45 * len(labels) + 6))
    fig_height = 8

    plt.figure(figsize=(fig_width, fig_height))
    plt.bar(range(len(labels)), values)
    plt.xticks(range(len(labels)), labels, rotation=60, ha="right")
    plt.ylabel("PotentialSatisfaction")
    plt.title("Potential Jobs — PotentialSatisfaction (sorted high → low)")
    plt.tight_layout()

    for i, v in enumerate(values):
        try:
            v_val = float(v)
            plt.text(i, v_val, f"{v_val:.1f}", ha="center", va="bottom", fontsize=8)
        except Exception:
            pass

    # >>> Save to Baan_analyze
    save_dir = Path(__file__).resolve().parent.parent
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / "job_potential.png"
    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    print(f"Saved plot to: {save_path}")

if __name__ == "__main__":
    main()
