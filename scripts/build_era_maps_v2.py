#!/usr/bin/env python3
"""Build kingdom-era map geometry (v2) from aourednik/historical-basemaps.

For each kingdom-era tab and slider year:
  * load world_YYYY.geojson (historical-basemaps, GPL-3.0),
  * clip to Europe and to Natural Earth land (data/europe.geojson), filling
    coastal gaps so shorelines match the basemap,
  * assign every dataset polygon to an existing polity id (name overrides,
    fuzzy name match, then spatial overlap with the old hand-drawn extent),
  * dissolve per polity and write one TopoJSON per era (shared arcs) via mapshaper.
Years with no dataset file keep the hand-drawn outlines, flagged approx=true.

Usage: python3 scripts/build_era_maps_v2.py --hb /path/to/historical-basemaps/geojson
"""
import argparse, json, math, re, subprocess, sys, tempfile, unicodedata
from pathlib import Path
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union
from shapely.validation import make_valid

REPO = Path(__file__).resolve().parents[1]
ERAS = ("high-medieval", "renaissance", "early-modern", "modern")
# slider year -> historical-basemaps file year (None = keep hand-drawn, approximate)
YEAR_FILE = {
    "high-medieval": {1000: 1000, 1100: 1100, 1200: 1200, 1300: 1300, 1400: 1400},
    "renaissance": {1400: 1400, 1450: None, 1500: 1500, 1550: 1530, 1600: 1600},
    "early-modern": {1600: 1600, 1648: 1650, 1700: 1700, 1750: None, 1789: 1783},
    "modern": {1815: 1815, 1871: None, 1914: 1914, 1945: 1945, 1990: None, 2000: 2000},
}
BBOX = box(-25, 33, 60, 72)
UMBRELLA = {"hre"}
SPATIAL_THR = {"high-medieval": 0.6, "renaissance": 0.6, "early-modern": 0.6, "modern": 9}
OVERRIDES = json.loads((REPO / "scripts" / "era_maps_v2_overrides.json").read_text()) \
    if (REPO / "scripts" / "era_maps_v2_overrides.json").exists() else {}

STOP = {"kingdom", "of", "the", "empire", "duchy", "grand", "principality", "republic",
        "and", "lands", "state", "states", "realm", "county", "khanate", "sultanate",
        "caliphate", "union", "crown", "confederation", "great", "/", "&"}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return {t for t in re.split(r"[^a-z]+", s) if t and t not in STOP and len(t) > 2}

def fix(g):
    if not g.is_valid:
        g = make_valid(g)
    g = g.buffer(0)
    return g

def polys_only(g):
    if g.is_empty:
        return g
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    parts = [p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(parts) if parts else g.__class__()

def circle(center, km):
    lon, lat = center
    pts = []
    for i in range(49):
        a = 2 * math.pi * i / 48
        pts.append((lon + km / (111.32 * math.cos(math.radians(lat))) * math.cos(a), lat + km / 110.57 * math.sin(a)))
    return {"type": "Polygon", "coordinates": [pts]}

def ext_geom(ext):
    if not ext:
        return None
    kind = ext.get("kind", "polygon")
    if kind == "approx" and ext.get("approx", {}).get("center"):
        return circle(ext["approx"]["center"], ext["approx"].get("radiusKm", 80))
    rings = ext.get("rings")
    if not rings:
        return None
    if kind == "multi" or (isinstance(rings[0][0], list) and isinstance(rings[0][0][0], list)):
        polys = [[p] if isinstance(p[0][0], (int, float)) else p for p in rings]
        return {"type": "MultiPolygon", "coordinates": polys}
    if isinstance(rings[0][0], (int, float)):
        return {"type": "Polygon", "coordinates": [rings]}
    return {"type": "Polygon", "coordinates": rings}

def tile(feats, land):
    """Make features disjoint and cover all land: no background shows through."""
    order = sorted(range(len(feats)), key=lambda i: (bool(feats[i]["properties"].get("extra")), bool(feats[i]["properties"].get("approx"))))
    taken, geoms = None, {}
    for i in order:
        g = polys_only(shape(feats[i]["geometry"]))
        if taken is not None:
            g = polys_only(g.difference(taken))
        geoms[i] = g
        if not g.is_empty:
            taken = g if taken is None else unary_union([taken, g])
    gaps = polys_only(land.difference(taken)) if taken is not None else land
    for gp in (getattr(gaps, "geoms", [gaps]) if not gaps.is_empty else []):
        gb = gp.buffer(0.03)
        best, bv = None, 0
        for i, g in geoms.items():
            if g.is_empty:
                continue
            v = gb.intersection(g).area
            if v > bv:
                best, bv = i, v
        if best is not None:
            geoms[best] = polys_only(unary_union([geoms[best], gp]))
        elif gp.area > 2e-3:
            feats.append({"type": "Feature", "properties": {"polityId": "", "name": "", "extra": 1}, "geometry": mapping(gp)})
            geoms[len(feats) - 1] = gp
    out = []
    for i, f in enumerate(feats):
        g = geoms.get(i)
        if g is None or g.is_empty:
            continue
        f["geometry"] = mapping(g)
        out.append(f)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hb", required=True)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    hb = Path(a.hb)
    land = fix(unary_union([fix(shape(f["geometry"])) for f in
                            json.loads((REPO / "data/europe.geojson").read_text())["features"]])).intersection(BBOX)
    out_dir = REPO / "data" / "kingdom-eras" / "geo"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for era in ERAS:
        pack = json.loads((REPO / f"data/kingdom-eras/{era}.json").read_text())
        pols = pack["polities"]
        ov = OVERRIDES.get(era, {})
        tmp = Path(tempfile.mkdtemp())
        layer_files = []
        rep = report.setdefault(era, {})
        for tick in pack["ticks"]:
            y = tick["year"]
            fy = YEAR_FILE[era].get(y)
            hand = {}
            for p in pols:
                g = ext_geom((p.get("extentsByTick") or {}).get(str(y)))
                if g:
                    hand[p["id"]] = fix(shape(g)).intersection(land)
            feats = []
            if fy is None:
                for pid, g in hand.items():
                    g = polys_only(g)
                    if not g.is_empty:
                        feats.append({"type": "Feature", "properties": {"polityId": pid, "approx": 1}, "geometry": mapping(g)})
                rep[str(y)] = {"source": "hand-drawn (approximate)"}
            else:
                src = json.loads((hb / f"world_{fy}.geojson").read_text())["features"]
                items = []
                for f in src:
                    if not f.get("geometry"):
                        continue
                    g = fix(shape(f["geometry"]))
                    if not g.intersects(BBOX):
                        continue
                    g = polys_only(g.intersection(land))
                    if g.is_empty or g.area < 1e-4:
                        continue
                    items.append([f["properties"].get("NAME") or "", g])
                # fill coastal gaps (NE land not covered by dataset) into the neighbour sharing most edge
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
                # assign
                assigned, unmatched, used = {}, [], set()
                for name, g in items:
                    pid, how = None, None
                    if name in ov:
                        if ov[name] is None:
                            how = "ignored"
                        else:
                            for cand in ov[name]:
                                if cand in hand:
                                    pid, how = cand, "override"
                                    break
                    if how is None and name:
                        nt = norm(name)
                        best, bs = None, 0
                        for p in pols:
                            if p["id"] not in hand:
                                continue
                            pt = norm(p["name"]) | norm(p["id"].replace("-", " "))
                            if not nt or not pt:
                                continue
                            j = len(nt & pt) / len(nt | pt)
                            sp = g.intersection(hand[p["id"]]).area / g.area
                            s = j + sp * 0.5
                            if (j >= 0.99 or (j >= 0.3 and sp > 0.05)) and s > bs:
                                best, bs = p["id"], s
                        if best:
                            pid, how = best, "name"
                    if how is None:
                        best, bv = None, 0
                        for p_id, hg in hand.items():
                            v = g.intersection(hg).area / g.area
                            if v > bv:
                                best, bv = p_id, v
                        thr = 0.5 if (not name or best in UMBRELLA) else SPATIAL_THR[era]
                        if best and bv >= thr:
                            pid, how = best, f"spatial {bv:.2f}"
                    if pid:
                        assigned.setdefault(pid, []).append(g)
                        used.add(pid)
                        rep.setdefault(str(y), {}).setdefault("matched", []).append(f"{name} -> {pid} ({how})")
                    else:
                        unmatched.append(name)
                        feats.append({"type": "Feature", "properties": {"polityId": "", "name": name, "extra": 1}, "geometry": mapping(g)})
                missing = [p for p in hand if p not in used]
                # a missing polity first absorbs unmatched dataset polygons it mostly covers
                keep = []
                for f in feats:
                    g = shape(f["geometry"])
                    best, bv = None, 0
                    for pid in missing:
                        v = g.intersection(hand[pid]).area / max(g.area, 1e-12)
                        if v > bv:
                            best, bv = pid, v
                    if best and bv >= 0.35:
                        assigned.setdefault(best, []).append(g)
                        used.add(best)
                        rep.setdefault(str(y), {}).setdefault("matched", []).append(
                            f"{f['properties'].get('name','')} -> {best} (absorbed {bv:.2f})")
                    else:
                        keep.append(f)
                feats = keep
                missing = [p for p in hand if p not in used]
                # carve polities the dataset lacks out of their hand-drawn extent (approximate)
                geoms = {pid: polys_only(unary_union(gs)) for pid, gs in assigned.items()}
                carved, taken = {}, None
                for pid in sorted(missing, key=lambda k: hand[k].area):
                    g = polys_only(hand[pid])
                    if taken is not None:
                        g = polys_only(g.difference(taken))
                    if g.is_empty or g.area < 2e-3:
                        continue
                    carved[pid] = g
                    taken = g if taken is None else unary_union([taken, g])
                if taken is not None:
                    geoms = {k: polys_only(v.difference(taken)) for k, v in geoms.items()}
                    for f in feats:
                        f["geometry"] = mapping(polys_only(shape(f["geometry"]).difference(taken)))
                for pid, g in geoms.items():
                    if not g.is_empty:
                        feats.append({"type": "Feature", "properties": {"polityId": pid}, "geometry": mapping(g)})
                for pid, g in carved.items():
                    feats.append({"type": "Feature", "properties": {"polityId": pid, "approx": 1}, "geometry": mapping(g)})
                feats = [f for f in feats if f["geometry"]["coordinates"]]
                rep.setdefault(str(y), {})["carvedFromHandDrawn"] = sorted(carved)
                missing = [m for m in missing if m not in carved]
                r = rep.setdefault(str(y), {})
                r["source"] = f"historical-basemaps world_{fy}"
                r["unmatchedDatasetNames"] = sorted(set(n for n in unmatched))
                r["politiesWithoutDatasetGeometry"] = missing
            feats = tile(feats, land)
            fp = tmp / f"y{y}.json"
            fp.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
            layer_files.append(str(fp))
        out = out_dir / f"{era}.topo.json"
        cmd = ["npx", "--yes", "mapshaper", "-i", *layer_files, "combine-files",
               "-clean", "target=*", "-simplify", "8%", "keep-shapes", "planar",
               "-clean", "target=*", "gap-fill-area=500km2", "-filter-islands", "target=*", "min-area=40km2",
               "-o", str(out), "format=topojson", "quantization=100000"]
        subprocess.run(cmd, check=True)
        print(era, out.stat().st_size // 1024, "KB")
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
