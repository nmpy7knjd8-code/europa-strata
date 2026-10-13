"""Content fixes from europa-review.md (review-fixes branch). Idempotent."""
import json, re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent / "data"
tl = json.loads((R / "timeline.json").read_text())
P = {p["id"]: p for p in tl["periods"]}

# Steppe ancestry too early in the south (Olalde 2019; Saupe et al. 2021)
ib = P["beaker-corded"]["regions"]["iberia"]
ib["ancestry"] = {"eef": 72, "whg": 23, "steppe": 5}
ib["ancestryRange"] = {"steppe": [0, 25], "eef": [55, 80]}
ib["ancestryCline"]["note"] = ("At c. 2500 BC most Iberians still carry little or no steppe ancestry; a few "
    "Beaker-associated incomers are steppe-rich. Population-wide steppe (~25–40%) builds after c. 2200–2000 BC.")
for end in ib["ancestryCline"]["ends"]:
    if end["id"] == "base":
        end["ancestry"] = {"eef": 76, "steppe": 2, "whg": 22}
ib["ancestryNote"] = "Beaker Iberia: steppe arrives with a few incomers c. 2500–2200 BC and spreads gradually (often male-biased); still low at this tick."
it = P["beaker-corded"]["regions"]["italy"]
it["ancestry"] = {"eef": 75, "whg": 22, "steppe": 3}
it["ancestryNote"] = "Still EEF+WHG; steppe-related ancestry is rare in Italy before c. 2000 BC (Saupe et al. 2021)."
iy = P["yamnaya"]["regions"]["italy"]
iy["ancestry"] = {"eef": 78, "whg": 22}
iy["ancestryNote"] = "EEF+WHG Copper Age Italy; no detectable steppe ancestry yet."

# High Medieval (c. 1200) anachronisms
e = P["high-medieval"]["regions"]["eastern"]
e["incoming"] = "Cuman/Kipchak steppe contact"
e["languageFamily"] = "East Slavic + Turkic (steppe neighbours)"
e["languages"] = "Old East Slavic varieties; Cuman/Kipchak Turkic on the steppe; Church Slavonic and Greek in church use"
e["linguisticNote"] = "East Slavic principalities beside Turkic-speaking steppe confederations; the Mongol conquest (1237–40) comes a generation later."
e["ancestryNote"] = "Medieval East Slavic base + variable steppe (Cuman/Kipchak) input."
P["high-medieval"]["regions"]["italy"]["linguisticNote"] = ("Sicilian School poetry and Tuscan/Umbrian volgare emerge on a dialect continuum; "
    "Dante (b. 1265) later crystallizes literary Italian.")

# Guernsey / Jersey belong to the Britain region
rc = tl["meta"]["regionCountries"]["britain"]
for iso in ("GGY", "JEY"):
    if iso not in rc:
        rc.append(iso)

# Glossary phenotype consistency lives in ancestry.json; Kyiv spelling + BC in UI text
def walk(o, key=None):
    if isinstance(o, dict):
        return {k: walk(v, k) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v, key) for v in o]
    if isinstance(o, str) and key not in ("src", "href", "url"):
        o = re.sub(r"\bKiev\b(?!an)", "Kyiv", o)
        o = re.sub(r"\bBCE\b", "BC", o)
    return o
tl = walk(tl)
(R / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False) + "\n")

# ancestry.json: unified colors with atlas, BC, phenotypes
anc = json.loads((R / "ancestry.json").read_text())
colors = {k["id"]: k["color"] for k in tl["meta"]["ancestryKeys"]}
colors["wsh"] = colors["steppe"]
for c in anc["components"]:
    c["color"] = colors.get(c["id"], c["color"])
    c["years"] = re.sub(r"\bBCE\b", "BC", c["years"])
    if c["id"] == "whg":
        c["phenotype"] = "Dark skin (as in Cheddar Man, Loschbour and La Braña genomes) combined with blue/light eyes. Dark hair."
    if c["id"] == "wsh":
        c["phenotype"] = "Mostly brown eyes and dark hair; intermediate-to-light skin; above-average stature. Light-hair alleles were rare."
anc = walk(anc)
(R / "ancestry.json").write_text(json.dumps(anc, ensure_ascii=False, indent=2) + "\n")
