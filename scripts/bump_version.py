#!/usr/bin/env python3
"""Bump the site's build string everywhere it appears, in one pass.

Updates, in every top-level *.html file:
  * <meta name="build" content="...">   (app.js / ancestry.js read this for data fetches)
  * every ?v=... cache-busting tag on a local href/src (CSS, JS, manifest, icons)

Usage:
    python3 scripts/bump_version.py <new-build>        # e.g. load-guard-1
    python3 scripts/bump_version.py <new-build> --dry-run
    python3 scripts/bump_version.py --show             # print current build strings

Exits non-zero if the build string is invalid or nothing was updated.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VALID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
META_RE = re.compile(r'(<meta\s+name="build"\s+content=")([^"]*)(")')
# ?v=<token> inside a local href/src attribute (not absolute http(s) URLs)
VTAG_RE = re.compile(r'((?:href|src)="(?!https?:|//)[^"?]+\?(?:[^"]*&)?v=)([^"&]*)')


def html_files():
    return sorted(ROOT.glob("*.html"))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    if argv[0] == "--show":
        for f in html_files():
            s = f.read_text(encoding="utf-8")
            metas = {m.group(2) for m in META_RE.finditer(s)}
            tags = {m.group(2) for m in VTAG_RE.finditer(s)}
            print(f"{f.name}: build={sorted(metas)} v={sorted(tags)}")
        return 0
    new = argv[0]
    dry = "--dry-run" in argv[1:]
    if not VALID.match(new):
        print(f"invalid build string: {new!r} (use letters, digits, . _ -)", file=sys.stderr)
        return 2
    total = 0
    for f in html_files():
        s = f.read_text(encoding="utf-8")
        s2, n_meta = META_RE.subn(lambda m: m.group(1) + new + m.group(3), s)
        s2, n_v = VTAG_RE.subn(lambda m: m.group(1) + new, s2)
        if s2 != s:
            if not dry:
                f.write_text(s2, encoding="utf-8")
            print(f"{'would update' if dry else 'updated'} {f.name}: meta={n_meta} ?v={n_v}")
            total += n_meta + n_v
    if total == 0:
        print("nothing to update (already at this build?)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
