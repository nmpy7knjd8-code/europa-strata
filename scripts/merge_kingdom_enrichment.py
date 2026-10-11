#!/usr/bin/env python3
"""Merge kingdom enrichment contest packs (A vs B) + cleaned geometry into site packs.

Sources (Project Agent Store):
  internal/kingdom-enrichment/{era}-a.json
  internal/kingdom-enrichment/{era}-b.json
  internal/kingdom-eras-cleaned/{era}.json
  internal/kingdom-eras-cleaned/QA-REPORT.md  (readiness hint only)
  internal/kingdom-eras/{era}.json           (base fallback)

Output:
  data/kingdom-eras/{era}.json
  internal/kingdom-enrichment/merge-{era}.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STORE = Path("/cursor/stores/self/internal")
ENRICH = STORE / "kingdom-enrichment"
CLEANED = STORE / "kingdom-eras-cleaned"
BASE_STORE = STORE / "kingdom-eras"
SITE = REPO / "data" / "kingdom-eras"

ERAS = ("high-medieval", "renaissance", "early-modern", "modern")

TEXT_FIELDS = (
    "description",
    "summary",
    "conflicts",
    "leaders",
    "religion",
    "culture",
    "story",
    "literature",
    "art",
    "ideas",
    "artIdeas",
    "artAndIdeas",
    "philosophy",
    "science",
)

# Map contest aliases → canonical polity fields (never “interesting things”)
FIELD_ALIASES = {
    "artIdeas": ("artIdeas", "artAndIdeas", "art_and_ideas"),
    "ideas": ("ideas", "intellectualLife", "intellectual_life"),
    "philosophy": ("philosophy", "thought", "ideasPhilosophy"),
    "science": ("science", "scienceAndMedicine", "science_medicine", "naturalPhilosophy"),
    "art": ("art", "artAndMaterialCulture", "materialCulture"),
    "story": ("story", "stories"),
}

HEADING_RE = re.compile(
    r"^\s*(interesting things|fun facts|did you know|misc\.?|miscellaneous)\s*:?\s*",
    re.I | re.M,
)


def load_json(path: Path):
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def clean_prose(text: str | None) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = HEADING_RE.sub("", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def score_text(s: str) -> tuple:
    """Prefer longer, paragraph-rich copy."""
    s = clean_prose(s)
    if not s:
        return (0, 0, 0)
    return (1, len(s), s.count("\n"))


def pick_text(*candidates: str | None) -> str:
    best = ""
    best_score = (0, 0, 0)
    for c in candidates:
        t = clean_prose(c)
        sc = score_text(t)
        if sc > best_score:
            best_score = sc
            best = t
    return best


def normalize_images(images) -> list:
    if not images:
        return []
    if isinstance(images, dict):
        images = images.get("items") or images.get("images") or []
    out = []
    seen = set()
    for img in images:
        if not isinstance(img, dict):
            continue
        src = (img.get("src") or img.get("url") or "").strip()
        if not src or src in seen:
            continue
        seen.add(src)
        role = (img.get("role") or "").strip().lower() or None
        out.append(
            {
                "src": src,
                "caption": (img.get("caption") or "").strip(),
                "alt": (img.get("alt") or img.get("caption") or "").strip(),
                **({"role": role} if role else {}),
            }
        )
    return out


def merge_images(*lists) -> list | None:
    merged = []
    seen = set()
    for lst in lists:
        for img in normalize_images(lst):
            if img["src"] in seen:
                continue
            seen.add(img["src"])
            merged.append(img)
    return merged or None


def polity_index(pack: dict | None) -> dict:
    if not pack:
        return {}
    pols = pack.get("polities")
    if isinstance(pols, list):
        return {p.get("id"): p for p in pols if isinstance(p, dict) and p.get("id")}
    if isinstance(pols, dict):
        return {k: v for k, v in pols.items() if isinstance(v, dict)}
    return {}


def field_from_aliases(sources: list, canonical: str) -> str:
    keys = FIELD_ALIASES.get(canonical, (canonical,))
    return pick_text(*(s.get(k) for s in sources for k in keys))


def join_prose(*parts: str) -> str:
    seen = set()
    out = []
    for p in parts:
        t = clean_prose(p)
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return "\n\n".join(out)


def merge_polity(base: dict, *alts: dict) -> dict:
    out = deepcopy(base)
    sources = [base] + [a for a in alts if a]
    for field in TEXT_FIELDS:
        out[field] = pick_text(*(s.get(field) for s in sources))
    # Contest aliases → canonical intellectual fields
    out["ideas"] = field_from_aliases(sources, "ideas") or out.get("ideas", "")
    out["philosophy"] = field_from_aliases(sources, "philosophy") or out.get(
        "philosophy", ""
    )
    out["science"] = field_from_aliases(sources, "science") or out.get("science", "")
    art = field_from_aliases(sources, "art") or out.get("art", "")
    bundled = field_from_aliases(sources, "artIdeas")
    # Surface as Art & ideas (never an “interesting things” dump)
    out["artIdeas"] = bundled or join_prose(art, out.get("ideas", ""))
    out["art"] = out["artIdeas"] or art
    # Prefer description into summary alias if summary empty
    if not out.get("summary") and out.get("description"):
        out["summary"] = out["description"]
    out["images"] = merge_images(
        *(s.get("images") for s in sources),
        *(s.get("photos") for s in sources),
    )
    # stories alias → story
    out["story"] = pick_text(
        out.get("story"),
        *(s.get("stories") for s in sources),
        *(s.get("story") for s in sources),
    )
    # Keep structural fields from base; allow name/type/years/color upgrades if base empty
    for field in ("name", "type", "yearsActive", "color"):
        if not out.get(field):
            for s in sources:
                if s.get(field):
                    out[field] = s[field]
                    break
    # extents: prefer cleaned (passed as last alt with only extents), else longest rings
    best_ext = out.get("extentsByTick") or {}
    best_n = sum(
        len(json.dumps(v)) for v in (best_ext.values() if isinstance(best_ext, dict) else [])
    )
    for s in sources:
        ext = s.get("extentsByTick")
        if not isinstance(ext, dict) or not ext:
            continue
        n = sum(len(json.dumps(v)) for v in ext.values())
        if n > best_n:
            best_ext = deepcopy(ext)
            best_n = n
    out["extentsByTick"] = best_ext
    # Drop empty optional blobs
    if not out.get("images"):
        out.pop("images", None)
    keep_empty = ("description", "conflicts", "leaders", "religion", "culture")
    for field in list(out.keys()):
        if field in TEXT_FIELDS or field in (
            "ideas",
            "artIdeas",
            "artAndIdeas",
            "philosophy",
            "science",
        ):
            if not out.get(field) and field not in keep_empty:
                out.pop(field, None)
    return out


def merge_era(era: str, *, force_geo: bool = False) -> dict:
    site_path = SITE / f"{era}.json"
    base = load_json(site_path) or load_json(BASE_STORE / f"{era}.json")
    if not base:
        raise SystemExit(f"No base pack for {era} at {site_path} or store")

    pack_a = load_json(ENRICH / f"{era}-a.json")
    pack_b = load_json(ENRICH / f"{era}-b.json")
    cleaned = load_json(CLEANED / f"{era}.json")
    qa_path = CLEANED / "QA-REPORT.md"
    cleanup_path = CLEANED / "CLEANUP-REPORT.md"

    idx_a = polity_index(pack_a)
    idx_b = polity_index(pack_b)
    idx_clean = polity_index(cleaned)

    use_cleaned = bool(idx_clean) and (force_geo or qa_path.is_file() or cleanup_path.is_file())

    out = deepcopy(base)
    if pack_a and pack_a.get("narrative"):
        out["narrative"] = pick_text(out.get("narrative"), pack_a.get("narrative"), pack_b.get("narrative") if pack_b else None)
    elif pack_b and pack_b.get("narrative"):
        out["narrative"] = pick_text(out.get("narrative"), pack_b.get("narrative"))

    base_pols = out.get("polities")
    if not isinstance(base_pols, list):
        raise SystemExit(f"{era}: expected polities list on base pack")

    merged_pols = []
    stats = {
        "era": era,
        "base": len(base_pols),
        "a": len(idx_a),
        "b": len(idx_b),
        "cleaned": len(idx_clean),
        "usedCleanedGeo": use_cleaned,
        "enrichedStory": 0,
        "enrichedImages": 0,
        "longerDescription": 0,
    }

    for bp in base_pols:
        pid = bp.get("id")
        a = idx_a.get(pid)
        b = idx_b.get(pid)
        c = idx_clean.get(pid) if use_cleaned else None
        # cleaned may be geometry-only — merge extents via merge_polity sources order
        mp = merge_polity(bp, a or {}, b or {}, c or {})
        if use_cleaned and c is not None:
            # Empty cleaned extents = intentional elision (e.g. kalmar-union)
            mp["extentsByTick"] = deepcopy(c.get("extentsByTick") or {})
        if score_text(mp.get("story") or "")[0]:
            stats["enrichedStory"] += 1
        if mp.get("images"):
            stats["enrichedImages"] += 1
        if len(clean_prose(mp.get("description"))) > len(clean_prose(bp.get("description"))):
            stats["longerDescription"] += 1
        merged_pols.append(mp)

    # Optionally append new polities present only in A/B (with extents)
    known = {p["id"] for p in merged_pols}
    for src_idx in (idx_a, idx_b):
        for pid, p in src_idx.items():
            if pid in known:
                continue
            if not p.get("extentsByTick"):
                continue
            merged_pols.append(merge_polity(p, idx_clean.get(pid) or {}))
            known.add(pid)
            stats.setdefault("addedPolities", 0)
            stats["addedPolities"] += 1

    out["polities"] = merged_pols
    stats["out"] = len(merged_pols)
    stats["sources"] = {
        "a": bool(pack_a),
        "b": bool(pack_b),
        "cleaned": bool(cleaned),
        "qaReport": qa_path.is_file(),
        "cleanupReport": cleanup_path.is_file(),
    }
    return out, stats


def write_report(era: str, stats: dict) -> Path:
    path = ENRICH / f"merge-{era}.md"
    lines = [
        f"# Merge report — {era}",
        "",
        f"UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "```json",
        json.dumps(stats, indent=2),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def update_status(era: str, stats: dict) -> None:
    status = ENRICH / "STATUS.md"
    # Rewrite table row for this era
    a = "yes" if stats["sources"]["a"] else "—"
    b = "yes" if stats["sources"]["b"] else "—"
    cleaned = "yes" if stats["sources"]["cleaned"] else "—"
    qa = "yes" if stats["sources"]["qaReport"] else "—"
    merged = f"yes ({stats['out']} polities)"
    row = f"| {era} | {a} | {b} | {cleaned} | {qa} | {merged} | pending deploy |"
    if not status.is_file():
        return
    text = status.read_text(encoding="utf-8")
    pattern = re.compile(rf"^\| {re.escape(era)} \|.*$", re.M)
    if pattern.search(text):
        text = pattern.sub(row, text)
    else:
        text = text.rstrip() + "\n" + row + "\n"
    status.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--era", choices=ERAS, required=True)
    ap.add_argument(
        "--force-geo",
        action="store_true",
        help="Use cleaned extents even if QA/CLEANUP report missing",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ENRICH.mkdir(parents=True, exist_ok=True)
    out, stats = merge_era(args.era, force_geo=args.force_geo)
    site_path = SITE / f"{args.era}.json"
    report = write_report(args.era, stats)
    update_status(args.era, stats)

    if args.dry_run:
        print(json.dumps(stats, indent=2))
        print(f"dry-run: would write {site_path}")
        print(f"report: {report}")
        return

    site_path.parent.mkdir(parents=True, exist_ok=True)
    with site_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(stats, indent=2))
    print(f"wrote {site_path}")
    print(f"report {report}")


if __name__ == "__main__":
    main()
