#!/usr/bin/env python3
"""Merge deep-time full enrichment packs into timeline.json region panels.

Watches:
  /cursor/stores/self/internal/deep-time-enrichment/full/
    neolithic-full.json
    bronze-full.json
    iron-classical-full.json
    migration-full.json

Pack shape (region-keyed, same spirit as culture-fill + kingdom enrichment):
{
  "packId": "neolithic-full",
  "periodIds": ["mesolithic", "early-neolithic", "middle-neolithic"],
  "regionIds": ["iberia", "britain", ...],
  "regions": {
    "italy": {
      "middle-neolithic": {
        "description": "long prose…",
        "culture": "…",
        "art": "…", "ideas": "…", "philosophy": "…", "science": "…",
        "leaders": "…", "religion": "…", "literature": "…", "conflicts": "…",
        "stories": [{"title": "…", "text": "…"}],
        "images": [{"src": "https://…", "caption": "…", "role": "art"}],
        "imageIdeas": ["File:Diana_ware.jpg", "Serra d'Alto pottery"]
      }
    }
  }
}

Also accepts period-keyed packs: periods.{periodId}.regions.{regionId}
and polity/layer overlays like culture-fill period packs.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import urllib.parse
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TIMELINE = REPO / "data" / "timeline.json"
FULL_DIR = Path("/cursor/stores/self/internal/deep-time-enrichment/full")
ALT_FULL = Path(
    "/cursor/stores/bc-01a121f3-4d13-797d-989d-162d7e4b69e1/internal/deep-time-enrichment/full"
)

PACK_FILES = (
    "neolithic-full.json",
    "bronze-full.json",
    "iron-classical-full.json",
    "migration-full.json",
)

TEXT_FIELDS = (
    "description",
    "summary",
    "narrative",
    "culture",
    "art",
    "ideas",
    "philosophy",
    "science",
    "leaders",
    "religion",
    "literature",
    "conflicts",
)

STORY_KEYS = ("stories", "story", "vignettes", "turningPoints", "turning_points")


def load_json(path: Path):
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def commons_file_url(name: str, width: int = 960) -> str:
    name = name.strip()
    name = re.sub(r"^File:", "", name, flags=re.I)
    name = name.replace("_", " ")
    enc = urllib.parse.quote(name, safe="")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def resolve_image_idea(idea) -> dict | None:
    if isinstance(idea, dict):
        src = (idea.get("src") or idea.get("url") or "").strip()
        if not src:
            file_name = idea.get("file") or idea.get("commons") or idea.get("title")
            if file_name and (
                str(file_name).startswith("File:")
                or str(file_name).lower().endswith(
                    (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".tif", ".tiff")
                )
            ):
                src = commons_file_url(str(file_name))
            else:
                return None
        return {
            "src": src,
            "caption": (idea.get("caption") or "").strip(),
            "alt": (idea.get("alt") or idea.get("caption") or "").strip(),
            **(
                {"role": (idea.get("role") or "").strip().lower()}
                if idea.get("role")
                else {}
            ),
        }
    if not isinstance(idea, str):
        return None
    s = idea.strip()
    if not s:
        return None
    if s.startswith("http://") or s.startswith("https://"):
        return {"src": s, "caption": "", "alt": ""}
    if s.startswith("File:") or s.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".tif", ".tiff")
    ):
        return {"src": commons_file_url(s), "caption": s.replace("File:", ""), "alt": ""}
    return None


def normalize_images(images, image_ideas=None) -> list:
    out = []
    seen = set()
    for img in images or []:
        resolved = resolve_image_idea(img)
        if not resolved or resolved["src"] in seen:
            continue
        seen.add(resolved["src"])
        out.append(resolved)
    for idea in image_ideas or []:
        resolved = resolve_image_idea(idea)
        if not resolved or resolved["src"] in seen:
            continue
        seen.add(resolved["src"])
        out.append(resolved)
    return out


def parse_stringified_stories(raw: str):
    s = raw.strip()
    if not s.startswith("["):
        return None
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass
    return None


def coerce_stories(value) -> list[dict]:
    if value is None:
        return []
    if isinstance(value, str):
        t = value.strip()
        if not t:
            return []
        parsed = parse_stringified_stories(t)
        if parsed is not None:
            return coerce_stories(parsed)
        return [{"text": t}]
    if isinstance(value, dict):
        title = str(value.get("title") or value.get("name") or "").strip()
        text = str(
            value.get("text")
            or value.get("body")
            or value.get("narrative")
            or value.get("description")
            or ""
        ).strip()
        if not title and not text:
            return []
        entry = {"text": text}
        if title:
            entry["title"] = title
        return [entry]
    if isinstance(value, list):
        out = []
        seen = set()
        for item in value:
            for piece in coerce_stories(item):
                key = (piece.get("title") or "", piece.get("text") or "")
                if key in seen or (not key[0] and not key[1]):
                    continue
                seen.add(key)
                out.append(piece)
        return out
    return []


def pick_text(*candidates: str | None) -> str:
    best = ""
    for c in candidates:
        if not isinstance(c, str):
            continue
        t = c.strip()
        if len(t) > len(best):
            best = t
    return best


def merge_stories(*candidates) -> list[dict] | None:
    best: list[dict] = []
    best_score = -1
    for c in candidates:
        items = coerce_stories(c)
        score = sum(len(i.get("text") or "") + len(i.get("title") or "") for i in items)
        if score > best_score:
            best_score = score
            best = items
    return best or None


def apply_slice(target: dict, src: dict, *, overwrite_longer: bool = True) -> dict:
    """Merge one enrichment slice onto a region/polity/layer dict."""
    stats = {"fields": 0, "stories": 0, "images": 0}
    if not isinstance(src, dict) or not isinstance(target, dict):
        return stats
    for field in TEXT_FIELDS:
        incoming = src.get(field)
        if not isinstance(incoming, str) or not incoming.strip():
            continue
        cur = target.get(field) if isinstance(target.get(field), str) else ""
        if overwrite_longer:
            if len(incoming.strip()) >= len((cur or "").strip()):
                target[field] = incoming.strip()
                stats["fields"] += 1
        elif not (cur or "").strip():
            target[field] = incoming.strip()
            stats["fields"] += 1

    stories = merge_stories(*(src.get(k) for k in STORY_KEYS), target.get("stories"), target.get("story"))
    if stories:
        target["stories"] = stories
        target["story"] = stories  # app accepts either
        stats["stories"] = len(stories)

    images = normalize_images(src.get("images") or src.get("photos"), src.get("imageIdeas") or src.get("image_ideas"))
    if images:
        existing = normalize_images(target.get("images"))
        merged = normalize_images(existing + images)
        target["images"] = merged
        stats["images"] = len(merged)
    return stats


def iter_region_slices(pack: dict):
    """Yield (periodId, regionId, fields)."""
    regions = pack.get("regions") or {}
    # Shape A: regions.{rid}.{pid}
    for rid, by_period in regions.items():
        if not isinstance(by_period, dict):
            continue
        # detect period-keyed vs field-keyed
        if any(k in TEXT_FIELDS or k in STORY_KEYS or k in ("images", "imageIdeas") for k in by_period):
            # flat fields with pack.periodIds
            for pid in pack.get("periodIds") or []:
                yield pid, rid, by_period
        else:
            for pid, fields in by_period.items():
                if isinstance(fields, dict):
                    yield pid, rid, fields
    # Shape B: periods.{pid}.regions.{rid}
    for pid, body in (pack.get("periods") or {}).items():
        if not isinstance(body, dict):
            continue
        for rid, fields in (body.get("regions") or {}).items():
            if isinstance(fields, dict):
                yield pid, rid, fields


def merge_pack(timeline: dict, pack: dict) -> dict:
    periods_by_id = {p["id"]: p for p in timeline["periods"]}
    region_countries = timeline.get("meta", {}).get("regionCountries") or {}
    stats = {
        "regions": 0,
        "polities": 0,
        "layers": 0,
        "fields": 0,
        "stories": 0,
        "images": 0,
        "missingPeriods": [],
    }

    for pid, rid, fields in iter_region_slices(pack):
        period = periods_by_id.get(pid)
        if not period:
            stats["missingPeriods"].append(pid)
            continue
        if not isinstance(period.get("regions"), dict):
            period["regions"] = {}
        reg = period["regions"].setdefault(rid, {})
        st = apply_slice(reg, fields)
        stats["regions"] += 1
        stats["fields"] += st["fields"]
        stats["stories"] += st["stories"]
        stats["images"] += st["images"]
        # Mirror onto ISO polities in this atlas region when present
        for iso in region_countries.get(rid) or []:
            pols = period.setdefault("polities", {})
            if not isinstance(pols, dict):
                continue
            pol = pols.get(iso)
            if not isinstance(pol, dict):
                continue
            st2 = apply_slice(pol, fields)
            stats["polities"] += 1
            stats["fields"] += st2["fields"]

    # Optional layer overlays
    for pid, body in (pack.get("periods") or {}).items():
        period = periods_by_id.get(pid)
        if not period or not isinstance(body, dict):
            continue
        for lid, fields in (body.get("layers") or {}).items():
            if not isinstance(fields, dict):
                continue
            layer = next(
                (l for l in (period.get("mapLayers") or []) if (l.get("id") or "").strip() == lid.strip()),
                None,
            )
            if not layer:
                continue
            st = apply_slice(layer, fields)
            stats["layers"] += 1
            stats["fields"] += st["fields"]
        for iso, fields in (body.get("polities") or {}).items():
            if not isinstance(fields, dict):
                continue
            pol = (period.get("polities") or {}).get(iso)
            if not isinstance(pol, dict):
                continue
            st = apply_slice(pol, fields)
            stats["polities"] += 1
            stats["fields"] += st["fields"]

    stats["missingPeriods"] = sorted(set(stats["missingPeriods"]))
    return stats


def find_packs(explicit: list[Path] | None = None) -> list[Path]:
    if explicit:
        return [p for p in explicit if p.is_file()]
    found = []
    for name in PACK_FILES:
        for root in (FULL_DIR, ALT_FULL):
            path = root / name
            if path.is_file() and path not in found:
                found.append(path)
                break
    # Also pick up any *-full.json dropped in either dir
    for root in (FULL_DIR, ALT_FULL):
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*-full.json")):
            if path not in found:
                found.append(path)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack", action="append", type=Path, help="Explicit pack path(s)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    packs = find_packs(args.pack)
    if not packs:
        print(
            json.dumps(
                {
                    "ok": True,
                    "merged": 0,
                    "message": f"No *-full.json packs yet under {FULL_DIR}",
                    "watched": PACK_FILES,
                },
                indent=2,
            )
        )
        return 0

    timeline = load_json(TIMELINE)
    if not timeline:
        raise SystemExit(f"Missing {TIMELINE}")

    report = {"packs": []}
    for path in packs:
        pack = load_json(path)
        if not pack:
            continue
        before = deepcopy(timeline)
        stats = merge_pack(timeline, pack)
        report["packs"].append({"path": str(path), "packId": pack.get("packId"), **stats})
        if args.dry_run:
            timeline = before

    if not args.dry_run:
        with TIMELINE.open("w", encoding="utf-8") as f:
            json.dump(timeline, f, ensure_ascii=False, indent=2)
            f.write("\n")
        report["wrote"] = str(TIMELINE)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
