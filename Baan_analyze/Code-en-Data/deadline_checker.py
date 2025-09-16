#!/usr/bin/env python3
# rank_deadlines.py
#
# Plaats dit script in: Baan_analyze/Code-en-Data
# Output: Baan_analyze/Code-en-Data/Deadlines_ranked.txt
#
# Loopt door ../.. /Solicitaties/<Job>_—_<Company>/relevant_info.json,
# pakt de Deadline en sorteert van dichtstbij tot verste weg.
# Daarna twee lege regels, en vervolgens alle onbekende deadlines.

from __future__ import annotations
from pathlib import Path
import json
import re
from datetime import date

def parse_folder_name(name: str) -> tuple[str, str]:
    """'[Job]_—_[Company]' -> ('Job', 'Company'), underscores -> spaces."""
    if "—" in name:
        left, right = name.split("—", 1)
    elif "-" in name:
        left, right = name.split("-", 1)
    else:
        return name.replace("_", " ").strip(), ""
    return left.replace("_", " ").strip(), right.replace("_", " ").strip()

def parse_deadline(s) -> date | None:
    """Parseer 'YYYY-MM-DD' (tolerant voor 1-cijferige maand/dag en / of -)."""
    if not s or str(s).strip().lower() in {"", "none", "null", "unknown", "onbekend"}:
        return None
    txt = str(s).strip()
    # Sta zowel 2025-9-3 als 2025/09/03 toe
    txt = re.sub(r"[./]", "-", txt)
    m = re.match(r"^\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*$", txt)
    if not m:
        return None
    y, mth, d = map(int, m.groups())
    try:
        return date(y, mth, d)
    except ValueError:
        return None

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    sollicitaties = repo_root / "Solicitaties"

    if not sollicitaties.exists():
        raise SystemExit(f"Map niet gevonden: {sollicitaties}")

    known: list[tuple[date, str, str]] = []
    unknown: list[tuple[str, str]] = []

    for entry in sorted(sollicitaties.iterdir()):
        if not entry.is_dir():
            continue
        job, company = parse_folder_name(entry.name)
        info_path = entry / "relevant_info.json"
        if not info_path.exists():
            # Geen file? Zet bij onbekend.
            unknown.append((job, company))
            continue

        try:
            data = json.loads(info_path.read_text(encoding="utf-8"))
        except Exception:
            unknown.append((job, company))
            continue

        dl = parse_deadline(data.get("Deadline"))
        if dl:
            known.append((dl, job, company))
        else:
            unknown.append((job, company))

    # sorteer bekende deadlines
    known.sort(key=lambda t: t[0])

    out_path = script_dir / "Deadlines_ranked.txt"
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for dl, job, company in known:
            f.write(f"{dl.isoformat()} - {job} — {company}\n")

        # twee lege regels
        f.write("\n\n")

        for job, company in unknown:
            if company:
                f.write(f"{job} — {company}\n")
            else:
                f.write(f"{job}\n")

    print(f"[OK] Geschreven naar: {out_path}  (bekend: {len(known)}, onbekend: {len(unknown)})")

if __name__ == "__main__":
    main()
