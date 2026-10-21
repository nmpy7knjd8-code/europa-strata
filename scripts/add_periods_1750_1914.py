#!/usr/bin/env python3
"""Add the deep-time periods 'enlightenment' (c. 1750) and 'eve-of-war' (c. 1914).

Inserts both periods between 'early-modern' and 'modern' in data/timeline.json
(text splice, so the rest of the hand-formatted file is untouched), writes
data/timeline-text/<id>.json, adds key events, link aliases, polity chain links,
and partial-country clip rings derived from historical-basemaps (GPL-3.0,
https://github.com/aourednik/historical-basemaps) cloned at --basemaps.

Idempotent: refuses to run if the periods already exist.
"""
import argparse, json, pathlib, re, sys, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import periods_1750_data as P1750
import periods_1914_data as P1914

ROLE_FIELDS = ("art", "ideas", "philosophy", "science")
LAYER_FILL = {  # fill gaps left as "—" in the layer tables
 ("eve-of-war", "portugal-1914", "science"): "Lisbon’s medical school; colonial survey missions in Angola and Mozambique.",
 ("eve-of-war", "finland-1914", "science"): "Helsinki University; Finnish engineering and forestry science.",
 ("eve-of-war", "serbia-1914", "philosophy"): "Liberal-radical constitutionalism after 1903.",
 ("eve-of-war", "serbia-1914", "science"): "Belgrade University (1905).",
 ("eve-of-war", "montenegro-1914", "science"): "Cetinje gymnasium and press.",
 ("eve-of-war", "greece-1914", "philosophy"): "The demotic-versus-katharevousa language question.",
 ("eve-of-war", "greece-1914", "science"): "University of Athens.",
 ("eve-of-war", "bulgaria-1914", "philosophy"): "Agrarian and liberal politics.",
 ("eve-of-war", "bulgaria-1914", "science"): "Sofia University (1888).",
 ("eve-of-war", "romania-1914", "philosophy"): "Junimea circle (Titu Maiorescu).",
 ("eve-of-war", "romania-1914", "science"): "Victor Babeș’s bacteriology.",
 ("eve-of-war", "albania-1914", "art"): "Marubi photography studio, Shkodër.",
 ("eve-of-war", "albania-1914", "philosophy"): "Sami Frashëri’s programme for an Albanian state.",
 ("eve-of-war", "albania-1914", "science"): "First Albanian schools; the 1908 alphabet.",
}
POLITY_FILL = {
 ("enlightenment", "SRB", "science"): "Learning moves north: Serbian schools at Sremski Karlovci (gymnasium founded 1791) grow from the church culture of the Habsburg Serbs.",
 ("eve-of-war", "BEL", "philosophy"): "Catholic neo-Thomism at Leuven (Cardinal Mercier).",
 ("eve-of-war", "POL", "philosophy"): "Positivism and Young Poland modernism; Kazimierz Twardowski’s Lwów school of logic.",
}
# Layer adjustments so that the fill rank picks the right polity (first layer wins ties).
EXTRA_LAYERS = {
 "eve-of-war": [
  ("ah-provinces-1914","Austro-Hungarian Galicia, Bukovina & Transylvania","#c8aa4a",["POL","UKR","ROU"],"fringe",0.65,"Habsburg provinces now in Poland, Ukraine and Romania.","Kraków and Lviv secession style.","Galician autonomy; Romanian claims on Transylvania.","Polish and Ukrainian national schools in Galicia.","Jagiellonian and Lviv universities."),
  ("prussian-poland-1914","Prussian Poland","#4a4a4a",["POL"],"fringe",0.65,"Posen and West Prussia, part of the German Empire.","—","Germanisation policy.","—","—"),
 ]
}
EXTENTS = [  # (iso, periodId, basemap file, feature NAME)
 ("POL", "enlightenment", "world_1715", "Polish–Lithuanian Commonwealth"),
 ("ROU", "eve-of-war", "world_1914", "Romania"),
 ("SRB", "eve-of-war", "world_1914", "Serbia"),
]
ALIASES = [
 ("Kingdom of Prussia", "enlightenment", "DEU"),
 ("Habsburg Monarchy", "enlightenment", "AUT"),
 ("Polish–Lithuanian Commonwealth", "enlightenment", "POL"),
 ("Cossack Hetmanate", "enlightenment", "UKR"),
 ("German Empire", "eve-of-war", "DEU"),
 ("Austria-Hungary", "eve-of-war", "AUT"),
 ("Russian Empire", "eve-of-war", "RUS"),
]

def src(fname, w):
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fname) + f"?width={w}"

def build(mod, early_regions):
    pid = mod.PERIOD["id"]
    p = dict(mod.PERIOD)
    regions, rtext = {}, {}
    for key, r in mod.REGIONS.items():
        r = dict(r)
        rtext[key] = {"description": r.pop("description")}
        base = early_regions[key]
        regions[key] = {"culture": r["culture"], "color": base["color"], "mode": "continuity",
                        "ancestry": dict(base["ancestry"]), "substrate": r["substrate"], "incoming": r["incoming"],
                        "fused": r["fused"], "languageFamily": r["languageFamily"], "languages": r["languages"],
                        "linguisticNote": r["linguisticNote"], "linguisticConfidence": r["linguisticConfidence"],
                        "ancestryNote": r["ancestryNote"]}
    layers = []
    rows = list(mod.LAYERS)
    if pid == "eve-of-war":  # finland before russia so the grand duchy keeps its own colour
        rows.sort(key=lambda l: 0 if l[0] == "finland-1914" else 1)
    rows += EXTRA_LAYERS.get(pid, [])
    for (lid, label, color, countries, role, op, note, art, ideas, phil, sci) in rows:
        d = {"id": lid, "label": label, "color": mute(color), "countries": countries, "role": role, "opacity": op,
             "note": note, "art": art, "ideas": ideas, "philosophy": phil, "science": sci}
        for f in ROLE_FIELDS:
            if d[f] == "—":
                d[f] = LAYER_FILL.get((pid, lid, f)) or f"See the {label} entry in the matching kingdom-era tab."
        layers.append(d)
    p["regions"] = regions
    p["mapLayers"] = layers
    polities, ptext = {}, {}
    for iso, q in mod.POL.items():
        q = dict(q)
        for f in list(q):
            if q[f] == "—":
                q[f] = POLITY_FILL[(pid, iso, f)]
        ent = {k: q[k] for k in ("name", "summary", "conflicts", "leaders", "religion", "culture")}
        if q.get("aliases"):
            ent["aliases"] = q["aliases"]
        polities[iso] = ent
        ptext[iso] = {"art": q["art"], "ideas": q["ideas"],
                      "images": [{"src": src(f, w), "alt": c, "caption": c, "role": r} for (f, c, r, w) in q["images"]],
                      "literature": q["literature"], "philosophy": q["philosophy"], "science": q["science"], "story": q["story"]}
    p["polities"] = polities
    order = ["id", "label", "era", "yearLabel", "yearApprox", "narrative", "culturesNote", "regions", "linguistics",
             "mapLayers", "tickYear", "polities", "periodName"]
    p = {k: p[k] for k in order}
    return p, {"periodId": pid, "regions": rtext, "polities": ptext}


def ind(obj, n):
    return "\n".join((" " * n + l) if k else l for k, l in enumerate(json.dumps(obj, indent=2, ensure_ascii=False).split("\n")))

def splice(text, data, e, w, early, modern):
    """Edit the hand-formatted timeline.json textually; everything else stays byte-identical."""
    em = text.index('      "id": "early-modern",')
    mo = text.index('      "id": "modern",')
    # chain links inside early-modern (succeededBy) and modern (precededBy)
    def sub_links(seg, key, pols):
        def rep(m):
            iso = re.search(r'"iso": "([A-Z]{3})"', m.group(0)).group(1)
            return f'"{key}": ' + ind(pols[iso][key], 10)
        seg = re.sub(r'"%s": \{[^}]*\}' % key, rep, seg)
        pstart = seg.index('"polities": {')
        for iso, pol in pols.items():
            if key not in pol:
                continue
            a = seg.index(f'\n        "{iso}": {{', pstart)
            b = seg.index("\n        }", a)
            if f'"{key}"' not in seg[a:b]:
                seg = seg[:b] + f',\n          "{key}": ' + ind(pol[key], 10) + seg[b:]
        return seg
    seg_e = sub_links(text[em:mo], "succeededBy", early["polities"])
    end_mod = text.index('"periodName"', mo)
    seg_m = sub_links(text[mo:end_mod], "precededBy", modern["polities"])
    start = text.rindex("    {\n", 0, mo)
    newp = "    " + ind(e, 4) + ",\n    " + ind(w, 4) + ",\n"
    cut = len(seg_e) - (mo - start)
    text = text[:em] + seg_e[:cut] + newp + seg_e[cut:] + seg_m + text[end_mod:]
    # link aliases
    la = text.index('"linkAliases": [')
    close = text.index("\n    ]", la)
    new_al = [a for a in data["meta"]["linkAliases"] if a["periodId"] in ("enlightenment", "eve-of-war")]
    text = text[:close] + "".join(",\n      " + ind(a, 6) for a in new_al) + text[close:]
    # fill extents (new countries only)
    c = text.index('"countries": {', text.index('"fillExtents"')) + len('"countries": {')
    add = ""
    for iso, per in data["meta"]["fillExtents"]["countries"].items():
        for pid in ("enlightenment", "eve-of-war"):
            if pid in per:
                ring = ", ".join(f"[{x}, {y}]" for x, y in per[pid])
                add += f'\n        "{iso}": {{\n          "{pid}": [{ring}]\n        }},'
    return text[:c] + add + text[c:]

def mute(hexc, k=0.62, base=(0x2b, 0x2b, 0x33)):
    """Pull the drafting palette toward the atlas's muted early-modern/modern tones."""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(c * k + o * (1 - k)) for c, o in zip((r, g, b), base))

def link(pid, iso, name):
    return {"periodId": pid, "iso": iso, "name": name}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basemaps", default="/tmp/historical-basemaps/geojson")
    a = ap.parse_args()
    tpath = ROOT / "data/timeline.json"
    text = tpath.read_text(encoding="utf-8")
    data = json.loads(text)
    ids = [p["id"] for p in data["periods"]]
    if "enlightenment" in ids:
        sys.exit("periods already present")
    early = next(p for p in data["periods"] if p["id"] == "early-modern")
    modern = next(p for p in data["periods"] if p["id"] == "modern")
    e, et = build(P1750, early["regions"])
    w, wt = build(P1914, early["regions"])
    # chains
    for iso, pol in e["polities"].items():
        if iso in early["polities"]:
            pol["precededBy"] = link("early-modern", iso, early["polities"][iso]["name"])
        if iso in w["polities"]:
            pol["succeededBy"] = link("eve-of-war", iso, w["polities"][iso]["name"])
    for iso, pol in w["polities"].items():
        if iso in e["polities"]:
            pol["precededBy"] = link("enlightenment", iso, e["polities"][iso]["name"])
        if iso in modern["polities"]:
            pol["succeededBy"] = link("modern", iso, modern["polities"][iso]["name"])
    for iso, pol in early["polities"].items():
        if iso in e["polities"]:
            pol["succeededBy"] = link("enlightenment", iso, e["polities"][iso]["name"])
    for iso, pol in modern["polities"].items():
        if iso in w["polities"]:
            pol["precededBy"] = link("eve-of-war", iso, w["polities"][iso]["name"])
    # extents
    from shapely.geometry import shape
    from shapely.ops import unary_union
    eu = {f["properties"]["iso"]: shape(f["geometry"]).buffer(0)
          for f in json.loads((ROOT / "data/europe.geojson").read_text())["features"]}
    ext = data["meta"]["fillExtents"]["countries"]
    for iso, pid, fn, name in EXTENTS:
        feats = json.loads(pathlib.Path(a.basemaps, fn + ".geojson").read_text())["features"]
        hist = unary_union([shape(f["geometry"]) for f in feats if f["properties"].get("NAME") == name]).buffer(0)
        g = hist.intersection(eu[iso].buffer(0.3))
        big = max(getattr(g, "geoms", [g]), key=lambda x: x.area).simplify(0.1)
        ext.setdefault(iso, {})[pid] = [[round(x, 2), round(y, 2)] for x, y in big.exterior.coords]
    for al, pid, iso in ALIASES:
        data["meta"]["linkAliases"].append({"alias": al, "periodId": pid, "iso": iso})
    # insert periods after early-modern
    i = ids.index("early-modern")
    data["periods"][i + 1:i + 1] = [e, w]
    tpath.write_text(splice(text, data, e, w, early, modern), encoding="utf-8")
    if json.loads(tpath.read_text(encoding="utf-8")) != data:
        sys.exit("splice mismatch")
    for t in (et, wt):
        (ROOT / "data/timeline-text" / f"{t['periodId']}.json").write_text(json.dumps(t, ensure_ascii=False) + "\n", encoding="utf-8")
    kp = ROOT / "data/key-events.json"
    k = json.loads(kp.read_text(encoding="utf-8"))
    newp = {}
    for pid, mod in (("enlightenment", P1750), ("eve-of-war", P1914)):
        newp[pid] = {"periodId": pid, "keyEvents": [
            {"date": d, "title": t, "detail": de, "regions": rg, "iso": iso, "start": s, "end": en}
            for (d, t, de, rg, iso, s, en) in mod.EVENTS]}
    per = {}
    for key, v in k["periods"].items():
        per[key] = v
        if key == "early-modern":
            per.update(newp)
    k["periods"] = per
    kp.write_text(json.dumps(k, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ok", len(e["polities"]), len(w["polities"]))

if __name__ == "__main__":
    main()
