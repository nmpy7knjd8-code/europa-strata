#!/usr/bin/env python3
"""Add the 1920, 1938 and 1960 maps to data/kingdom-eras/geo/modern.topo.json.

The six original Modern ticks keep their geometry: the existing TopoJSON is
read back in as-is and only the three new layers are cleaned and simplified,
with the same mapshaper settings as build_era_maps_v2.py.

Polities are assigned by an explicit dataset-name table (NAME_MAP, with
per-year overrides in YEAR_NAME_MAP), like build_early_medieval_map.py.
Names not in the tables stay as named extras (profiles come from
basemap-profiles.json); unnamed land stays pale and unclickable.

Usage: python3 scripts/build_modern_extra_years.py --hb /path/to/historical-basemaps/geojson
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_era_maps_v2 import BBOX, REPO, fix, polys_only, tile  # noqa: E402

ERA = "modern"
YEARS = (1920, 1938, 1960)

NAME_MAP = {
    "USSR": "ussr", "Sweden": "sweden", "Finland": "finland", "France": "france", "Norway": "norway",
    "Spain": "spain", "Poland": "poland", "United Kingdom of Great Britain and Ireland": "united-kingdom",
    "United Kingdom": "united-kingdom", "Ireland": "ireland", "Romania": "romania", "Italy": "italy",
    "Yugoslavia": "yugoslavia", "Ottoman Sultanate": "ottoman-empire", "Turkey": "turkey", "Iceland": "iceland",
    "Czechoslovakia": "czechoslovakia", "Greece": "greece", "Bulgaria": "bulgaria", "Denmark": "denmark",
    "Hungary": "hungary", "Austria": "austria", "Portugal": "portugal", "Lithuania": "lithuania",
    "Latvia": "latvia", "Estonia": "estonia", "Switzerland": "switzerland", "Netherlands": "netherlands",
    "Belgium": "belgium", "Albania": "albania", "Luxembourg": "luxembourg",
    "Ukraine": "ukrainian-ssr", "White Russia": "byelorussian-ssr", "South Russia": "south-russia",
    "Georgia": "georgia-dr", "Azerbaijan": "azerbaijan-dr", "Cyprus": "cyprus",
    "West Germany": "germany-west", "East Germany": "germany-east",
}
YEAR_NAME_MAP = {
    1920: {"Germany": "weimar-republic", "East Prussia": "weimar-republic", "Armenia": "armenia-republic"},
    1938: {"Germany": "nazi-germany", "Armenia": "ussr"},
}
# (years, (minlon, minlat, maxlon, maxlat), polityId) for unnamed dataset land
UNNAMED_BOXES = [
    ((1938,), (-25, 63, -13, 67), "iceland"),
]
# (year, dataset name, box, polityId): carve part of a named dataset polygon.
# The 1938 file draws Iceland, then a kingdom in personal union, as Denmark.
CARVE = [
    (1938, "Denmark", (-25, 63, -13, 67), "iceland"),
]


def land_shape():
    """Natural Earth land, seam-closed exactly as in build_era_maps_v2.main()."""
    land = fix(unary_union([fix(shape(f["geometry"])) for f in
                            json.loads((REPO / "data/europe.geojson").read_text())["features"]])).intersection(BBOX)
    land = fix(land.buffer(0.03, join_style=2).buffer(-0.03, join_style=2).union(land))
    return unary_union([Polygon(pg.exterior, [r for r in pg.interiors if Polygon(r).area > 0.3])
                        for pg in getattr(land, "geoms", [land])])


def build_layer(hb, y, land, ids):
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
        else:
            items.append(["", gp])  # land the dataset leaves out entirely (e.g. Iceland in 1938)
    names = {**NAME_MAP, **YEAR_NAME_MAP.get(y, {})}
    assigned, feats, extras = {}, [], set()
    for name, g in items:
        for cy, cname, bb, cpid in CARVE:
            if cy == y and cname == name:
                part = polys_only(g.intersection(box(*bb)))
                if not part.is_empty:
                    assigned.setdefault(cpid, []).append(part)
                    g = polys_only(g.difference(box(*bb)))
        if g.is_empty:
            continue
        if name:
            pid = names.get(name)
            if pid:
                if pid not in ids:
                    sys.exit(f"{name} -> {pid}: no such polity in {ERA}.json")
                assigned.setdefault(pid, []).append(g)
            else:
                extras.add(name)
                feats.append({"type": "Feature", "properties": {"polityId": "", "name": name, "extra": 1}, "geometry": mapping(g)})
            continue
        rest = g
        for yrs, bb, pid in UNNAMED_BOXES:
            if y in yrs:
                part = polys_only(rest.intersection(box(*bb)))
                if not part.is_empty and part.area > 1e-4:
                    assigned.setdefault(pid, []).append(part)
                    rest = polys_only(rest.difference(box(*bb)))
        if not rest.is_empty:
            feats.append({"type": "Feature", "properties": {"polityId": "", "name": "", "extra": 1}, "geometry": mapping(rest)})
    # smallest first: the dataset's USSR overlaps Ukraine, Belarus and the
    # Caucasus republics in 1920, and tile() gives earlier features priority
    for pid, gs in sorted(assigned.items(), key=lambda kv: unary_union(kv[1]).area):
        g = polys_only(unary_union(gs))
        if not g.is_empty:
            feats.append({"type": "Feature", "properties": {"polityId": pid}, "geometry": mapping(g)})
    return tile(feats, land), {"polities": sorted(assigned), "extras": sorted(extras)}


def merge_topologies(base, extra):
    """Append extra's objects to base without touching base's arcs: extra's arcs
    are re-quantized onto base's transform and appended after base's arcs."""
    (bsx, bsy), (btx, bty) = base["transform"]["scale"], base["transform"]["translate"]
    (esx, esy), (etx, ety) = extra["transform"]["scale"], extra["transform"]["translate"]
    off = len(base["arcs"])
    for arc in extra["arcs"]:
        x = y = 0
        qx0 = qy0 = 0
        enc = []
        for i, (dx, dy) in enumerate(arc):
            x += dx; y += dy
            qx = round((x * esx + etx - btx) / bsx)
            qy = round((y * esy + ety - bty) / bsy)
            enc.append([qx, qy] if i == 0 else [qx - qx0, qy - qy0])
            qx0, qy0 = qx, qy
        base["arcs"].append(enc)
    def shift(v):
        if isinstance(v, int):
            return v + off if v >= 0 else ~(~v + off)
        return [shift(x) for x in v]
    for k, o in extra["objects"].items():
        for g in o.get("geometries", []):
            if "arcs" in g:
                g["arcs"] = shift(g["arcs"])
        base["objects"][k] = o
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hb", required=True)
    a = ap.parse_args()
    hb = Path(a.hb)
    land = land_shape()
    pack = json.loads((REPO / f"data/kingdom-eras/{ERA}.json").read_text())
    ids = {p["id"] for p in pack["polities"]}
    topo_path = REPO / "data" / "kingdom-eras" / "geo" / f"{ERA}.topo.json"
    topo = json.loads(topo_path.read_text())
    tmp = Path(tempfile.mkdtemp())
    # existing layers only (re-running replaces the extra years, never stacks them)
    for y in YEARS:
        topo["objects"].pop(f"y{y}", None)
    # their arcs were appended after the original ones: drop them too
    used = []
    def collect(v):
        if isinstance(v, int):
            used.append(v if v >= 0 else ~v)
        else:
            for x in v:
                collect(x)
    for o in topo["objects"].values():
        for g in o.get("geometries", []):
            collect(g.get("arcs", []))
    del topo["arcs"][max(used) + 1:]
    files, report = [], {}
    for y in YEARS:
        feats, report[y] = build_layer(hb, y, land, ids)
        fp = tmp / f"y{y}.json"
        fp.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
        files.append(str(fp))
    subprocess.run(["npx", "--yes", "mapshaper", "-i", *files, "combine-files",
                    "-clean", "target=*", "-simplify", "8%", "keep-shapes", "planar",
                    "-clean", "target=*", "gap-fill-area=500km2", "-filter-islands", "target=*", "min-area=40km2",
                    "-o", str(tmp / "new.topo.json"), "format=topojson", "quantization=100000"], check=True)
    out = merge_topologies(topo, json.loads((tmp / "new.topo.json").read_text()))
    out["objects"] = {k: out["objects"][k] for k in sorted(out["objects"], key=lambda k: int(k[1:]))}
    topo_path.write_text(json.dumps(out, separators=(",", ":")))
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print(ERA, topo_path.stat().st_size // 1024, "KB", list(out["objects"]))


if __name__ == "__main__":
    main()
