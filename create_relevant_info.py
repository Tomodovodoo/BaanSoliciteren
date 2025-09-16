# Created with future in mind, to add folders and other jobs automatically from csv, or redo with --force.

from __future__ import annotations
import argparse
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


# 1) CONFIG

CSV_REL_PATH = Path("Baan_analyze") / "Code-en-Data" / "JobTracker.csv"
SOLICITATIES_DIR = Path("Solicitaties")

# Column names in JobTracker.csv
COLS = {
    "job": "Job",
    "company": "Company",
    "loc": "Location",
    "deadline": "Deadline",
    "notes": "Notes",
    "link": "Link",
    "salary": "Salary",
    "fit": "Fit",
    "contact": "Contact",
    "contact_name": "ContactName",
    "contact_phone": "ContactPhone",
    "contact_job": "ContactJob",
    "next_action": "NextAction",
    "potential_sat": "PotentialSatisfaction",
}

# Static mapping: (job_contains, company_contains) -> folder name
MAPPING: Dict[Tuple[str, str], str] = {
    ("Adviseur Waterkwaliteit", "Wetterskip"): "Adviseur_Waterkwaliteit_—_Wetterskip",
    ("AI/ML Engineer", "Ilionx"): "AI_ML_Engineer_—_Ilionx",
    ("Analist Genoomdiagnostiek", "UMCG"): "Analist_Genoomdiagnostiek_—_UMCG",
    ("Analist HLO", "UMCG"): "Analist_HLO_kwaliteitszorg_—_UMCG",
    ("Chemisch Analist", "Teijin Aramid"): "Chemisch_Analist_—_Teijin_Aramid",
    ("Data Analyst", "Gomibo"): "Data_Analist_—_Gomibo",
    ("Data Analist", "Maandag"): "Data_Analist_—_Maandag",
    ("Data Analyst", "EasyToys"): "Data_Analyst_—_EasyToys",
    ("Data Engineer", "Springer Nature"): "Data_Engineer_—_Springer_Nature",
    ("Data Scientist", "Politie"): "Data_Scientist_Team_Cybercrime_—_Politie",
    ("Data Scientist", "Sopra Steria"): "Data_Scientist_—_Sopra_Steria",
    ("Functioneel Ontwerper", "RDW"): "Functioneel_Ontwerper_—_RDW",
    ("Junior Test Engineer", "DUO"): "Junior_Test_Engineer_—_DUO",
    ("Medewerker Kwaliteit- en Servicemanagement (ODC-Noord)", "DUO"): "Kwaliteit_en_Servicemanagement_—_Duo",
    ("Mastership Data Science", "House of Beta"): "Mastership_Data_Science_—_House_of_Beta",
    ("ML Engineer", "Springer Nature"): "ML_Engineer_—_Springer_Nature",
    ("Python Software Engineer", "CIMSOLUTIONS"): "Python_Software_Engineer_—_CIMSOLUTIONS",
    ("QA Engineer", "CropX"): "QA_Engineer_—_CropX",
    ("QA Engineer", "SciSure"): "QA_Engineer_—_SciSure",
    ("Specialist Datatactiek", "Politie"): "Specialist_Datatactiek_Team_Opsporing_—_Politie",
    ("Biolog", "UMCG"): "Statistisch_Biologist_—_UMCG",
    ("Young Professional Track (Cloud/Security); Data Analyst (offline)", "Sogeti"): "Young_Track_Data_Analyst_—_Sogeti",
}

# Company aliases that appear in CSV
COMPANY_ALIASES = {
    "Wetterskip": ["Wetterskip", "Wetterskip Fryslân"],
    "Gomibo": ["Gomibo", "Belsimpel"],
    "EasyToys": ["EasyToys", "EDC Retail"],
    "DUO": ["DUO", "Duo", "DUO (Rijksoverheid)"],
    "Politie": ["Politie", "Eenheid Noord", "Team Opsporing"],
}


# 2) LOGIC

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().casefold()

def contains_any(hay: str, needles: List[str]) -> bool:
    hay_n = norm(hay)
    return any(norm(n) in hay_n for n in needles)

def pick_best_match(
    candidates: pd.DataFrame,
    folder_stats: Optional[dict],
    cols: dict,
    folder_name: str,
) -> Optional[pd.Series]:
    """If multiple CSV rows match, use stats.json hints (PotentialSatisfaction/NextAction) to choose."""
    if candidates.empty:
        return None
    if len(candidates) == 1 or not folder_stats:
        return candidates.iloc[0]

    wanted_sat = folder_stats.get("PotentialSatisfaction", None)
    wanted_next = folder_stats.get("NextAction", None)
    best_idx = None
    best_score = -1.0

    for idx, row in candidates.iterrows():
        score = 0.0
        # NextAction similarity (exact-ish, casefold)
        if wanted_next and isinstance(row.get(cols["next_action"]), str):
            if norm(row[cols["next_action"]]) == norm(wanted_next):
                score += 2.0
        # PotentialSatisfaction closeness
        try:
            if wanted_sat is not None:
                row_sat = float(row.get(cols["potential_sat"]))
                if not math.isnan(row_sat):
                    diff = abs(float(wanted_sat) - row_sat)
                    score += max(0.0, 1.0 - min(diff, 1.0))  # 1.0 if equal, down to 0 if diff >= 1
        except Exception:
            pass

        if score > best_score:
            best_score = score
            best_idx = idx

    return candidates.loc[best_idx] if best_idx is not None else candidates.iloc[0]

def read_stats_json(folder: Path) -> Optional[dict]:
    stats_path = folder / "stats.json"
    if stats_path.exists():
        try:
            return json.loads(stats_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None

def row_matches(row: pd.Series, job_sub: str, company_sub: str) -> bool:
    job_ok = job_sub.lower() in str(row[COLS["job"]]).lower()
    # company may have aliases
    aliases = COMPANY_ALIASES.get(company_sub, [company_sub])
    comp_ok = any(a.lower() in str(row[COLS["company"]]).lower() for a in aliases)
    return job_ok and comp_ok

def to_relevant_info(row: pd.Series) -> dict:
    def val(col_key: str):
        col = COLS[col_key]
        v = row[col] if col in row else None
        # NaNs -> None / ""
        if pd.isna(v):
            return None if col_key in {"deadline", "link"} else ""
        return v

    # Fit can be numeric or string; leave as-is if numeric, else string
    fit_val = row.get(COLS["fit"], "")
    if pd.isna(fit_val):
        fit_out = ""
    else:
        try:
            fit_out = float(fit_val)
            # If it's an int like 7.0, keep as 7
            if fit_out.is_integer():
                fit_out = int(fit_out)
        except Exception:
            fit_out = str(fit_val)

    out = {
        "Locatie": val("loc") or "",
        "Deadline": val("deadline"),              # prefer "YYYY-MM-DD"
        "Notes": val("notes") or "",
        "Link": val("link"),
        "Salary": val("salary") or "",
        "Fit": fit_out,
        "Contact": val("contact") or "",
        "ContactNaam": row.get(COLS["contact_name"], "") if not pd.isna(row.get(COLS["contact_name"], "")) else "",
        "ContactPhone": row.get(COLS["contact_phone"], "") if not pd.isna(row.get(COLS["contact_phone"], "")) else "",
        "ContactJob": row.get(COLS["contact_job"], "") if not pd.isna(row.get(COLS["contact_job"], "")) else "",
    }
    # Normalize empty Nones to ""
    for k, v in list(out.items()):
        if v is None:
            out[k] = ""
    return out


def main():
    parser = argparse.ArgumentParser(description="Create relevant_info.json files from JobTracker.csv.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing relevant_info.json files")
    parser.add_argument("--dry-run", action="store_true", help="Only print actions, don't write files")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    csv_path = repo_root / CSV_REL_PATH
    sol_dir = repo_root / SOLICITATIES_DIR

    if not csv_path.exists():
        raise SystemExit(f"CSV not found at: {csv_path}")
    if not sol_dir.exists():
        raise SystemExit(f"Solicitaties folder not found at: {sol_dir}")

    df = pd.read_csv(csv_path)

    missing = [c for c in COLS.values() if c not in df.columns]
    if missing:
        print("[WARN] Missing columns in CSV, continuing with what we have:", missing)

    created, skipped, warnings = 0, 0, 0

    # Speed up matching, filtering
    for (job_sub, company_sub), folder_name in MAPPING.items():
        folder_path = sol_dir / folder_name
        if not folder_path.exists():
            print(f"[WARN] Folder not found, skipping mapping: {folder_name}")
            warnings += 1
            continue

        # Find candidate rows
        mask = df.apply(lambda r: row_matches(r, job_sub, company_sub), axis=1)
        candidates = df[mask]

        # Just force it at this point
        if len(candidates) > 1:
            if "Cybercrime" in folder_name:
                candidates = candidates[candidates[COLS["job"]].str.contains("Cybercrime", case=False, na=False)]
            if "EasyToys" in folder_name and candidates.empty:
                candidates = df[df[COLS["company"]].str.contains("EDC", case=False, na=False)]

        # If still multiple, use stats.json to choose
        stats = read_stats_json(folder_path)
        chosen = pick_best_match(candidates, stats, COLS, folder_name)

        if chosen is None or candidates.empty:
            print(f"[WARN] No CSV row matched for: {folder_name}  (job~'{job_sub}' company~'{company_sub}')")
            warnings += 1
            continue

        info = to_relevant_info(chosen)

        out_path = folder_path / "relevant_info.json"
        if out_path.exists() and not args.force:
            print(f"[SKIP] {out_path} exists (use --force to overwrite)")
            skipped += 1
            continue

        if args.dry_run:
            print(f"[DRY] Would write: {out_path}")
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            out_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[OK]  Wrote: {out_path}")
            created += 1

    print(f"\nDone. Created: {created}, Skipped: {skipped}, Warnings: {warnings}")


if __name__ == "__main__":
    main()
