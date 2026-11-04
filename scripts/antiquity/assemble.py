import json, sys, urllib.parse
from pathlib import Path
from part4 import P
from imgcheck import resolve
REPO=Path(__file__).resolve().parents[2]
cache_f=Path(__file__).with_name('image_choices.json')
cache=json.loads(cache_f.read_text()) if cache_f.exists() else {}
TICKS=[
 dict(year=-500,label="500 BC",name="Persia and the poleis",era="Achaemenids, Greek cities, Carthage, Etruscans",
  narrative="In 500 BC Darius I rules the largest empire yet seen, reaching into Europe in Thrace. Athens has just become a democracy, Carthage controls the western sea lanes, the Etruscans dominate central Italy and Rome is a young republic. Celtic, Germanic and Scythian peoples fill the lands to the north."),
 dict(year=-323,label="323 BC",name="Death of Alexander",era="Alexander's empire, Celts, Rome rising",
  narrative="Alexander dies in Babylon in June 323 BC, master of an empire from Greece to the Indus. His generals will soon carve it up. In the west Carthage holds Spain's coast and Sardinia, Rome is fighting the Samnites for central Italy, and Celts have settled from Britain to the Danube."),
 dict(year=-200,label="200 BC",name="Rome after Hannibal",era="Rome, Hellenistic kingdoms, Scythians",
  narrative="Rome has just defeated Hannibal (202 BC) and taken Carthage's Spanish lands. In the east the Antigonids, Seleucids, Ptolemies and Attalids of Pergamon contest the Hellenistic world, and Rome is about to intervene. Scythians hold the steppe, Norse farmers Scandinavia."),
 dict(year=-1,label="1 BC",name="Augustan peace",era="Roman Empire, Parthia, Germania",
  narrative="Augustus rules the Mediterranean world as first emperor and is pushing toward the Elbe. Parthia holds Iran and Mesopotamia, Armenia is contested between them, and the Odrysian kings of Thrace and the Bosporan kings are Roman clients. Germanic, Dacian and Sarmatian peoples lie beyond the frontier."),
 dict(year=100,label="100 AD",name="The Pax Romana",era="Trajan, Dacia, Parthia",
  narrative="Trajan has just become emperor and will soon conquer Dacia. The Roman frontier runs along the Rhine and Danube, with Britain held up to the Caledonian north. Goths live on the Vistula, Sarmatians and Alans on the steppe, Parthia remains Rome's eastern rival."),
 dict(year=300,label="300 AD",name="The Tetrarchy",era="Diocletian's four rulers, Sasanian Persia",
  narrative="Diocletian has divided imperial rule among four emperors after the crisis of the third century. Dacia has been abandoned to the Goths, who now hold the Black Sea steppe. The Sasanian Persians have replaced the Parthians, and Armenia has just become the first Christian kingdom."),
]
FP="https://commons.wikimedia.org/wiki/Special:FilePath/"
pols=[]; changed=False
for p in P:
    imgs=[]
    for q,cap,role in p['images']:
        f=cache.get(q)
        if f is None:
            f=resolve(q); cache[q]=f; changed=True
        if f: imgs.append({"src":FP+urllib.parse.quote(f.replace('_',' '))+"?width=800","caption":cap,"alt":cap,"role":role})
    d={k:v for k,v in p.items() if k!='images'}
    d.update(images=imgs, extentsByTick={}, stories=p['story'], philosophy=p['ideas'], artIdeas=p['art']+"\n\n"+p['ideas'])
    pols.append(d)
cache_f.write_text(json.dumps(cache,indent=1,ensure_ascii=False))
pack={"tabId":"antiquity","tabLabel":"Antiquity","defaultYear":-323,"ticks":TICKS,
 "notes":"Antiquity polities, 500 BC–AD 300. Borders from historical-basemaps (A. Ourednik, GPL-3.0), clipped to Natural Earth land; large unnamed dataset areas are assigned only where the people are well attested, the rest is left unassigned. Tribal peoples and archaeological cultures had fluid, not linear, borders. Sources: Encyclopaedia Britannica; The Cambridge Ancient History; M. Beard, SPQR (2015); B. Cunliffe, Europe Between the Oceans (2008); per-polity sources in each profile's 'sources' field.",
 "polities":pols}
(REPO/'data/kingdom-eras/antiquity.json').write_text(json.dumps(pack,ensure_ascii=False,indent=1))
print(len(pols))
