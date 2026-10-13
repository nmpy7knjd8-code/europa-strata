"""Bump the single build string (era-ui-N) everywhere it appears in HTML.
JS reads it from <meta name="build">, so data fetches follow automatically.
Usage: python3 scripts/bump_version.py era-ui-54"""
import pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
new = sys.argv[1]
for f in root.glob("*.html"):
    s = f.read_text()
    f.write_text(re.sub(r"era-ui-\d+", new, s))
    print("updated", f.name)
