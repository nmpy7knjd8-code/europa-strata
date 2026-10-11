#!/usr/bin/env python3
"""Overlay cleaned extentsByTick onto site kingdom packs (geometry only)."""
from __future__ import annotations
import argparse, json
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLEANED = Path("/cursor/stores/self/internal/kingdom-eras-cleaned")
SITE = REPO / "data" / "kingdom-eras"
ERAS = ("high-medieval", "renaissance", "early-modern", "modern")

def apply_era(era: str) -> dict:
    site_path = SITE / f"{era}.json"
    clean_path = CLEANED / f"{era}.json"
    site = json.loads(site_path.read_text(encoding="utf-8"))
    clean = json.loads(clean_path.read_text(encoding="utf-8"))
    cidx = {p["id"]: p for p in clean.get("polities") or [] if p.get("id")}
    changed = 0
    missing = []
    for p in site.get("polities") or []:
        pid = p.get("id")
        cp = cidx.get(pid)
        if not cp or not cp.get("extentsByTick"):
            if pid not in cidx:
                missing.append(pid)
            continue
        before = json.dumps(p.get("extentsByTick"), sort_keys=True)
        after = json.dumps(cp["extentsByTick"], sort_keys=True)
        if before != after:
            p["extentsByTick"] = deepcopy(cp["extentsByTick"])
            changed += 1
    # drop polities that cleaned elided entirely? keep site polities; only overlay extents
    # if cleaned dropped an extent tick key, overlay full extentsByTick already handles it
    site_path.write_text(json.dumps(site, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"era": era, "polities": len(site.get("polities") or []), "extentChanged": changed, "missingInCleaned": missing}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--era", choices=ERAS, action="append")
    args = ap.parse_args()
    eras = args.era or list(ERAS)
    for era in eras:
        print(json.dumps(apply_era(era)))

if __name__ == "__main__":
    main()
