#!/usr/bin/env python3
"""Build data/kingdom-eras/geo/early-medieval.topo.json from historical-basemaps.

Early Medieval has no older hand-drawn extents, so polities are assigned by an
explicit dataset-name table (NAME_MAP) instead of the fuzzy/spatial matching in
build_era_maps_v2.py. Large unnamed dataset areas are assigned only where a
rough box in UNNAMED_BOXES says whose land they were; the rest stays unnamed
(drawn pale and unclickable, like the other era tabs).

Reuses land clipping, tiling and mapshaper settings from build_era_maps_v2.py so
the geometry matches the other tabs.

Usage: python3 scripts/build_early_medieval_map.py --hb /path/to/historical-basemaps/geojson
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_era_maps_v2 import BBOX, REPO, fix, polys_only, tile  # noqa: E402

ERA = "early-medieval"
YEARS = (400, 500, 600, 700, 800, 900)

NAME_MAP = {
    "western-roman": ["Western Roman Empire"],
    "byzantium": ["Eastern Roman Empire", "Byzantine Empire", "Cyprus"],
    "hunnic-empire": ["Hunnic Empire", "Akatziri", "Skirii", "Gepids"],
    "alans": ["Caucasian Alans", "Alans"],
    "sasanian": ["Persia", "Sasanian Empire"],
    "visigoths": ["Visigoths", "Visigothic Kingdom"],
    "ostrogoths": ["Ostrogoths", "Goths"],
    "franks": ["Franks", "Frankish Kingdom", "Neustria", "Carolingian Empire"],
    "burgundians": ["Burgundians"],
    "alamanni": ["Alamans"],
    "vandals": ["Vandals"],
    "suebi": ["Suebi"],
    "saxons": ["Saxons"],
    "thuringians": ["Turingians"],
    "frisians": ["Frisians"],
    "anglo-saxons": ["Anglo-Saxons", "Cantia", "Kent", "Essex", "Mercia", "Wessex", "Northumbria"],
    "britons": ["Dumonii", "Dumnonia", "Celtic kingdoms", "Welsh", "Armorica", "Broërec", "Britany"],
    "picts-scots": ["Picts", "Scots"],
    "irish": ["Irlanda"],
    "basques": ["Basques", "Vasconia"],
    "swedes": ["Swedes", "Swedes and Goths", "Geats", "Guta"],
    "danes": ["Danes"],
    "norway": ["Northmen", "Kingdom of Norway"],
    "saami": ["Saami", "Sámi", "Sami"],
    "finno-ugric": ["Finno-Ugric taiga hunter-gatherers", "Finns", "Karelians", "Veps", "Ests", "Chuds",
                    "Permians", "Mordvinians", "Mari", "Bashkirs", "Paleo-Siberian hunter-gatherers",
                    "Lake Vygozero", "Lake Segozerskoye"],
    "avars": ["Avars"],
    "khazars": ["Khazars", "Sabirs", "Huns"],
    "bulgaria": ["Bulgars", "Danube Bulgars"],
    "volga-bulgars": ["Volga Bulgars"],
    "lombards": ["Lombard principalities", "Lombard duchies"],
    "slavs": ["Slavs", "Proto-Slavs", "Slavonic tribes", "Slavic tribes", "Kryvichs", "Polanes",
              "Severians", "Czechs", "Polyanians", "Chelmia"],
    "great-moravia": ["Moravians", "Great Moravia"],
    "balts": ["Balts", "Baltic tribes"],
    "umayyad": ["Umayyad Caliphate"],
    "abbasid": ["Abbasid Caliphate", "Saffarids", "Samanid Empire", "Kwarezm"],
    "cordoba": ["Emirate of Córdoba"],
    "aghlabids": ["Aghlabid Emirate", "Emirate of Sicily"],
    "gokturks": ["Western Gokturk Khaganate", "West Getaes", "East Getaes"],
    "caucasus": ["Georgian Kingdom", "Armenia", "Caucasian Albania"],
    "magyars": ["Magyars"],
    "pechenegs": ["Pechenegs", "Oghuz Turks"],
    "rus": ["Rus' Khaganate", "Kyivan Rus"],
    "papal-states": ["Papal States"],
    "asturias": ["Asturias"],
    "east-francia": ["East Francia"],
    "west-francia": ["West Francia"],
    "croatia": ["Croatian kingdom"],
    "serbia": ["Serbia"],
}
BY_NAME = {n: pid for pid, names in NAME_MAP.items() for n in names}

# (years, (minlon, minlat, maxlon, maxlat), polityId) for unnamed dataset land
UNNAMED_BOXES = [
    (YEARS, (-11, 51, -5.4, 55.5), "irish"),
    ((400, 600, 700), (-6.5, 54.6, 0, 59.5), "picts-scots"),
    ((400,), (-6, 50, 2, 54.6), "britons"),
    ((600, 700), (-6, 50, 2, 54.6), "britons"),
    ((500,), (-6.5, 55, 0, 59.5), "picts-scots"),
    ((400, 500, 600), (4.5, 57.8, 19, 66), "norway"),
    ((400,), (11, 55, 17.5, 58.4), "swedes"),
    ((400,), (38, 39.5, 51, 44.5), "caucasus"),
    ((500, 600), (14, 44, 40, 58), "slavs"),
    ((700,), (22, 47, 38, 60), "slavs"),
    ((700,), (38, 47, 60, 60), "finno-ugric"),
    ((700,), (20, 59, 32, 63), "finno-ugric"),
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
    missing = set(NAME_MAP) - ids
    if missing:
        sys.exit(f"NAME_MAP ids missing from {ERA}.json: {sorted(missing)}")
    tmp = Path(tempfile.mkdtemp())
    files, report = [], {}
    for y in YEARS:
        items = []
        for f in json.loads((hb / f"world_{y}.geojson").read_text())["features"]:
            if not f.get("geometry"):
                continue
            g = fix(shape(f["geometry"]))
            if not g.intersects(BBOX):
                continue
            g = polys_only(g.intersection(land))
            if g.is_empty or g.area < 1e-4:
                continue
            items.append([f["properties"].get("NAME") or "", g])
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
                pid = BY_NAME.get(name)
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
        for pid, gs in assigned.items():
            g = polys_only(unary_union(gs))
            if not g.is_empty:
                feats.append({"type": "Feature", "properties": {"polityId": pid}, "geometry": mapping(g)})
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
