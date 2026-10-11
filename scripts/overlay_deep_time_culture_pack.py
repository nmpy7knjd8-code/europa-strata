#!/usr/bin/env python3
"""Overlay authored deep-time culture-fill packs into timeline.json.

Supports:
  1) Region packs: { periodIds, regionIds, regions: {rid: {periodId: fields}} }
     e.g. neolithic-culture.json, bronze-culture.json
  2) Period packs: { periodIds, periods: {pid: {polities: {ISO: fields}, layers: {id: fields}}} }
     e.g. iron-classical-culture.json, migration-culture.json
  3) Legacy layer list: { cultures: [{id, periodId, ...fields}] }
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TIMELINE = REPO / "data" / "timeline.json"
FILL_DIR = Path("/cursor/stores/self/internal/deep-time-enrichment/culture-fill")
FIELDS = ("culture", "art", "ideas", "philosophy", "science")


def norm_id(s: str | None) -> str:
    return (s or "").strip()


def apply_fields(target: dict, src: dict, *, overwrite: bool = True) -> int:
    n = 0
    for f in FIELDS:
        if src.get(f) and (overwrite or not str(target.get(f) or "").strip()):
            target[f] = src[f]
            n += 1
    if src.get("label") and not target.get("label"):
        target["label"] = src["label"]
    return n


def overlay_region_pack(timeline: dict, pack: dict) -> dict:
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
            apply_fields(reg, slice_)
            stats["regions"] += 1
            for iso in region_countries.get(rid) or []:
                pol = (period.get("polities") or {}).get(iso)
                if not pol:
                    continue
                apply_fields(pol, slice_)
                stats["polities"] += 1
    return stats


def find_layer(period: dict, layer_id: str) -> dict | None:
    want = norm_id(layer_id)
    for layer in period.get("mapLayers") or []:
        if norm_id(layer.get("id")) == want:
            # Repair leading-space ids in timeline if present
            if layer.get("id") != want and want:
                layer["id"] = want
            return layer
    return None


def overlay_period_pack(timeline: dict, pack: dict) -> dict:
    periods_by_id = {p["id"]: p for p in timeline["periods"]}
    stats = {"polities": 0, "layers": 0, "missingLayers": []}
    for pid, body in (pack.get("periods") or {}).items():
        period = periods_by_id.get(pid)
        if not period or not isinstance(body, dict):
            continue
        for iso, fields in (body.get("polities") or {}).items():
            pol = (period.get("polities") or {}).get(iso)
            if not pol or not isinstance(fields, dict):
                continue
            apply_fields(pol, fields)
            stats["polities"] += 1
        for lid, fields in (body.get("layers") or {}).items():
            layer = find_layer(period, lid)
            if not layer:
                stats["missingLayers"].append(f"{pid}:{lid!r}")
                continue
            if isinstance(fields, dict):
                apply_fields(layer, fields)
                stats["layers"] += 1
    return stats


def overlay_culture_list(timeline: dict, pack: dict) -> dict:
    periods_by_id = {p["id"]: p for p in timeline["periods"]}
    stats = {"layers": 0, "missingLayers": []}
    for c in pack.get("cultures") or []:
        if not isinstance(c, dict):
            continue
        pid = c.get("periodId")
        lid = c.get("id")
        period = periods_by_id.get(pid)
        if not period:
            stats["missingLayers"].append(f"{pid}:{lid!r}")
            continue
        layer = find_layer(period, lid)
        if not layer:
            stats["missingLayers"].append(f"{pid}:{lid!r}")
            continue
        apply_fields(layer, c)
        stats["layers"] += 1
    return stats


def overlay_pack(timeline: dict, pack: dict) -> dict:
    if pack.get("regions"):
        return {"shape": "regions", **overlay_region_pack(timeline, pack)}
    if pack.get("periods") and isinstance(pack["periods"], dict):
        return {"shape": "periods", **overlay_period_pack(timeline, pack)}
    if pack.get("cultures"):
        return {"shape": "cultures", **overlay_culture_list(timeline, pack)}
    raise SystemExit("Unrecognized culture pack shape")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "packs",
        nargs="*",
        type=Path,
        help="Pack JSON paths (default: known authored packs in culture-fill/)",
    )
    args = ap.parse_args()
    paths = args.packs or [
        FILL_DIR / "neolithic-culture.json",
        FILL_DIR / "bronze-culture.json",
        FILL_DIR / "iron-classical-culture.json",
        FILL_DIR / "migration-culture.json",
    ]
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    report = []
    for path in paths:
        if not path.is_file():
            report.append({"path": str(path), "error": "missing"})
            continue
        pack = json.loads(path.read_text(encoding="utf-8"))
        stats = overlay_pack(timeline, pack)
        pack_id = pack.get("packId") or path.stem
        packs = timeline.setdefault("meta", {}).setdefault("cultureFillPacks", [])
        if pack_id not in packs:
            packs.append(pack_id)
        # drop stale migration-layer tag if full migration pack applied
        if pack_id == "migration" and "migration-layer" in packs:
            packs.remove("migration-layer")
        stamp = FILL_DIR / f"{pack_id}-applied.json"
        stamp.write_text(
            json.dumps({"applied": str(path), "stats": stats}, indent=2) + "\n",
            encoding="utf-8",
        )
        report.append({"pack": pack_id, **stats})
        print(json.dumps(report[-1]))

    TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Repair Magna-germania id if still spaced anywhere
    fixed = 0
    for period in timeline["periods"]:
        for layer in period.get("mapLayers") or []:
            if isinstance(layer.get("id"), str) and layer["id"] != layer["id"].strip():
                layer["id"] = layer["id"].strip()
                fixed += 1
    if fixed:
        TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"strippedLayerIds": fixed}))


if __name__ == "__main__":
    main()
