"""Move long prose (region + deep-time polity text) out of data/timeline.json into
data/timeline-text/<period>.json, loaded lazily by js/app.js (ensurePeriodText)."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent / "data"
HEAVY = ("images", "description", "story", "stories", "science", "philosophy", "art", "ideas", "literature")
tl = json.loads((R / "timeline.json").read_text())
out_dir = R / "timeline-text"; out_dir.mkdir(exist_ok=True)
for p in tl["periods"]:
    txt = {"periodId": p["id"], "regions": {}, "polities": {}}
    for group in ("regions", "polities"):
        for k, obj in (p.get(group) or {}).items():
            moved = {f: obj.pop(f) for f in HEAVY if f in obj}
            if moved:
                txt[group][k] = moved
    (out_dir / f"{p['id']}.json").write_text(json.dumps(txt, ensure_ascii=False) + "\n")
(R / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2) + "\n")
