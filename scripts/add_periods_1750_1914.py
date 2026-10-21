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
import periods_depth as DEPTH

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
 "enlightenment": [
  ("plc-ukraine-1750","Right-bank Ukraine (Polish–Lithuanian Commonwealth)","#a83a6a",["UKR"],"fringe",0.7,
   "Kyiv, Podolia and Volhynia palatinates west of the Dnieper, ruled by Polish magnates such as the Potockis.",
   "Uniate and Orthodox wooden churches; magnate residences at Tulchyn and Berdychiv.",
   "Polish lordship over a Ukrainian Orthodox and Uniate peasantry; Haidamak revolts (1734, 1750, 1768).",
   "Hasidism begins here: the Baal Shem Tov teaches in Medzhybizh (d. 1760).",
   "Jesuit and Basilian colleges."),
  ("transcarpathia-1750","Kingdom of Hungary (Transcarpathia)","#b89a2a",["UKR"],"fringe",0.7,
   "Mukachevo and Uzhhorod, part of the Habsburg Kingdom of Hungary.",
   "Wooden churches of the Carpathian Rusyns.",
   "Habsburg lordship; the Union of Uzhhorod (1646) ties the Rusyn church to Rome.",
   "Greek Catholic clergy at Mukachevo.",
   "Salt mines and estates of the Schönborn family."),
  ("prussian-silesia-1750","Prussian Silesia and Pomerania","#2f2f2f",["POL"],"fringe",0.75,
   "Silesia, taken from Austria in 1740–42, and Prussian Pomerania; today in Poland.",
   "Breslau (Wrocław) baroque: the Leopoldina university hall.",
   "Frederick II’s cameralist administration, a war treasury and Protestant toleration of Catholics.",
   "Silesian Pietism and the Breslau Jesuits.",
   "Silesian linen and mining under Prussian rule."),
  ("wallachia-1750","Principality of Wallachia","#7a8a3a",["ROU"],"fringe",0.7,
   "Ottoman vassal principality ruled from Bucharest by Phanariot princes; Oltenia returned by Austria in 1739.",
   "Brâncovenesc monasteries; post-Byzantine church painting.",
   "Phanariot reform: Mavrocordatos abolishes serfdom in 1746.",
   "Princely Academy of Saint Sava, Bucharest.",
   "Greek-language academy teaching."),
  ("moldavia-1750","Principality of Moldavia","#8a7a2a",["ROU","MDA"],"fringe",0.7,
   "Ottoman vassal principality ruled from Iași, between the Carpathians and the Dniester; the boundary with Wallachia is drawn approximately along the Milcov and Siret.",
   "Painted monasteries of Bukovina (sixteenth century); Iași’s Golia and Trei Ierarhi churches.",
   "Mavrocordatos abolishes serfdom in 1749.",
   "Princely Academy of Iași.",
   "Dimitrie Cantemir’s Descriptio Moldaviae (1714–16)."),
  ("transylvania-1750","Principality of Transylvania (Habsburg)","#b89a2a",["ROU"],"fringe",0.7,
   "Habsburg principality since 1699 with its own Diet of three ‘nations’—Hungarian nobles, Székelys and Saxons—and four received religions; Romanians, the largest group, are not among them.",
   "Saxon fortified churches; Baroque Alba Iulia.",
   "Micu-Klein’s campaign for Romanian rights.",
   "Greek Catholic schools at Blaj (from 1754).",
   "Mining in the Apuseni mountains."),
  ("dobruja-1750","Ottoman Dobruja and the Danube fortresses","#2a7a7a",["ROU"],"fringe",0.7,
   "Directly ruled Ottoman land between the lower Danube and the Black Sea; the boundary is approximate.",
   "Ottoman mosques in Babadag and Constanța (Köstence).",
   "Nogai Tatars and Turkish settlers alongside Romanian and Bulgarian villages.",
   "Islamic schools.",
   "Danube river trade."),
 ],
 "eve-of-war": [
  ("ah-provinces-1914","Austro-Hungarian Galicia, Bukovina & Transylvania","#c8aa4a",["POL","UKR","ROU"],"fringe",0.65,
   "Galicia (Kraków, Lwów) and Bukovina (Czernowitz) in the Austrian half of the monarchy; Transylvania, the Banat and Crișana in the Hungarian half. Today they lie in Poland, Ukraine and Romania.",
   "Kraków is the capital of Young Poland: Wyspiański’s stained glass and Malczewski’s symbolism. Lwów’s opera house (1900) and Czernowitz’s Residence of the Bukovinian metropolitans mix Viennese and local styles.",
   "Galicia has run its own affairs in Polish since 1867, with a Polish governor and Polish schools; Ukrainians press for their own university in Lwów. In Transylvania, Hungarian-only school laws (the Apponyi laws, 1907) and a narrow franchise keep Romanians, the majority, almost out of parliament.",
   "Kazimierz Twardowski founds the Lwów school of logic and philosophy; Romanian Transylvanians follow the Romanian National Party’s programme of autonomy.",
   "The Jagiellonian University in Kraków and the University of Lwów teach in Polish; the Czernowitz university (1875) teaches in German. Galicia’s Borysław oil fields are among the largest in Europe."),
  ("prussian-poland-1914","Prussian Poland","#4a4a4a",["POL"],"fringe",0.65,
   "The Prussian provinces of Posen and West Prussia, with Upper Silesia, Pomerania and southern East Prussia, part of the German Empire since 1871 and of Prussia since the partitions.",
   "Poznań’s Imperial Castle (1910), built for Wilhelm II as a symbol of German rule, faces Polish banks, cooperatives and the Raczyński Library.",
   "Germanisation: the Settlement Commission (1886) buys land for German farmers, the expropriation law of 1908 allows forced purchase, and religious lessons in German spark the school strike of 1901–07. Poles answer with cooperatives, savings banks and ‘organic work’.",
   "The Polish Catholic clergy lead the defence of the language; Wojciech Korfanty speaks for Upper Silesian Poles in the Reichstag.",
   "Upper Silesia’s coal and steel make it the second industrial region of Germany; Danzig shipyards build for the Imperial Navy."),
  ("vojvodina-1914","Hungarian Bačka, Banat & Srem (Austria-Hungary)","#b89a2a",["SRB"],"fringe",0.7,
   "Southern Hungary and Croatian Srem, part of Austria-Hungary in 1914; today the Serbian province of Vojvodina.",
   "Novi Sad’s Matica srpska and Serbian theatre.",
   "Serbian, Hungarian, German, Slovak and Romanian villages side by side.",
   "Serbian cultural life centred on Novi Sad and Sremski Karlovci.",
   "Grain farming on the Pannonian plain."),
 ],
}
# Layer edits so that the right polity gets the base fill (first layer wins ties).
def edit_layers(pid, rows):
    out = []
    for r in rows:
        r = list(r)
        if pid == "enlightenment":
            if r[0] == "russia-1750":
                r[3] = [c for c in r[3] if c != "UKR"]
            if r[0] == "hetmanate":
                r[1] = "Cossack Hetmanate & Sloboda Ukraine (Russian)"
                r[4] = "dominant"
                r[6] = "Left-bank Ukraine under its own hetman and Sloboda Ukraine, both under Russian rule."
            if r[0] == "crimea":
                r[3] = ["UKR", "RUS"]  # the atlas basemap draws the Crimean peninsula inside RUS
                r[1] = "Crimean Khanate & Ottoman Black Sea coast"
                r[4] = "fringe"
                r[6] = ("Crimean Khanate, an Ottoman vassal, with its Nogai steppes, and Ottoman fortresses such as Ochakiv. "
                        "Outline from the 1715 basemap, which still includes Zaporozhian steppe that returned to Russian protection in 1734.")
            if r[0] == "principalities":
                continue  # split into wallachia-1750 / moldavia-1750 / transylvania-1750
        out.append(tuple(r))
    return out
OVERLAY_SPECS = {  # (iso, periodId) -> base layer + overlays from historical-basemaps features
 ("UKR", "enlightenment"): {"base": ("world_1715", ["Tsardom of Muscovy"]),
    "overlays": [("plc-ukraine-1750", "world_1715", ["Polish–Lithuanian Commonwealth"]),
                 ("crimea", "world_1715", ["Ottoman Empire"]),
                 ("transcarpathia-1750", "world_1715", ["Austrian Empire"])]},
 ("RUS", "enlightenment"): {"base": None,  # Crimea and the Kuban/Azov steppe; the rest stays Russian
    "overlays": [("crimea", "world_1715", ["Ottoman Empire"])]},
 ("POL", "enlightenment"): {"base": ("world_1715", ["Polish–Lithuanian Commonwealth"]),
    "overlays": [("prussian-silesia-1750", "world_1783", ["Prussia"])]},
 ("ROU", "enlightenment"): {"base": ("world_1715", ["Ottoman Empire"]),
    "overlays": [("moldavia-1750", "world_1715", ["Ottoman Empire"], "MOLDAVIA"),
                 ("dobruja-1750", "world_1715", ["Ottoman Empire"], "DOBRUJA"),
                 ("transylvania-1750", "world_1715", ["Austrian Empire"])]},
 ("POL", "eve-of-war"): {"base": ("world_1914", ["Russian Empire"]),
    "overlays": [("prussian-poland-1914", "world_1914", ["German Empire"]),
                 ("ah-provinces-1914", "world_1914", ["Austro-Hungarian Empire"])]},
 ("UKR", "eve-of-war"): {"base": None,  # remainder of the country (Russian); the basemap misplaces Bessarabia
    "overlays": [("ah-provinces-1914", "world_1914", ["Austro-Hungarian Empire"])]},
 ("ROU", "eve-of-war"): {"base": ("world_1914", ["Romania"]),
    "overlays": [("ah-provinces-1914", "world_1914", ["Austro-Hungarian Empire"])]},
 ("SRB", "eve-of-war"): {"base": ("world_1914", ["Serbia"]),
    "overlays": [("vojvodina-1914", "world_1914", ["Austro-Hungarian Empire"])]},
}
# Approximate cuts where historical-basemaps has no internal boundary (lon, lat; drawn
# through Focșani/Milcov–Siret and along the lower Danube via Silistra, Hârșova, Brăila, Galați, Isaccea, Tulcea).
CUTS = {
 "MOLDAVIA": [(24.5, 46.6), (26.3, 45.95), (26.8, 45.8), (27.18, 45.7), (27.45, 45.55), (28.0, 45.42), (28.25, 45.45), (30.5, 45.45), (30.5, 48.6), (24.5, 48.6)],
 "DOBRUJA": [(27.27, 43.6), (27.27, 44.12), (28.03, 44.34), (27.95, 44.68), (27.97, 45.27), (28.1, 45.38), (28.46, 45.27), (28.8, 45.18), (29.9, 45.2), (29.9, 43.6)],
}
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
    rows = edit_layers(pid, list(mod.LAYERS))
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
        for f, t in DEPTH.SET[pid].get(iso, {}).items():
            q[f] = t
        for f, t in DEPTH.ADD[pid].get(iso, {}).items():
            if q.get(f) == "—":
                q[f] = t
            elif t not in q[f]:
                q[f] = q[f].rstrip() + " " + t
        if iso in DEPTH.IMAGES[pid]:
            q["images"] = [(f, c, r, 640) for (f, c, r) in DEPTH.IMAGES[pid][iso]]
        q["images"] = list(q["images"]) + [(f, c, r, 640) for (f, c, r) in DEPTH.EXTRA[pid].get(iso, [])]
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
    # fill extents: new countries get a new block, existing ones get extra period keys
    fe = text.index('"fillExtents"')
    c0 = text.index('"countries": {', fe)
    c = c0 + len('"countries": {')
    cend = text.index("\n      }", c)
    add = ""
    inserts = []
    for iso, per in data["meta"]["fillExtents"]["countries"].items():
        items = [(pid, per[pid]) for pid in ("enlightenment", "eve-of-war") if pid in per]
        if not items:
            continue
        body = ",\n".join(f'          "{pid}": ' + json.dumps(v, separators=(", ", ": ")) for pid, v in items)
        key = f'\n        "{iso}": {{'
        k = text.find(key, c, cend)
        if k >= 0:
            inserts.append((k + len(key), "\n" + body + ","))
        else:
            add += key + "\n" + body + "\n        },"
    for pos, chunk in sorted(inserts, reverse=True):
        text = text[:pos] + chunk + text[pos:]
    text = text[:c] + add + text[c:]
    ov = data["meta"]["fillExtents"].get("overlays")
    if ov:
        text = text[:c0] + '"overlays": ' + json.dumps(ov, ensure_ascii=False, separators=(", ", ": ")) + ",\n      " + text[c0:]
    return text

def mute(hexc, k=0.62, base=(0x2b, 0x2b, 0x33)):
    """Pull the drafting palette toward the atlas's muted early-modern/modern tones."""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(c * k + o * (1 - k)) for c, o in zip((r, g, b), base))

def link(pid, iso, name):
    return {"periodId": pid, "iso": iso, "name": name}

def _parts(g, min_area=0.02):
    g = g.buffer(0)
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area >= min_area]
    out = []
    for p in sorted(parts, key=lambda x: -x.area):
        p = p.simplify(0.05)
        if p.is_empty or p.geom_type != "Polygon":
            continue
        out.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
    return out

def build_extents(data, basemaps):
    from shapely.geometry import shape, Polygon
    from shapely.ops import unary_union
    eu = {f["properties"]["iso"]: shape(f["geometry"]).buffer(0)
          for f in json.loads((ROOT / "data/europe.geojson").read_text())["features"]}
    cache = {}
    def hist(fn, names):
        if fn not in cache:
            cache[fn] = json.loads(pathlib.Path(basemaps, fn + ".geojson").read_text())["features"]
        return unary_union([shape(f["geometry"]).buffer(0) for f in cache[fn] if f["properties"].get("NAME") in names]).buffer(0)
    ext = data["meta"]["fillExtents"]["countries"]
    ovs = data["meta"]["fillExtents"]["overlays"]
    for (iso, pid), spec in OVERLAY_SPECS.items():
        country = eu[iso].buffer(0.3)
        core = hist(*spec["base"]).intersection(country) if spec["base"] else Polygon()
        for o in spec["overlays"]:
            if len(o) > 3:
                core = core.difference(Polygon(CUTS[o[3]]))
        taken, ov_geoms = core, []
        for o in spec["overlays"]:
            g = hist(o[1], o[2]).intersection(country)
            if len(o) > 3:
                g = g.intersection(Polygon(CUTS[o[3]]))
            g = g.difference(taken)
            taken = taken.union(g)
            ov_geoms.append((o[0], g))
        base = core if spec["base"] else country.difference(taken)
        rings = _parts(base)
        ext.setdefault(iso, {})[pid] = rings[0] if len(rings) == 1 else rings
        for lid, g in ov_geoms:
            r = _parts(g)
            if r:
                ovs.setdefault(pid, []).append({"iso": iso, "layer": lid, "rings": r})


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
    # extents and sub-country overlays
    data["meta"]["fillExtents"].setdefault("overlays", {})
    build_extents(data, a.basemaps)
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
