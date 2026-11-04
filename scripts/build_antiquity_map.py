#!/usr/bin/env python3
"""Build data/kingdom-eras/geo/antiquity.topo.json from historical-basemaps.

Antiquity has no older hand-drawn extents, so polities are assigned by an
explicit dataset-name table (NAME_MAP) instead of the fuzzy/spatial matching in
build_era_maps_v2.py. Large unnamed dataset areas are assigned only where a
rough box in UNNAMED_BOXES says whose land they were; the rest stays unnamed
(drawn pale and unclickable, like the other era tabs).

Reuses land clipping, tiling and mapshaper settings from build_era_maps_v2.py so
the geometry matches the other tabs.

Usage: python3 scripts/build_antiquity_map.py --hb /path/to/historical-basemaps/geojson
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_era_maps_v2 import BBOX, REPO, fix, polys_only, tile  # noqa: E402

ERA = "antiquity"
# (year, historical-basemaps file stem)
YEARS = ((-500, "bc500"), (-323, "bc323"), (-200, "bc200"), (-1, "bc1"), (100, "100"), (300, "300"))
ALL = tuple(y for y, _ in YEARS)

NAME_MAP = {
    "achaemenid": ["Achaemenid Empire"],
    "greek-poleis": ["Greek city-states"],
    "alexander-empire": ["Empire of Alexander"],
    "antigonid-macedon": ["Macedon and Hellenic League"],
    "seleucid": ["Seleucid Kingdom"],
    "ptolemaic": ["Ptolemaic Kingdom"],
    "pergamon": ["Pergamon"],
    "anatolian-kingdoms": ["Cappadocia", "minor states"],
    "bosporan": ["Bosporan Kingdom", "Bosporian Kingdom"],
    "carthage": ["Carthaginian Empire"],
    "etruscans": ["Etrurians"],
    "roman-republic": ["Rome"],
    "roman-empire": ["Roman Empire", "Rome (Constantinus)", "Rome (Maximian)", "Rome (Galerius)", "Rome (Diocletianus)"],
    "italic-peoples": ["Sabini", "Sabines", "Samnites"],
    "celts": ["Celts", "Boii"],
    "britons": ["Dumonii"],
    "illyrians": ["Illyrians", "Dardania"],
    "thracians": ["Odrysian Kingdom", "?"],
    "dacians": ["Dacia"],
    "scythians": ["Scythians"],
    "sarmatians": ["Alans"],
    "armenia": ["Armenia"],
    "atropatene": ["Atropatene"],
    "colchis": ["Colchis"],
    "parthia": ["Parthian Empire"],
    "marcomanni": ["Boihaenum"],
    "scandinavians": ["Norsemen", "Heruli"],
    "balts": ["Sambian-Nothangian culture", "Western Masurian culture", "Eastern Masurian culture",
              "Curonians", "Brushed Pottery culture"],
    "dnieper-dvina": ["Plain-Pottery culture"],
    "milograd": ["Milograd culture"],
    "pomeranian-culture": ["Pomeranian culture", "Bell-shaped burials culture"],
    "finno-ugric": ["Finno-Ugric taiga hunter-gatherers", "Paleo-Siberian hunter-gatherers"],
    "saami": ["Saami"],
}
BY_NAME = {n: pid for pid, names in NAME_MAP.items() for n in names}
# the same dataset name means a different polity in some years
YEAR_NAME_MAP = {
    (300, "Parthian Empire"): "sasanian",
    **{(y, "Bell-shaped burials culture"): "przeworsk" for y in (-200, -1, 100)},
    **{(y, "Pomeranian culture"): "germanic-peoples" for y in (-200, -1)},
    (100, "Pomeranian culture"): "goths",
}
EXTRA_IDS = {"sasanian", "przeworsk", "germanic-peoples", "goths"}

# (years, (minlon, minlat, maxlon, maxlat), polityId) for unnamed dataset land; first match wins
UNNAMED_BOXES = [
    ((-500, -1, 100, 300), (-11, 51, -5.4, 55.5), "irish"),
    ((100, 300), (-6.5, 55, -1.5, 59.5), "caledonians"),
    ((-1,), (-6.5, 50, 2, 59.5), "britons"),
    ((-500,), (-6.5, 50, 2, 59.5), "celts"),
    (ALL, (4, 54.8, 19, 71), "scandinavians"),
    (ALL, (19, 60, 25, 71), "scandinavians"),
    ((-500, -323, -200), (-10, 35.9, 3.3, 43.4), "iberians"),
    ((-500,), (11.5, 40, 16.5, 43.5), "italic-peoples"),
    ((-500, -323, -200), (-5, 43.4, 16, 50.5), "celts"),
    ((-500, -323, -200), (4, 50.5, 15.5, 54.8), "germanic-peoples"),
    ((-1, 100, 300), (4, 47, 15.5, 54.8), "germanic-peoples"),
    ((-500, -323, -200), (20, 41, 30, 48.5), "thracians"),
    ((-500, -323), (28, 44, 50, 52), "scythians"),
    ((100, 300), (18, 45, 23.5, 48.5), "sarmatians"),
    ((300,), (15.5, 49.5, 24, 54.5), "goths"),
    ((300,), (24, 45, 36, 52), "goths"),
    ((300,), (19, 54.5, 28, 58.5), "balts"),
    ((-1, 100, 300), (28, 42, 55, 52), "sarmatians"),
]


def land_shape():
    land = fix(unary_union([fix(shape(f["geometry"])) for f in
                            json.loads((REPO / "data/europe.geojson").read_text())["features"]])).intersection(BBOX)
    land = fix(land.buffer(0.03, join_style=2).buffer(-0.03, join_style=2).union(land))
    return unary_union([Polygon(pg.exterior, [r for r in pg.interiors if Polygon(r).area > 0.3])
                        for pg in getattr(land, "geoms", [land])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hb", required=True)
    a = ap.parse_args()
    hb = Path(a.hb)
    land = land_shape()
    pack = json.loads((REPO / f"data/kingdom-eras/{ERA}.json").read_text())
    ids = {p["id"] for p in pack["polities"]}
    missing = (set(NAME_MAP) | EXTRA_IDS | {b[2] for b in UNNAMED_BOXES}) - ids
    if missing:
        sys.exit(f"NAME_MAP ids missing from {ERA}.json: {sorted(missing)}")
    tmp = Path(tempfile.mkdtemp())
    files, report = [], {}
    for y, stem in YEARS:
        items = []
        for f in json.loads((hb / f"world_{stem}.geojson").read_text())["features"]:
            if not f.get("geometry"):
                continue
            g = fix(shape(f["geometry"]))
            if not g.intersects(BBOX):
                continue
            g = polys_only(g.intersection(land))
            if g.is_empty or g.area < 1e-4:
                continue
            items.append([(f["properties"].get("NAME") or "").strip(), g])
        covered = unary_union([g for _, g in items])
        gaps = polys_only(land.difference(covered))
        for gp in getattr(gaps, "geoms", [gaps]) if not gaps.is_empty else []:
            best, bv = None, 0
            gb = gp.buffer(0.05)
            for it in items:
                v = gb.intersection(it[1]).area
                if v > bv:
                    best, bv = it, v
            if best is not None:
                best[1] = polys_only(unary_union([best[1], gp]))
        assigned, feats, unknown = {}, [], set()
        for name, g in items:
            if name:
                pid = YEAR_NAME_MAP.get((y, name)) or BY_NAME.get(name)
                if pid:
                    assigned.setdefault(pid, []).append(g)
                else:
                    unknown.add(name)
                    feats.append({"type": "Feature", "properties": {"polityId": "", "name": name, "extra": 1}, "geometry": mapping(g)})
                continue
            rest = g
            for yrs, bb, pid in UNNAMED_BOXES:
                if y not in yrs:
                    continue
                part = polys_only(rest.intersection(box(*bb)))
                if not part.is_empty and part.area > 1e-4:
                    assigned.setdefault(pid, []).append(part)
                    rest = polys_only(rest.difference(box(*bb)))
                if rest.is_empty:
                    break
            if not rest.is_empty:
                feats.append({"type": "Feature", "properties": {"polityId": "", "name": "", "extra": 1}, "geometry": mapping(rest)})
        pol_feats = []
        for pid, gs in assigned.items():
            g = polys_only(unary_union(gs))
            if not g.is_empty:
                pol_feats.append((g.area, {"type": "Feature", "properties": {"polityId": pid}, "geometry": mapping(g)}))
        # tile() gives earlier features priority: smallest polities first, unnamed land last
        feats = [f for _, f in sorted(pol_feats, key=lambda t: t[0])] + feats
        feats = tile(feats, land)
        report[y] = {"polities": sorted(assigned), "unmappedNames": sorted(unknown)}
        fp = tmp / f"y{y}.json"
        fp.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
        files.append(str(fp))
    out = REPO / "data" / "kingdom-eras" / "geo" / f"{ERA}.topo.json"
    subprocess.run(["npx", "--yes", "mapshaper", "-i", *files, "combine-files",
                    "-clean", "target=*", "-simplify", "8%", "keep-shapes", "planar",
                    "-clean", "target=*", "gap-fill-area=500km2", "-filter-islands", "target=*", "min-area=40km2",
                    "-o", str(out), "format=topojson", "quantization=100000"], check=True)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print(ERA, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
