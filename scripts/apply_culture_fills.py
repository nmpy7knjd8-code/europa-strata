#!/usr/bin/env python3
"""Apply art/ideas/philosophy/science culture fills to kingdom packs + deep-time timeline.

Kingdom: merge A+B, then overlay culture-fill/*.json philosophy (and any other fields).
Deep-time: generate polity- and layer-level fills grounded in existing art/religion/layers.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STORE = Path("/cursor/stores/self/internal")
ENRICH = STORE / "kingdom-enrichment"
CULTURE_FILL = ENRICH / "culture-fill"
DT_FILL = STORE / "deep-time-enrichment" / "culture-fill"
SITE_KINGDOM = REPO / "data" / "kingdom-eras"
TIMELINE = REPO / "data" / "timeline.json"

ERAS = ("high-medieval", "renaissance", "early-modern", "modern")

# Periods where "philosophy" means ritual/cosmology, not named schools
PRELITERATE = {
    "mesolithic",
    "early-neolithic",
    "middle-neolithic",
    "yamnaya",
    "beaker-corded",
    "nordic-bronze",
    "iron-age",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def first_sentence(text: str, max_len: int = 180) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip())
    if not t:
        return ""
    m = re.split(r"(?<=[.!?])\s+", t, maxsplit=1)
    s = m[0]
    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + "…"
    return s


def dominant_layers(period: dict, iso: str) -> list[dict]:
    layers = []
    for l in period.get("mapLayers") or []:
        if iso in (l.get("countries") or []):
            layers.append(l)
    # prefer dominant/incoming roles
    layers.sort(key=lambda l: 0 if l.get("role") == "dominant" else 1 if l.get("role") == "incoming" else 2)
    return layers


def dt_ideas(period: dict, iso: str, pol: dict, layers: list[dict]) -> str:
    labels = ", ".join(l.get("label") or l.get("id") for l in layers[:2]) or "local groups"
    art_bit = first_sentence(pol.get("art") or "")
    rel_bit = first_sentence(pol.get("religion") or "")
    pid = period["id"]
    place = pol.get("name") or iso
    if pid in PRELITERATE or pid in {"migration"} and not any(
        x in (layers[0].get("id") if layers else "") for x in ("roman", "greek", "latin")
    ):
        return (
            f"In {place} under the {labels} horizon, social ideas show in burial rites, "
            f"exchange gifts, and household layout more than in texts. "
            f"{rel_bit or art_bit}"
        ).strip()
    return (
        f"{place} in the {period.get('label')} frame organizes power and belonging through "
        f"{labels}. {rel_bit or art_bit}"
    ).strip()


def dt_philosophy(period: dict, iso: str, pol: dict, layers: list[dict]) -> str:
    labels = ", ".join(l.get("label") or l.get("id") for l in layers[:2]) or "this cultural slice"
    place = pol.get("name") or iso
    pid = period["id"]
    rel = first_sentence(pol.get("religion") or "")
    if pid in PRELITERATE:
        return (
            f"No named philosophical schools survive for {labels} in {place}; "
            f"cosmology is inferred from ritual deposits, burial posture, and craft canons—"
            f"honestly thin as doctrine, thick as practice. {rel}"
        ).strip()
    if pid in {"iron-age", "classical"}:
        return (
            f"Where literacy reaches {place}, argument about gods, fate, and the good life "
            f"can be named; elsewhere {labels} still speak through sanctuary and law. {rel}"
        ).strip()
    if pid in {"migration", "frankish", "vikings"}:
        return (
            f"Political theology is conversion, kingship sacralization, and customary law "
            f"under {labels}—philosophy as who may judge and who is protected. {rel}"
        ).strip()
    # medieval–modern deep-time schematic slices
    return (
        f"In this deep-time schematic of {place}, ideas of legitimacy, confession, and "
        f"law track the {labels} map layer—read alongside kingdom-era panels for denser named schools. {rel}"
    ).strip()


def dt_science(period: dict, iso: str, pol: dict, layers: list[dict]) -> str:
    labels = ", ".join(l.get("label") or l.get("id") for l in layers[:2]) or "local craft"
    place = pol.get("name") or iso
    art = first_sentence(pol.get("art") or "")
    pid = period["id"]
    if pid in {"mesolithic"}:
        return (
            f"Forager science in {place} is landscape literacy: microlith geometries, "
            f"seasonal scheduling, hide and bone toolkits under the {labels} horizon. {art}"
        ).strip()
    if pid in {"early-neolithic", "middle-neolithic"}:
        return (
            f"Farming knowledge—cereal calendars, animal management, ceramic temper, "
            f"and monument surveying—defines {labels} technical culture in {place}. {art}"
        ).strip()
    if pid in {"yamnaya", "beaker-corded"}:
        return (
            f"Pastoral mobility, early metallurgy, wagon/wheel know-how, and ceramic "
            f"standardization are the measurable sciences of {labels} across {place}. {art}"
        ).strip()
    if pid in {"nordic-bronze", "iron-age"}:
        return (
            f"Bronze/iron alloying, ship and wagon carpentry, and long-distance amber/metal "
            f"routes encode applied science for {labels} in {place}. {art}"
        ).strip()
    if pid == "classical":
        return (
            f"Surveying, medicine, natural philosophy, and military engineering travel with "
            f"{labels}; {place} participates as producer or provincial adopter. {art}"
        ).strip()
    return (
        f"Technical culture in {place} for this slice follows {labels}: "
        f"agrarian calendars, craft guilds or state arsenals, and whatever astral or medical "
        f"learning the period's elites keep. {art}"
    ).strip()


def layer_fill(period: dict, layer: dict) -> dict:
    """Culture fields particular to a map layer (archaeological culture / polity zone)."""
    label = layer.get("label") or layer["id"]
    pid = period["id"]
    note = (layer.get("note") or "").strip()
    role = layer.get("role") or "presence"
    art = (
        f"Material signature of {label}: the objects, monuments, and dress styles that "
        f"archaeologists use to draw this {role} layer on the {period.get('label')} map."
        + (f" {note}" if note else "")
    )
    if pid in PRELITERATE:
        ideas = (
            f"{label} ideas of belonging are read from graves, enclosures, and exchange—"
            f"who is buried with what, who shares ceramic recipes, who is kept outside the ditch."
        )
        philosophy = (
            f"Named philosophers are anachronistic for {label}. Treat cosmology as ritual "
            f"geometry, ancestor practice, and craft taboo—reconstructed, not quoted."
        )
        science = (
            f"Craft science of {label}: lithic or metal chaînes opératoires, ceramic tempers, "
            f"and environmental scheduling that made this horizon reproducible across sites."
        )
    elif pid in {"iron-age", "classical"}:
        ideas = f"{label} encodes status, warfare, and sanctuary politics visible in oppida, temples, or civic centers."
        philosophy = (
            f"Where {label} overlaps literate zones, Greek/Roman (or neighboring) ethical and "
            f"political argument can be cited; on the fringe, law and cult still carry the load."
        )
        science = f"Technical repertoire tied to {label}: metallurgy, surveying, medicine, and logistics of army or agora."
    else:
        ideas = f"{label} marks a political-cultural claim in the {period.get('label')} schematic—law, confession, and court style."
        philosophy = (
            f"Political and religious thought attached to {label} in this era: legitimacy, "
            f"confession, and corporate privilege (see kingdom packs for denser named schools)."
        )
        science = f"Administrative, military, and artisanal knowledge sustaining {label} on this map."
    return {
        "art": art,
        "ideas": ideas,
        "philosophy": philosophy,
        "science": science,
    }


def apply_deep_time() -> dict:
    timeline = load(TIMELINE)
    stats = {"polityFilled": 0, "layerFilled": 0, "periods": []}
    fill_export = {"version": 1, "periods": {}}

    for period in timeline["periods"]:
        pid = period["id"]
        per_export = {"polities": {}, "layers": {}}
        for iso, pol in (period.get("polities") or {}).items():
            layers = dominant_layers(period, iso)
            # Keep existing art; fill missing culture quartet
            if not str(pol.get("ideas") or "").strip():
                pol["ideas"] = dt_ideas(period, iso, pol, layers)
            if not str(pol.get("philosophy") or "").strip():
                pol["philosophy"] = dt_philosophy(period, iso, pol, layers)
            if not str(pol.get("science") or "").strip():
                pol["science"] = dt_science(period, iso, pol, layers)
            # Ensure art exists (already does) but never leave empty
            if not str(pol.get("art") or "").strip():
                labs = ", ".join(l.get("label") or "" for l in layers[:2])
                pol["art"] = f"Material culture of {pol.get('name') or iso} under {labs or period.get('label')}."
            stats["polityFilled"] += 1
            per_export["polities"][iso] = {
                "art": pol.get("art"),
                "ideas": pol.get("ideas"),
                "philosophy": pol.get("philosophy"),
                "science": pol.get("science"),
            }
        for layer in period.get("mapLayers") or []:
            fills = layer_fill(period, layer)
            for k, v in fills.items():
                if not str(layer.get(k) or "").strip():
                    layer[k] = v
            stats["layerFilled"] += 1
            per_export["layers"][layer["id"]] = {
                "art": layer.get("art"),
                "ideas": layer.get("ideas"),
                "philosophy": layer.get("philosophy"),
                "science": layer.get("science"),
            }
        fill_export["periods"][pid] = per_export
        stats["periods"].append(pid)

    save(TIMELINE, timeline)
    DT_FILL.mkdir(parents=True, exist_ok=True)
    save(DT_FILL / "all-periods.json", fill_export)
    (DT_FILL / "README.md").write_text(
        "# Deep-time culture fills\n\n"
        "Generated `all-periods.json` plus inlined into `data/timeline.json` "
        "polities and mapLayers (`art`, `ideas`, `philosophy`, `science`).\n"
        "Preliterate philosophy notes are explicitly non-nominal (ritual/cosmology).\n",
        encoding="utf-8",
    )
    return stats


def apply_kingdom_fill(era: str) -> dict:
    path = SITE_KINGDOM / f"{era}.json"
    pack = load(path)
    by = {p["id"]: p for p in pack["polities"]}
    applied = 0
    for fill_path in sorted(CULTURE_FILL.glob(f"{era}*.json")):
        doc = load(fill_path)
        for row in doc.get("fills") or []:
            pid = row.get("id")
            p = by.get(pid)
            if not p:
                continue
            for key in ("art", "ideas", "philosophy", "science"):
                if row.get(key) and (
                    doc.get("overwrite")
                    or not str(p.get(key) or "").strip()
                ):
                    p[key] = row[key]
                    applied += 1
    # Split bundled artIdeas if art duplicates ideas join
    for p in pack["polities"]:
        art = (p.get("art") or "").strip()
        ideas = (p.get("ideas") or "").strip()
        bundled = (p.get("artIdeas") or "").strip()
        if bundled and ideas and art == bundled and ideas in art:
            # art was merge-joined; restore art as portion before ideas
            if art.endswith(ideas):
                p["art"] = art[: -len(ideas)].strip() or art.split("\n\n")[0]
        if not ideas and bundled:
            parts = [x.strip() for x in bundled.split("\n\n") if x.strip()]
            if len(parts) >= 2:
                p["art"] = p.get("art") or parts[0]
                p["ideas"] = parts[1] if not ideas else ideas
    save(path, pack)
    return {"era": era, "fillOps": applied, "polities": len(pack["polities"])}


def coverage(era_path: Path) -> dict:
    pack = load(era_path)
    n = len(pack["polities"])
    out = {"n": n}
    for f in ("art", "ideas", "philosophy", "science"):
        out[f] = sum(1 for p in pack["polities"] if str(p.get(f) or "").strip())
    return out


def main():
    # Re-merge kingdoms from contest packs (best-of) then apply fills
    import subprocess
    import sys

    merge = REPO / "scripts" / "merge_kingdom_enrichment.py"
    for era in ERAS:
        subprocess.check_call(
            [sys.executable, str(merge), "--era", era, "--force-geo"],
            cwd=str(REPO),
        )
        print("merged", era, apply_kingdom_fill(era), coverage(SITE_KINGDOM / f"{era}.json"))

    dt = apply_deep_time()
    print("deep-time", dt)
    # verify deep-time coverage
    t = load(TIMELINE)
    miss = 0
    for p in t["periods"]:
        for pol in (p.get("polities") or {}).values():
            for f in ("art", "ideas", "philosophy", "science"):
                if not str(pol.get(f) or "").strip():
                    miss += 1
    print("deep-time missing fields", miss)


if __name__ == "__main__":
    main()
