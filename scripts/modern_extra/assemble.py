"""Patch data/kingdom-eras/modern.json with the 1920, 1938 and 1960 ticks,
the new polities in profiles.py and period names for existing polities.
Idempotent: re-running replaces what it added."""
import json, urllib.parse
from pathlib import Path
from profiles import P
from imgcheck import resolve
REPO = Path(__file__).resolve().parents[2]
F = REPO / "data/kingdom-eras/modern.json"
cache_f = Path(__file__).with_name("image_choices.json")
cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
FP = "https://commons.wikimedia.org/wiki/Special:FilePath/"
TICKS = [
 dict(year=1920, label="1920 AD", name="Versailles settlement", era="New republics, civil war in the east",
  narrative="By 1920 the peace treaties have dissolved Austria-Hungary and redrawn Central Europe: Poland, Czechoslovakia, the Kingdom of Serbs, Croats and Slovenes and the Baltic states are new or reborn, Germany is a republic shorn of territory, and Hungary has lost two-thirds of its land at Trianon. In the east the Bolsheviks are winning the civil war, fighting Poland and swallowing the short-lived Caucasian republics, while the Ottoman sultan accepts the Treaty of Sèvres that Kemal's nationalists reject."),
 dict(year=1938, label="1938 AD", name="Munich year", era="Dictatorships, Anschluss, appeasement",
  narrative="In 1938 most of Europe's new democracies have given way to dictatorships. Hitler annexes Austria in March and, at Munich in September, Britain and France agree to hand him the Sudetenland. Spain is in the third year of civil war, Stalin's purges are at their height, and Mussolini's Italy has conquered Ethiopia and joined the Axis."),
 dict(year=1960, label="1960 AD", name="Cold War Europe", era="Two Germanys, NATO and the Warsaw Pact",
  narrative="By 1960 Europe is divided by the Iron Curtain. West Germany is booming inside NATO and the new European Economic Community, while East Germany, Poland, Czechoslovakia, Hungary, Romania and Bulgaria are Soviet satellites. Yugoslavia goes its own way under Tito, Cyprus becomes independent from Britain, and the Berlin Wall is a year away."),
]
NAME_BY_TICK = {
 "ussr": {"1920": "Soviet Russia (RSFSR)"},
 "iceland": {"1920": "Kingdom of Iceland", "1938": "Kingdom of Iceland"},
 "yugoslavia": {"1920": "Kingdom of Serbs, Croats and Slovenes", "1938": "Kingdom of Yugoslavia",
                "1960": "Federal People's Republic of Yugoslavia"},
 "ottoman-empire": {"1920": "Ottoman Empire (Sultanate)"},
 "spain": {"1938": "Spain (Civil War)"},
 "italy": {"1920": "Kingdom of Italy", "1938": "Kingdom of Italy (Fascist)"},
 "ireland": {"1938": "Éire (Ireland)"},
 "austria": {"1920": "Republic of Austria"},
 "hungary": {"1920": "Kingdom of Hungary (Regency)", "1938": "Kingdom of Hungary (Regency)",
             "1960": "Hungarian People's Republic"},
 "poland": {"1920": "Second Polish Republic", "1938": "Second Polish Republic", "1960": "Polish People's Republic"},
 "romania": {"1920": "Greater Romania", "1938": "Kingdom of Romania", "1960": "Romanian People's Republic"},
 "albania": {"1938": "Kingdom of Albania", "1960": "People's Republic of Albania"},
 "portugal": {"1938": "Portugal (Estado Novo)", "1960": "Portugal (Estado Novo)"},
 "greece": {"1938": "Kingdom of Greece (Metaxas regime)", "1960": "Kingdom of Greece"},
 "bulgaria": {"1920": "Tsardom of Bulgaria", "1938": "Tsardom of Bulgaria", "1960": "People's Republic of Bulgaria"},
 "czechoslovakia": {"1960": "Czechoslovak Socialist Republic"},
 "united-kingdom": {"1920": "United Kingdom of Great Britain and Ireland"},
}
d = json.loads(F.read_text())
colors = {p["id"]: p.get("color") for p in d["polities"]}
new_ids = {p["id"] for p in P}
d["polities"] = [p for p in d["polities"] if p["id"] not in new_ids]
for p in d["polities"]:
    nb = {k: v for k, v in (p.get("nameByTick") or {}).items() if k not in ("1920", "1938", "1960")}
    nb.update(NAME_BY_TICK.get(p["id"], {}))
    if nb: p["nameByTick"] = nb
    else: p.pop("nameByTick", None)
for p in P:
    imgs = []
    for q, cap, role in p["images"]:
        f = cache.get(q)
        if f is None:
            f = resolve(q); cache[q] = f
        if f:
            imgs.append({"src": FP + urllib.parse.quote(f.replace("_", " ")) + "?width=640", "caption": cap, "alt": cap, "role": role})
    o = {k: v for k, v in p.items() if k not in ("images", "colorFrom", "story")}
    if p.get("colorFrom") and colors.get(p["colorFrom"]):
        o["color"] = colors[p["colorFrom"]]
    o.update(extentsByTick={}, story=p["story"][0]["text"], stories=p["story"], images=imgs,
             philosophy=p["ideas"], artIdeas=p["art"] + "\n\n" + p["ideas"])
    d["polities"].append(o)
cache_f.write_text(json.dumps(cache, indent=1, ensure_ascii=False))
ticks = [t for t in d["ticks"] if int(t["year"]) not in (1920, 1938, 1960)] + TICKS
d["ticks"] = sorted(ticks, key=lambda t: int(t["year"]))
d["notes"] = d["notes"].replace("1914 (July Crisis), 1945", "1914 (July Crisis), 1920 (Versailles settlement), 1938 (Munich year), 1945") \
                       .replace("1990 (reunification", "1960 (Cold War blocs), 1990 (reunification")
F.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print(len(d["polities"]), [t["year"] for t in d["ticks"]])

# Basemap profiles for named extras that first appear on the new ticks
BP = REPO / "data/kingdom-eras/basemap-profiles.json"
EXTRA_PROFILES = [
 {"id": "syria-mandate", "names": ["Syria (France)"], "name": "French Mandate for Syria and Lebanon", "type": "League of Nations mandate",
  "yearsActive": "1920–1946",
  "summary": "After the Ottoman defeat the League of Nations gave France a mandate over Syria and Lebanon. French troops ended Faisal's Arab Kingdom of Syria at Maysalun in July 1920, and France ruled through separate states until Syria and Lebanon became independent in 1943–46.",
  "description": "After the Ottoman defeat the League of Nations gave France a mandate over Syria and Lebanon. French troops ended Faisal's Arab Kingdom of Syria at Maysalun in July 1920, and France ruled through separate states until Syria and Lebanon became independent in 1943–46.",
  "conflicts": "Battle of Maysalun (1920); the Great Syrian Revolt (1925–27); the Hatay was ceded to Turkey in 1939.",
  "leaders": "High commissioners Henri Gouraud and Maurice Sarrail; nationalist leaders Sultan al-Atrash and Shukri al-Quwatli.",
  "religion": "Sunni Muslim majority with Alawite, Druze and Christian communities.", "culture": "Damascus, Aleppo and Beirut.",
  "story": "The 1925 revolt began in the Druze mountains under Sultan al-Atrash; French artillery shelled Damascus to suppress it.",
  "sources": ["Encyclopaedia Britannica, “Syria: The French mandate”", "P. S. Khoury, Syria and the French Mandate (1987)"],
  "when": ["modern:1920", "modern:1938"]},
 {"id": "iraq-mandate", "names": ["Mesopotamia (GB)"], "name": "British Mandate of Mesopotamia (Iraq)", "type": "League of Nations mandate",
  "yearsActive": "1920–1932",
  "summary": "Britain took the Ottoman provinces of Baghdad, Basra and Mosul in the First World War and governed them under a League mandate. After the 1920 revolt it made Faisal I king of Iraq in 1921; the kingdom became independent in 1932 but kept close treaty ties with Britain.",
  "description": "Britain took the Ottoman provinces of Baghdad, Basra and Mosul in the First World War and governed them under a League mandate. After the 1920 revolt it made Faisal I king of Iraq in 1921; the kingdom became independent in 1932 but kept close treaty ties with Britain.",
  "conflicts": "The Iraqi revolt of 1920; the Mosul question with Turkey, settled by the League in 1926.",
  "leaders": "Faisal I (king 1921–1933); Gertrude Bell and Percy Cox shaped the British administration.",
  "religion": "Shia and Sunni Muslims, with Kurdish, Christian, Jewish and Yazidi communities.", "culture": "Baghdad, Basra and Mosul.",
  "story": "Oil was struck at Baba Gurgur near Kirkuk in October 1927, and the gusher burned for over a week.",
  "sources": ["Encyclopaedia Britannica, “Iraq: The British mandate”", "C. Tripp, A History of Iraq (3rd ed. 2007)"],
  "when": ["modern:1920", "modern:1938"]},
]
bp = json.loads(BP.read_text())
ids = {e["id"] for e in EXTRA_PROFILES}
bp["profiles"] = [e for e in bp["profiles"] if e["id"] not in ids] + EXTRA_PROFILES
BP.write_text(json.dumps(bp, ensure_ascii=False, indent=1) + "\n")
