#!/usr/bin/env python3
"""Flag Commons images reused across 3+ polities in data/kingdom-eras/*.json.

A reuse is OK only on the polities listed for that file in scripts/image_homes.json.
Exit 1 on any unapproved reuse. --fix drops the image from the unapproved polities.
"""
import json, glob, sys, collections, urllib.parse

HOMES = {k: set(v) for k, v in json.load(open("scripts/image_homes.json")).items() if not k.startswith("_")}

def fname(src):
    return urllib.parse.unquote(src.split("?")[0].split("FilePath/")[-1])

def main():
    fix = "--fix" in sys.argv
    files = {f: json.load(open(f)) for f in sorted(glob.glob("data/kingdom-eras/*.json"))}
    use = collections.defaultdict(set)
    for f, d in files.items():
        for q in (d.get("polities") if isinstance(d, dict) else None) or []:
            for im in q.get("images") or []:
                use[fname(im.get("src", ""))].add((f, q["id"]))
    bad = []
    for name, owners in use.items():
        if len(owners) < 3:
            continue
        ok = HOMES.get(name, set())
        bad += [(name, f, pid) for f, pid in owners if pid not in ok]
    for name, f, pid in sorted(bad):
        print(f"unrelated reuse: {name} on {f.split('/')[-1]}:{pid}")
    if fix and bad:
        drop = {(f, pid, n) for n, f, pid in bad}
        for f, d in files.items():
            changed = False
            for q in d.get("polities") or []:
                ims = q.get("images") or []
                keep = [im for im in ims if (f, q["id"], fname(im.get("src", ""))) not in drop]
                if len(keep) != len(ims):
                    q["images"] = keep; changed = True
            if changed:
                raw = open(f).read()
                indent = 2 if raw.startswith("{\n  ") else None
                json.dump(d, open(f, "w"), ensure_ascii=False, indent=indent)
                if raw.endswith("\n"): open(f, "a").write("\n")
        print(f"dropped {len(bad)}")
        return 0
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
