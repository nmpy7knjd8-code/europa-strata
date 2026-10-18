#!/usr/bin/env python3
"""Repair or remove Commons image references that point at files that do not exist.

One-off companion to scripts/check_images.py. For every missing file it looks for a
replacement it can match with confidence, and otherwise removes the image entry:

  1. Extension / case variants of the same name (.jpg <-> .JPG <-> .jpeg, .png, .tif ...).
  2. A Commons file search on the name; a hit is accepted only when its name is the same
     after normalisation (accents stripped, case folded, punctuation/spaces removed,
     extension ignored). No fuzzy or "looks similar" matches.

Everything else is removed from its "images" list (an emptied list is dropped so the app
falls back to other images, as it did when the broken figure removed itself).

Usage:
    python3 scripts/fix_missing_images.py --dry-run   # report only
    python3 scripts/fix_missing_images.py             # rewrite data/*.json in place
    python3 scripts/fix_missing_images.py --report scripts/image_fix_report.json
    python3 scripts/fix_missing_images.py --from-report scripts/image_fix_report.json  # re-apply a saved plan
"""
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_images import PREFIX, ROOT, api_get, collect, existing_files, filename_from_src  # noqa: E402

# SVGs are left out on purpose: a same-named .svg is usually a diagram or emblem, not the
# photograph or painting the caption describes.
EXTS = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".tif", ".tiff", ".gif", ".webp"]


def split_ext(name):
    m = re.match(r"^(.*?)(\.[A-Za-z0-9]{2,5})$", name)
    return (m.group(1), m.group(2)) if m else (name, "")


def norm(name):
    stem, _ = split_ext(name)
    s = unicodedata.normalize("NFKD", stem)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.casefold())


def variant_candidates(name):
    stem, ext = split_ext(name)
    out = []
    for e in EXTS:
        if e != ext:
            out.append(stem + e)
    if stem and stem[0].islower():
        out.append(stem[0].upper() + stem[1:] + ext)
    return out


def search_match(name):
    stem, _ = split_ext(name)
    key = norm(name)
    if len(key) < 6:
        return None
    d = api_get({"action": "query", "list": "search", "srnamespace": 6, "srsearch": stem, "srlimit": 20})
    hits = [h["title"][5:] for h in d.get("query", {}).get("search", []) if h["title"].startswith("File:")]
    exact = [h for h in hits if norm(h) == key and not h.lower().endswith(".svg")]
    # Only accept a single unambiguous match (prefer raster images when both svg and jpg exist)
    if len(exact) == 1:
        return exact[0]
    raster = [h for h in exact if split_ext(h)[1].lower() in (".jpg", ".jpeg", ".png", ".tif", ".tiff")]
    return raster[0] if len(raster) == 1 else None


def make_src(old_src, new_name):
    query = old_src.split("?", 1)[1] if "?" in old_src else ""
    enc = urllib.parse.quote(new_name.replace(" ", " "), safe="(),'!-._~")
    return PREFIX + enc + (("?" + query) if query else "")


def find_fixes(missing):
    fixes = {}
    # 1. extension/case variants, checked in bulk
    cand = {}
    for n in missing:
        for c in variant_candidates(n):
            cand.setdefault(c, []).append(n)
    ok = existing_files(cand)
    for c in sorted(ok):
        for n in cand[c]:
            fixes.setdefault(n, (c, "variant"))
    # 2. normalised-name search
    rest = [n for n in missing if n not in fixes]
    for i, n in enumerate(rest):
        try:
            hit = search_match(n)
        except Exception as e:
            print(f"  search failed for {n}: {e}", file=sys.stderr)
            hit = None
        if hit and hit != n:
            fixes[n] = (hit, "search")
        time.sleep(0.1)
        if (i + 1) % 100 == 0:
            print(f"  searched {i + 1}/{len(rest)}", file=sys.stderr)
    # double-check every replacement really exists
    good = existing_files({v[0] for v in fixes.values()})
    return {n: v for n, v in fixes.items() if v[0] in good}


def dump(path, data, raw):
    if raw.lstrip().startswith("{\n") or "\n  " in raw[:200]:
        text = json.dumps(data, indent=2, ensure_ascii=False, separators=(",", ": "))
    else:
        text = json.dumps(data, ensure_ascii=False)
    path.write_text(text + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")


def apply(missing, fixes):
    stats = {"fixed_refs": 0, "removed_refs": 0, "emptied_lists": 0}

    def walk(node):
        if isinstance(node, dict):
            for k in list(node.keys()):
                v = node[k]
                if k == "images" and isinstance(v, list):
                    keep = []
                    for img in v:
                        n = filename_from_src(img.get("src")) if isinstance(img, dict) else None
                        if n in fixes:
                            img["src"] = make_src(img["src"], fixes[n][0])
                            stats["fixed_refs"] += 1
                            keep.append(img)
                        elif n in missing:
                            stats["removed_refs"] += 1
                        else:
                            keep.append(img)
                    if keep:
                        node[k] = keep
                    else:
                        del node[k]
                        stats["emptied_lists"] += 1
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for f in sorted((ROOT / "data").rglob("*.json")):
        raw = f.read_text(encoding="utf-8")
        if "Special:FilePath" not in raw:
            continue
        data = json.loads(raw)
        before = json.dumps(data, sort_keys=True)
        walk(data)
        if json.dumps(data, sort_keys=True) != before:
            dump(f, data, raw)
    return stats


def main(argv):
    dry = "--dry-run" in argv
    report = argv[argv.index("--report") + 1] if "--report" in argv else None
    refs = collect()
    ok = existing_files(refs)
    missing = {n for n in refs if n not in ok}
    print(f"{len(missing)} missing files ({sum(len(refs[n]) for n in missing)} references)")
    if "--from-report" in argv:
        saved = json.loads(pathlib.Path(argv[argv.index("--from-report") + 1]).read_text(encoding="utf-8"))
        fixes = {n: (v["replacement"], v["method"]) for n, v in saved["fixed"].items()
                 if n in missing and not v["replacement"].lower().endswith(".svg")}
        good = existing_files({v[0] for v in fixes.values()})
        fixes = {n: v for n, v in fixes.items() if v[0] in good}
    else:
        fixes = find_fixes(sorted(missing))
    removed = sorted(missing - set(fixes))
    print(f"fixable: {len(fixes)} files ({sum(len(refs[n]) for n in fixes)} refs); "
          f"to remove: {len(removed)} files ({sum(len(refs[n]) for n in removed)} refs)")
    if report:
        pathlib.Path(report).write_text(json.dumps({
            "fixed": {n: {"replacement": v[0], "method": v[1], "refs": len(refs[n])} for n, v in sorted(fixes.items())},
            "removed": {n: len(refs[n]) for n in removed},
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not dry:
        print(apply(missing, fixes))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
