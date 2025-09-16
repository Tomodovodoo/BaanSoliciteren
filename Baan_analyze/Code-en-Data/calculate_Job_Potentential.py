#!/usr/bin/env python3
# calculate_Job_Potential.py
#
# Reads ../.. /Solicitaties/<Job>_—_<Company>/relevant_info.json,
# computes a PotentialSatisfaction, and writes CalculatedJobPotential.csv next to this script.

from __future__ import annotations
from pathlib import Path
import json
import math
import csv


# Tunable parameters

# Salary curve: F(s) = B + (SMAX - B) * (1 - exp(-K * (s - S0)))
S0   = 2200.0
SMAX = 10.0
B    = 3.0 # Minimaal Salaris krijgt een 3
K    = math.log((SMAX - B) / (SMAX - 9.5)) / (6000.0 - S0)  # een salaris van 6000 krijgt een 9.5

# Component sharpening, vergroot verschillen
GAMMA = 1.7

# Weights van componenten, Preferentie is het belangrijkst voor me.
W_PREF   = 0.50
W_FIT    = 0.25
W_SALARY = 0.25
W_TOTAL  = W_PREF + W_FIT + W_SALARY

# Hoe goed ik mijn baan kan doen zonder veel extra training
FIT_MAP = {
    "strong": 10.0,
    "good": 8.5,
    "maybe": 6.5,
    "stretch": 5.5,
    "hold": 3.0,
    "bad": 1.5,
}

# Helpers
def salary_weight(salary_num: float | int | None) -> float:
    """Salary curve F(s) met clamp tot 10; Missend Salaris = Minimum Salaris. (In de stats heb ik een indicatie salaris al toegevoegd)"""
    if salary_num is None:
        s = S0
    else:
        try:
            s = float(round(salary_num))
        except Exception:
            s = S0
    val = B + (SMAX - B) * (1.0 - math.exp(-K * (s - S0)))
    if not math.isfinite(val):
        return B
    return max(0.0, min(SMAX, val))

def normalize_fit(val) -> float:
    """Fit naar nummer mapping"""
    if isinstance(val, (int, float)):
        x = float(val)
    elif isinstance(val, str):
        key = val.strip().lower()
        if key in FIT_MAP:
            x = FIT_MAP[key]
        else:
            try:
                x = float(key.replace(",", "."))
            except Exception:
                x = 0.0
    else:
        x = 0.0
    return max(0.0, min(10.0, x)) / 10.0

def normalize_pref(val) -> float:
    """Preferentie normalizering (extra beveiliging)"""
    try:
        x = float(val)
    except Exception:
        x = 0.0
    if not math.isfinite(x):
        x = 0.0
    return max(0.0, min(10.0, x)) / 10.0

def salary_norm_from_weight(sal_w: float) -> float:
    """Salaris gewicht naar normalizering"""
    return max(0.0, min(1.0, (sal_w - B) / (SMAX - B)))

def sharpen(x: float) -> float:
    """Verscherping gebaseerd op Gamma voor extra aanduiding voor betere/slechtere kandidaat banen"""
    if x <= 0.0:
        return 0.0
    return x ** GAMMA

def compute_potential_satisfaction(fit_num: float, pref_num: float, sal_weight_val: float) -> tuple[float, float, float, float]:
    """
    Keert terug:
      score_10 (Afgerond op 1 decimaal),
      pref_share, fit_share, salary_share  (elk in range van 0-1.)
    """
    p = normalize_pref(pref_num)                    # Preference
    f = normalize_fit(fit_num)                      # Fit
    s = salary_norm_from_weight(sal_weight_val)     # Salary

    # Sharpen voor seperatie
    p_s = sharpen(p)
    f_s = sharpen(f)
    s_s = sharpen(s)

    # Gewichten invoegen
    sum_terms = (W_PREF * p_s) + (W_FIT * f_s) + (W_SALARY * s_s)
    if sum_terms <= 0:
        pref_share = fit_share = salary_share = 0.0
        score_raw = 0.0
    else:
        pref_share   = (W_PREF   * p_s) / sum_terms
        fit_share    = (W_FIT    * f_s) / sum_terms
        salary_share = (W_SALARY * s_s) / sum_terms
        score_raw = (10.0 * (sum_terms / W_TOTAL))+ 1.0

    score_10 = float(f"{min(10.0, max(0.0, score_raw)):.1f}")
    return score_10, pref_share, fit_share, salary_share

def parse_folder_name(name: str) -> tuple[str, str]:
    """Krijgt Job+Company naam van folders"""
    sep = "—"
    if sep in name:
        left, right = name.split(sep, 1)
    elif "-" in name:
        left, right = name.split("-", 1)
    else:
        return name.replace("_", " ").strip(), ""
    return left.replace("_", " ").strip(), right.replace("_", " ").strip()

# Main
def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    sollicitaties = repo_root / "Solicitaties"
    if not sollicitaties.exists():
        raise SystemExit(f"Solicitaties folder not found at: {sollicitaties}")

    rows = []

    for entry in sorted(sollicitaties.iterdir()):
        if not entry.is_dir():
            continue

        job, company = parse_folder_name(entry.name)
        rel_path = entry / "relevant_info.json"
        if not rel_path.exists():
            print(f"[WARN] relevant_info.json not found, skipping: {entry}")
            continue

        try:
            data = json.loads(rel_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Could not read JSON in {rel_path}: {e}")
            continue

        salary_raw = data.get("Salary", None)
        fit_raw    = data.get("Fit", 0)
        pref_raw   = data.get("Preference", 0)

        # Dubbelcheck Salaris een nummer is en geen string
        salary_num = None
        if isinstance(salary_raw, (int, float)):
            salary_num = float(salary_raw)
        elif isinstance(salary_raw, str) and salary_raw.strip():
            cleaned = (
                salary_raw.replace("€", "")
                          .replace("k", "000")
                          .replace(",", ".")
            )
            try:
                salary_num = float("".join(ch for ch in cleaned if ch.isdigit() or ch == "."))
            except Exception:
                salary_num = None

        sal_w = salary_weight(salary_num)
        score, p_share, f_share, s_share = compute_potential_satisfaction(fit_raw, pref_raw, sal_w)

        rows.append({
            "Job": job,
            "Company": company,
            "PotentialSatisfaction": score,
            "PreferenceBased": round(p_share, 6),
            "FitBased": round(f_share, 6),
            "SalaryBased": round(s_share, 6),
        })

    out_path = script_dir / "CalculatedJobPotential.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Job", "Company", "PotentialSatisfaction", "PreferenceBased", "FitBased", "SalaryBased"]
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"[OK] Wrote {len(rows)} rows to: {out_path}")

if __name__ == "__main__":
    main()
