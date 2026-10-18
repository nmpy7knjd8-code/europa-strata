#!/usr/bin/env python3
"""Check that every Wikimedia Commons image referenced in data/ exists.

Scans every data/**/*.json for image "src" URLs of the form
  https://commons.wikimedia.org/wiki/Special:FilePath/<File name>?width=...
and asks the Commons API (50 titles per request) whether each file exists,
following normalisation and file redirects.

Usage:
    python3 scripts/check_images.py              # summary + missing list, exit 1 if any missing
    python3 scripts/check_images.py --json out.json   # also write a machine-readable report
    python3 scripts/check_images.py --quiet      # summary only

Exit codes: 0 = all files exist, 1 = missing files found, 2 = API/network error.
"""
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = "https://commons.wikimedia.org/w/api.php"
PREFIX = "https://commons.wikimedia.org/wiki/Special:FilePath/"
UA = "EuropaStrataImageCheck/1.0 (https://github.com/nmpy7knjd8-code/europa-strata)"


def filename_from_src(src):
    """'.../Special:FilePath/Foo%20bar.jpg?width=800' -> 'Foo bar.jpg' (or None)."""
    if not isinstance(src, str) or not src.startswith(PREFIX):
        return None
    name = src[len(PREFIX):].split("?", 1)[0].split("#", 1)[0]
    return urllib.parse.unquote(name).replace("_", " ").strip()


def iter_image_srcs(node, path=""):
    """Yield (json_path, src) for every image src under node."""
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            if k == "src" and isinstance(v, str):
                yield p, v
            else:
                yield from iter_image_srcs(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_image_srcs(v, f"{path}[{i}]")


def collect(root=ROOT):
    """Return {filename: [(relative json file, json path), ...]}."""
    refs = {}
    for f in sorted((root / "data").rglob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for p, src in iter_image_srcs(data):
            name = filename_from_src(src)
            if name:
                refs.setdefault(name, []).append((str(f.relative_to(root)), p))
    return refs


def api_get(params, retries=4):
    q = urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def existing_files(names, delay=0.1):
    """Return the subset of names (plain 'Foo bar.jpg') that exist on Commons."""
    names = list(names)
    exists = set()
    for i in range(0, len(names), 50):
        chunk = names[i : i + 50]
        d = api_get({"action": "query", "titles": "|".join("File:" + n for n in chunk), "redirects": 1})
        q = d.get("query", {})
        # map requested title -> final title through normalisation and redirects
        fwd = {}
        for key in ("normalized", "redirects"):
            for m in q.get(key, []):
                fwd[m["from"]] = m["to"]
        ok_titles = {
            p["title"]
            for p in q.get("pages", [])
            if not p.get("missing") and not p.get("invalid") or p.get("known")
        }
        for n in chunk:
            t = "File:" + n
            seen = set()
            while t in fwd and t not in seen:
                seen.add(t)
                t = fwd[t]
            if t in ok_titles:
                exists.add(n)
        time.sleep(delay)
    return exists


def main(argv):
    quiet = "--quiet" in argv
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    refs = collect()
    try:
        ok = existing_files(refs)
    except Exception as e:  # network / API failure
        print(f"error: could not query Commons API: {e}", file=sys.stderr)
        return 2
    missing = sorted(n for n in refs if n not in ok)
    n_refs = sum(len(v) for v in refs.values())
    n_missing_refs = sum(len(refs[n]) for n in missing)
    print(f"{len(refs)} unique Commons files in {n_refs} references; "
          f"{len(missing)} missing ({n_missing_refs} references)")
    if missing and not quiet:
        for n in missing:
            files = sorted({f for f, _ in refs[n]})
            print(f"  MISSING  {n}  ({len(refs[n])}x in {', '.join(files)})")
    if out_json:
        pathlib.Path(out_json).write_text(
            json.dumps({"missing": {n: refs[n] for n in missing}, "checked": len(refs)}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
