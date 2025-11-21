"""Calculate and update PotentialSatisfaction for all active jobs."""
from __future__ import annotations
from pathlib import Path
import json
import math

# Salary curve parameters
S0 = 2200.0
SMAX = 10.0
B = 3.0
K = math.log((SMAX - B) / (SMAX - 9.5)) / (6000.0 - S0)

# Sharpening factor
GAMMA = 1.7

# Component weights
W_PREF = 0.50
W_FIT = 0.25
W_SALARY = 0.25
W_TOTAL = W_PREF + W_FIT + W_SALARY

# Fit mapping
FIT_MAP = {
    "strong": 10.0,
    "good": 8.5,
    "maybe": 6.5,
    "stretch": 5.5,
    "hold": 3.0,
    "bad": 1.5,
}

def salary_weight(salary_num: float | int | None) -> float:
    """Convert salary to weight (3-10 scale)."""
    s = S0 if salary_num is None else float(round(salary_num))
    val = B + (SMAX - B) * (1.0 - math.exp(-K * (s - S0)))
    return B if not math.isfinite(val) else max(0.0, min(SMAX, val))

def normalize_fit(val) -> float:
    """Normalize fit to 0-1 range."""
    if isinstance(val, (int, float)):
        x = float(val)
    elif isinstance(val, str):
        key = val.strip().lower()
        x = FIT_MAP.get(key, 0.0) if key in FIT_MAP else float(key.replace(",", ".") if key else 0)
    else:
        x = 0.0
    return max(0.0, min(10.0, x)) / 10.0

def normalize_pref(val) -> float:
    """Normalize preference to 0-1 range."""
    try:
        x = float(val)
    except Exception:
        x = 0.0
    return max(0.0, min(10.0, x if math.isfinite(x) else 0.0)) / 10.0

def salary_norm_from_weight(sal_w: float) -> float:
    """Convert salary weight to normalized value."""
    return max(0.0, min(1.0, (sal_w - B) / (SMAX - B)))

def sharpen(x: float) -> float:
    """Apply gamma sharpening."""
    return 0.0 if x <= 0.0 else x ** GAMMA

def compute_potential_satisfaction(fit_num: float, pref_num: float, sal_weight_val: float) -> float:
    """Calculate PotentialSatisfaction score (0-10)."""
    p = sharpen(normalize_pref(pref_num))
    f = sharpen(normalize_fit(fit_num))
    s = sharpen(salary_norm_from_weight(sal_weight_val))
    
    sum_terms = (W_PREF * p) + (W_FIT * f) + (W_SALARY * s)
    score_raw = 0.0 if sum_terms <= 0 else (10.0 * (sum_terms / W_TOTAL)) + 1.0
    
    return float(f"{min(10.0, max(0.0, score_raw)):.1f}")

def parse_folder_name(name: str) -> tuple[str, str]:
    """Extract job and company from folder name."""
    sep = "—" if "—" in name else "-"
    if sep in name:
        left, right = name.split(sep, 1)
        return left.replace("_", " ").strip(), right.replace("_", " ").strip()
    return name.replace("_", " ").strip(), ""

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    sollicitaties = repo_root / "Solicitaties"
    
    if not sollicitaties.exists():
        raise SystemExit(f"Solicitaties folder not found at: {sollicitaties}")

    updated, skipped, errors = 0, 0, 0
    print("Updating PotentialSatisfaction for active jobs...\n")

    for entry in sorted(sollicitaties.iterdir()):
        if not entry.is_dir() or entry.name == "Archief":
            continue

        rel_path = entry / "relevant_info.json"
        stats_path = entry / "stats.json"
        
        if not rel_path.exists():
            print(f"  ⚠ {entry.name}: No relevant_info.json, skipping")
            skipped += 1
            continue

        if not stats_path.exists():
            print(f"  ⚠ {entry.name}: No stats.json, skipping")
            skipped += 1
            continue

        try:
            rel_data = json.loads(rel_path.read_text(encoding="utf-8"))
            salary_raw = rel_data.get("Salary")
            fit_raw = rel_data.get("Fit", 0)
            pref_raw = rel_data.get("Preference", 0)

            # Parse salary
            salary_num = None
            if isinstance(salary_raw, (int, float)):
                salary_num = float(salary_raw)
            elif isinstance(salary_raw, str) and salary_raw.strip():
                cleaned = salary_raw.replace("€", "").replace("k", "000").replace(",", ".")
                try:
                    salary_num = float("".join(ch for ch in cleaned if ch.isdigit() or ch == "."))
                except Exception:
                    pass

            # Calculate score
            sal_w = salary_weight(salary_num)
            score = compute_potential_satisfaction(fit_raw, pref_raw, sal_w)

            # Update stats.json
            stats_data = json.loads(stats_path.read_text(encoding="utf-8"))
            old_score = stats_data.get("PotentialSatisfaction")
            stats_data["PotentialSatisfaction"] = score

            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)

            if old_score != score:
                print(f"  ✓ {entry.name}: {old_score} → {score}")
            else:
                print(f"  ✓ {entry.name}: {score} (unchanged)")
            
            updated += 1

        except Exception as e:
            print(f"  ✗ {entry.name}: Error - {e}")
            errors += 1

    print(f"\n{'='*60}")
    print(f"✓ PotentialSatisfaction update complete!")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    main()
