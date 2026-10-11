#!/usr/bin/env python3
"""Apply kingdom-eras-cleaned/*-qa-fixes.json patches to site packs (and cleaned mirrors)."""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "data" / "kingdom-eras"
FIXDIR = Path("/cursor/stores/self/internal/kingdom-eras-cleaned")


def apply_fixes(pack_path: Path, fixes_doc: dict) -> dict:
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in pack.get("polities") or []}
    applied = 0
    missing = []
    for fix in fixes_doc.get("fixes") or []:
        pid = fix.get("id")
        tick = str(fix.get("tick"))
        patch = fix.get("fix") or {}
        p = by_id.get(pid)
        if not p:
            missing.append(pid)
            continue
        ext = (p.get("extentsByTick") or {}).get(tick)
        if not isinstance(ext, dict):
            missing.append(f"{pid}@{tick}")
            continue
        for k, v in patch.items():
            ext[k] = v
        applied += 1
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "era": fixes_doc.get("era"),
        "applied": applied,
        "fixCount": len(fixes_doc.get("fixes") or []),
        "missing": sorted(set(missing)),
    }


def main():
    for fixes_path in sorted(FIXDIR.glob("*-qa-fixes.json")):
        doc = json.loads(fixes_path.read_text(encoding="utf-8"))
        era = doc["era"]
        r = apply_fixes(SITE / f"{era}.json", doc)
        clean = FIXDIR / f"{era}.json"
        if clean.is_file():
            r["cleanedApplied"] = apply_fixes(clean, doc)["applied"]
        print(json.dumps(r))


if __name__ == "__main__":
    main()
