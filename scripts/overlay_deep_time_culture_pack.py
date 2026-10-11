#!/usr/bin/env python3
"""Overlay authored deep-time culture-fill packs (region × period) into timeline.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TIMELINE = REPO / "data" / "timeline.json"
FILL_DIR = Path("/cursor/stores/self/internal/deep-time-enrichment/culture-fill")
FIELDS = ("culture", "art", "ideas", "philosophy", "science")


def overlay_region_pack(timeline: dict, pack: dict) -> dict:
    """Pack shape: { periodIds, regionIds, regions: {rid: {periodId: {fields}}} }"""
    region_countries = timeline.get("meta", {}).get("regionCountries") or {}
    periods_by_id = {p["id"]: p for p in timeline["periods"]}
    stats = {"regions": 0, "polities": 0}
    for pid in pack.get("periodIds") or []:
        period = periods_by_id.get(pid)
        if not period:
            continue
        if not isinstance(period.get("regions"), dict):
            period["regions"] = {}
        for rid in pack.get("regionIds") or []:
            slice_ = (pack.get("regions") or {}).get(rid, {}).get(pid)
            if not slice_:
                continue
            reg = period["regions"].setdefault(rid, {})
            for f in FIELDS:
                if slice_.get(f):
                    reg[f] = slice_[f]
            stats["regions"] += 1
            for iso in region_countries.get(rid) or []:
                pol = (period.get("polities") or {}).get(iso)
                if not pol:
                    continue
                for f in FIELDS:
                    if slice_.get(f):
                        pol[f] = slice_[f]
                stats["polities"] += 1
    pack_id = pack.get("packId") or "culture-pack"
    packs = timeline.setdefault("meta", {}).setdefault("cultureFillPacks", [])
    if pack_id not in packs:
        packs.append(pack_id)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack", type=Path, help="Path to *-culture.json region pack")
    args = ap.parse_args()
    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    if "regions" not in pack:
        raise SystemExit(
            f"{args.pack} is not a region×period pack (expected top-level 'regions'). "
            "Layer/culture-keyed bundles need a separate adapter."
        )
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    stats = overlay_region_pack(timeline, pack)
    TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stamp = FILL_DIR / f"{pack.get('packId', args.pack.stem)}-applied.json"
    stamp.write_text(
        json.dumps({"applied": str(args.pack), "stats": stats}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"pack": pack.get("packId"), **stats}, indent=2))


if __name__ == "__main__":
    main()
