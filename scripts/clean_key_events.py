"""One-off cleanup of data/key-events.json (review-fixes).
Strips generated boilerplate, adds titles, numeric years, fixes errors,
drops vague thematic entries, sorts chronologically."""
import json, re, pathlib
P = pathlib.Path(__file__).resolve().parent.parent / "data/key-events.json"
src = json.loads(P.read_text())
ALL = ["iberia","britain","france","central","scandinavia","italy","balkans","eastern"]
DROP = {("yamnaya",7),("beaker-corded",8),("classical",7),("high-medieval",8),("early-modern",6)}
MOVE = {("early-modern",7):"modern",("early-modern",8):"modern"}
TITLES = {
"early-modern":["Edict of Nantes","Thirty Years' War","Peace of Westphalia","Revocation of the Edict of Nantes","Glorious Revolution","Great Northern War",None,"French Revolution","Congress of Vienna"],
"modern":["Industrial Revolution","Revolutions and national unifications","First World War","Second World War and the Holocaust","Iron Curtain and two German states","Treaties of Rome","Fall of communism","Maastricht Treaty","Euro and EU enlargement"],
"iron-age":["Hallstatt Iron Age begins","Greeks found Massalia","Jastorf culture in the north","Hallstatt princely seats","Roman Republic founded (traditional)","Hallstatt collapse, La Tène rises","Herodotus describes the Scythians","Gauls sack Rome","Galatian invasion of Greece"],
"classical":["First Punic War","Second Punic War","Carthage and Corinth destroyed","Caesar's Gallic Wars","Actium and the Principate","Battle of the Teutoburg Forest","Roman conquest of Britain",None],
"migration":["Wielbark expansion","Chernyakhov culture","Battle of Adrianople","Visigoths sack Rome","Adventus Saxonum (traditional)","Battle of the Catalaunian Plains","End of the Western Empire","Ostrogothic Italy","Wielbark networks collapse"],
"frankish":["Battle of Soissons","Baptism of Clovis","Battle of Tours/Poitiers","Pepin founds the Carolingians","Saxon Wars","Charlemagne crowned emperor","Treaty of Verdun","Viking raids escalate","Slavic mission and Bulgarian conversion"],
"vikings":["Normandy founded","Battle of Lechfeld","Poland, Hungary and Rus' convert","Hugh Capet elected","Iceland adopts Christianity","Battle of Clontarf","Cnut's North Sea empire","Battle of Stiklestad","1066: Stamford Bridge and Hastings"],
"high-medieval":["First Crusade","Canossa and the Investiture Contest","Frederick Barbarossa","Fourth Crusade sacks Constantinople","Las Navas de Tolosa","Magna Carta","Albigensian Crusade","Mongol invasion",None],
"late-medieval":["Hundred Years' War","Black Death","Western Schism","Battle of Kosovo","Battle of Grunwald","Agincourt and Joan of Arc","Fall of Constantinople","Gutenberg's press","Golden Bull"],
"reformation":["Luther's Ninety-Five Theses","Diet of Worms","German Peasants' War","Act of Supremacy","Calvin's Geneva","Council of Trent","Ivan IV crowned tsar","Peace of Augsburg","Abdication of Charles V"],
}
FIX = {
("yamnaya",2): dict(date="c. 4100–3000 BC", title="Late Trypillia megasites and Usatove contact",
  detail="Classic Cucuteni–Trypillia megasites of the forest-steppe flourish c. 4100–3600 BC and then wind down. Later, c. 3500–3000 BC, the Usatove group near the northwest Black Sea forms from a roughly even mix of steppe-related (CLV-derived) and Trypillian farmer ancestry, as North Pontic foragers, farmers, and pastoralists meet in overlapping pulses."),
("yamnaya",4): dict(title="Yamnaya expand to the Danube and Carpathian Basin"),
("reformation",0): dict(detail="Martin Luther circulates the Ninety-Five Theses against indulgence abuses (traditionally said to be posted on the Wittenberg church door, a detail historians debate), the conventional spark of the Protestant Reformation in the Empire."),
("reformation",1): dict(detail="At the Diet of Worms, Luther refuses to recant before Charles V; the Edict of Worms outlaws him, while print and princely protection spread his cause."),
}
REGIONS = {("high-medieval",0):["france","italy","central"],("late-medieval",1):ALL,("modern",2):ALL,("modern",8):ALL,("modern",3):ALL}
SPECIAL={"late 3rd–4th c. AD":(270,399),"9 AD":(9,9),"25 Dec 800 AD":(800,800),"c. 390/387 BC":(-390,-387),"c. 860s–880s AD":(860,889),"793–840s AD":(793,849)}
def years(d):
    if d in SPECIAL: return SPECIAL[d]
    s = d.replace("–","-").replace("/", "-")
    bc = "BC" in s
    m = re.search(r"(\d{1,2})(st|nd|rd|th) c\.", s)
    nums = [int(x) for x in re.findall(r"\d{2,4}", s)]
    if "mid-18th" in s: return 1740,1760
    if "mid-5th" in s: return 440,460
    if m and not nums:
        c=int(m.group(1)); a=(c-1)*100; b=c*100-1
        return (-b,-a) if bc else (a,b)
    if "late 3rd" in s: return 270,399
    if "12th" in s: return 1100,1299
    if "1st c." in s: return 1,99
    if "5th c. BC" in s: return -499,-400
    nums=[n for n in nums if n>=10 or True]
    a=nums[0]; b=nums[-1] if len(nums)>1 else a
    if len(nums)>1 and b<100 and a>100 and not bc: b=(a//100)*100+b  # 1700-21 style
    if bc: a,b=-a,-b
    if "s AD" in s or re.search(r"\d0s",s): b=b+9 if b>0 else b
    return min(a,b),max(a,b)
out = {}
for pid, pp in src["periods"].items():
    for i, e in enumerate(pp["keyEvents"]):
        if (pid,i) in DROP: continue
        tgt = MOVE.get((pid,i), pid)
        body = (e.get("detail") or e.get("text") or "").split("\n\n")[0].strip()
        title = e.get("title") or (TITLES.get(pid) or [None]*20)[i]
        ev = {"date": e["date"], "title": title, "detail": body}
        ev.update(FIX.get((pid,i), {}))
        regs = REGIONS.get((pid,i)) or e.get("regions") or ([e["region"]] if e.get("region") else [])
        ev["regions"] = regs
        if e.get("iso"): ev["iso"] = e["iso"]
        ev["start"], ev["end"] = years(ev["date"])
        assert ev["title"], (pid,i)
        out.setdefault(tgt, []).append(ev)
res = {"version": 3, "periods": {}}
for pid, evs in out.items():
    evs.sort(key=lambda e:(e["start"], e["end"]))
    res["periods"][pid] = {"periodId": pid, "keyEvents": evs}
P.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
for pid,pv in res["periods"].items():
    evs=pv["keyEvents"]
    print(pid, [(e["date"], e["start"], e["end"]) for e in evs])
