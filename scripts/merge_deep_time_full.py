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
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TIMELINE = REPO / "data" / "timeline.json"
FULL_DIR = Path("/cursor/stores/self/internal/deep-time-enrichment/full")
ALT_FULL = Path(
    "/cursor/stores/bc-01a121f3-4d13-797d-989d-162d7e4b69e1/internal/deep-time-enrichment/full"
)
COMMONS_CACHE = FULL_DIR / "_commons-resolve-cache.json"
UA = "EuropaStrataBot/1.0 (https://github.com/nmpy7knjd8-code/europa-strata; deep-time enrichment)"
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".tif", ".tiff")

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


_commons_cache: dict[str, str | None] | None = None
_commons_lock = threading.Lock()


def load_commons_cache() -> dict[str, str | None]:
    global _commons_cache
    if _commons_cache is not None:
        return _commons_cache
    data = load_json(COMMONS_CACHE) or {}
    _commons_cache = {str(k): v for k, v in data.items()}
    return _commons_cache


def save_commons_cache() -> None:
    if _commons_cache is None:
        return
    COMMONS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with _commons_lock:
        snapshot = dict(_commons_cache)
    with COMMONS_CACHE.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
        f.write("\n")


def commons_file_url(name: str, width: int = 960) -> str:
    name = name.strip()
    name = re.sub(r"^File:", "", name, flags=re.I)
    name = name.replace("_", " ")
    enc = urllib.parse.quote(name, safe="")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def _looks_like_file_title(s: str) -> bool:
    t = s.strip()
    if t.startswith("File:"):
        return True
    low = t.lower()
    return low.endswith(IMG_EXT)


def _commons_api_search(query: str, limit: int = 5) -> list[str]:
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": limit,
            "format": "json",
        }
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    hits = data.get("query", {}).get("search") or []
    return [h.get("title") or "" for h in hits if h.get("title")]


def _pick_image_title(titles: list[str]) -> str | None:
    preferred = []
    for t in titles:
        low = t.lower()
        if low.endswith(".pdf") or low.endswith(".djvu"):
            continue
        if any(low.endswith(ext) for ext in IMG_EXT):
            preferred.append(t)
    return (preferred or titles or [None])[0]


def resolve_commons_query(query: str) -> str | None:
    """Resolve a File: title or free-text Commons idea to a Special:FilePath URL."""
    q = (query or "").strip()
    if not q:
        return None
    if q.startswith("http://") or q.startswith("https://"):
        return q
    cache = load_commons_cache()
    with _commons_lock:
        if q in cache and cache[q]:
            return cache[q]
        # Cached misses (None) are retried — free-text ideas often need shorter queries
    if _looks_like_file_title(q):
        url = commons_file_url(q)
        with _commons_lock:
            cache[q] = url
            n = len(cache)
        if n % 25 == 0:
            save_commons_cache()
        return url

    # Progressive search — long idea strings often miss; shorter tokens hit.
    STOP = {
        "reconstruction",
        "excavation",
        "historic",
        "landscape",
        "region",
        "overlay",
        "zone",
        "site",
        "or",
        "and",
        "the",
        "from",
        "with",
        "late",
        "early",
        "period",
        "age",
        "art",
        "map",
        "plan",
        "why",
    }
    trimmed = re.split(r"\s+[—–-]\s+", q)[0].strip()
    words = re.findall(r"[A-Za-zÀ-ÿ0-9’']+", trimmed or q)
    content = [w for w in words if w.lower() not in STOP]
    candidates = []
    if trimmed:
        candidates.append(trimmed)
    if len(content) >= 4:
        candidates.append(" ".join(content[:4]))
    if len(content) >= 3:
        candidates.append(" ".join(content[:3]))
    if len(content) >= 2:
        candidates.append(" ".join(content[:2]))
    if content:
        candidates.append(content[0])
    # Also try without trailing geography after "or"
    if " or " in (trimmed or "").lower():
        candidates.insert(1, re.split(r"\s+or\s+", trimmed, flags=re.I)[0].strip())
    seen_c = set()
    uniq = []
    for c in candidates:
        cl = c.lower()
        if c and cl not in seen_c:
            seen_c.add(cl)
            uniq.append(c)

    file_title = None
    for cand in uniq[:4]:
        time.sleep(0.03)
        hits = _commons_api_search(cand)
        file_title = _pick_image_title(hits)
        if file_title:
            break

    url = commons_file_url(file_title) if file_title else None
    with _commons_lock:
        cache[q] = url
        n = len(cache)
    if n % 15 == 0:
        save_commons_cache()
    return url


def collect_commons_queries(pack: dict) -> list[str]:
    found: list[str] = []

    def add_images(images):
        for im in images or []:
            if isinstance(im, dict):
                for key in ("commons", "file", "title", "name", "src", "url"):
                    v = im.get(key)
                    if isinstance(v, str) and v.strip():
                        found.append(v.strip())
                        break
            elif isinstance(im, str) and im.strip():
                found.append(im.strip())

    for rid, by_period in (pack.get("regions") or {}).items():
        if not isinstance(by_period, dict):
            continue
        for pid, fields in by_period.items():
            if isinstance(fields, dict):
                add_images(fields.get("images"))
                add_images(fields.get("imageIdeas") or fields.get("image_ideas"))
            elif any(
                k in by_period for k in ("images", "imageIdeas", "description", "art")
            ):
                add_images(by_period.get("images"))
                break
    for pid, body in (pack.get("periods") or {}).items():
        if not isinstance(body, dict):
            continue
        for bucket in ("regions", "polities", "layers"):
            for _k, fields in (body.get(bucket) or {}).items():
                if isinstance(fields, dict):
                    add_images(fields.get("images"))
                    add_images(fields.get("imageIdeas") or fields.get("image_ideas"))
    # unique preserve order
    seen = set()
    out = []
    for q in found:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def prefetch_commons(queries: list[str], workers: int = 6) -> dict:
    cache = load_commons_cache()
    pending = [q for q in queries if q not in cache]
    stats = {"total": len(queries), "pending": len(pending), "workers": workers}
    if not pending:
        stats["resolved"] = sum(1 for q in queries if cache.get(q))
        return stats

    def one(q: str):
        return q, resolve_commons_query(q)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(one, q) for q in pending]
        done = 0
        for fut in as_completed(futs):
            fut.result()
            done += 1
            if done % 40 == 0:
                save_commons_cache()
                print(
                    json.dumps({"prefetchProgress": done, "of": len(pending)}),
                    flush=True,
                )
    save_commons_cache()
    cache = load_commons_cache()
    stats["resolved"] = sum(1 for q in queries if cache.get(q))
    stats["failed"] = sum(1 for q in queries if q in cache and not cache.get(q))
    return stats


def resolve_image_idea(idea) -> dict | None:
    if isinstance(idea, dict):
        src = (idea.get("src") or idea.get("url") or "").strip()
        caption = (idea.get("caption") or "").strip()
        alt = (idea.get("alt") or caption).strip()
        role = (idea.get("role") or "").strip().lower()
        if not src:
            file_name = (
                idea.get("file")
                or idea.get("commons")
                or idea.get("title")
                or idea.get("name")
                or ""
            )
            src = resolve_commons_query(str(file_name)) or ""
        if not src:
            return None
        out = {"src": src, "caption": caption, "alt": alt}
        if role:
            out["role"] = role
        return out
    if not isinstance(idea, str):
        return None
    s = idea.strip()
    if not s:
        return None
    src = resolve_commons_query(s)
    if not src:
        return None
    cap = re.sub(r"^File:", "", s, flags=re.I).strip()
    return {"src": src, "caption": cap, "alt": cap}


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

    # Short horizon label vs long culture prose
    label = src.get("cultureLabel") or src.get("label")
    if isinstance(label, str) and label.strip():
        target["cultureLabel"] = label.strip()
    elif isinstance(src.get("name"), str) and src["name"].strip() and len(src["name"].strip()) <= 80:
        target.setdefault("cultureLabel", src["name"].strip())
    if isinstance(src.get("name"), str) and src["name"].strip():
        if not target.get("name") or len(src["name"]) >= len(str(target.get("name") or "")):
            target["name"] = src["name"].strip()

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


def iso_to_region_map(region_countries: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for rid, isos in (region_countries or {}).items():
        for iso in isos or []:
            out[str(iso)] = rid
    return out


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
    iso_region = iso_to_region_map(region_countries)
    stats = {
        "regions": 0,
        "polities": 0,
        "layers": 0,
        "fields": 0,
        "stories": 0,
        "images": 0,
        "missingPeriods": [],
        "missingLayers": [],
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
            pol = pols.setdefault(iso, {})
            st2 = apply_slice(pol, fields)
            stats["polities"] += 1
            stats["fields"] += st2["fields"]

    # Optional layer / polity overlays (iron-classical shape)
    for pid, body in (pack.get("periods") or {}).items():
        period = periods_by_id.get(pid)
        if not period or not isinstance(body, dict):
            continue
        for lid, fields in (body.get("layers") or {}).items():
            if not isinstance(fields, dict):
                continue
            layer = next(
                (
                    l
                    for l in (period.get("mapLayers") or [])
                    if (l.get("id") or "").strip() == str(lid).strip()
                ),
                None,
            )
            if not layer:
                stats["missingLayers"].append(f"{pid}:{lid}")
                continue
            st = apply_slice(layer, fields)
            stats["layers"] += 1
            stats["fields"] += st["fields"]
            stats["stories"] += st["stories"]
            stats["images"] += st["images"]
        for iso, fields in (body.get("polities") or {}).items():
            if not isinstance(fields, dict):
                continue
            pols = period.setdefault("polities", {})
            if not isinstance(pols, dict):
                continue
            pol = pols.setdefault(iso, {})
            st = apply_slice(pol, fields)
            stats["polities"] += 1
            stats["fields"] += st["fields"]
            stats["stories"] += st["stories"]
            stats["images"] += st["images"]
            # Roll richest polity prose onto atlas region for region-click panels
            rid = iso_region.get(iso)
            if rid:
                if not isinstance(period.get("regions"), dict):
                    period["regions"] = {}
                reg = period["regions"].setdefault(rid, {})
                st_r = apply_slice(reg, fields)
                stats["regions"] += 1
                stats["fields"] += st_r["fields"]

    stats["missingPeriods"] = sorted(set(stats["missingPeriods"]))
    stats["missingLayers"] = sorted(set(stats["missingLayers"]))
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
    ap.add_argument(
        "--workers",
        type=int,
        default=6,
        help="Parallel Commons resolvers for free-text image ideas",
    )
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

    # Prefetch Commons URLs up front (parallel) so merge is CPU/IO local
    all_queries: list[str] = []
    loaded_packs = []
    for path in packs:
        pack = load_json(path)
        if not pack:
            continue
        loaded_packs.append((path, pack))
        all_queries.extend(collect_commons_queries(pack))
    # unique
    seen_q = set()
    uniq_q = []
    for q in all_queries:
        if q not in seen_q:
            seen_q.add(q)
            uniq_q.append(q)
    prefetch_stats = prefetch_commons(uniq_q, workers=max(1, args.workers))
    print(json.dumps({"prefetch": prefetch_stats}, indent=2), flush=True)

    report = {"packs": [], "prefetch": prefetch_stats}
    for path, pack in loaded_packs:
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
        save_commons_cache()
        report["commonsCache"] = str(COMMONS_CACHE)
        cache = load_commons_cache()
        resolved = sum(1 for v in cache.values() if v)
        report["commonsResolved"] = resolved
        report["commonsFailed"] = sum(1 for v in cache.values() if not v)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
