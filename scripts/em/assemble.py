import json, sys, urllib.parse
from pathlib import Path
from part4 import P
from enrich import E as ENRICH
from imgcheck import resolve
REPO=Path(__file__).resolve().parents[2]
cache_f=Path(__file__).with_name('image_choices.json')
cache=json.loads(cache_f.read_text()) if cache_f.exists() else {}
TICKS=[
 dict(year=400,label="400 AD",name="Late Roman twilight",era="Two Roman empires, Huns on the Danube",
  narrative="In 400 the Roman Empire is split between Honorius in the West and Arcadius in the East. The Huns rule the steppe and Hungarian plain, pushing Goths and others toward the Roman frontier. Within a decade the Rhine will be crossed and Rome sacked; for now Persia remains Rome's equal in the east."),
 dict(year=500,label="500 AD",name="Successor kingdoms",era="Ostrogoths, Visigoths, Franks, Vandals",
  narrative="By 500 the Western Empire is gone. Theodoric's Ostrogoths rule Italy, the Visigoths Spain and southern Gaul, Clovis's Franks northern Gaul, the Vandals Africa, while Anglo-Saxons settle Britain. Constantinople still claims to rule them all."),
 dict(year=600,label="600 AD",name="Justinian's aftermath",era="Lombards, Avars, Slavs, Merovingians",
  narrative="Justinian's reconquests have exhausted Byzantium. Lombards hold much of Italy, the Avars rule the Carpathian Basin and Slavs are settling the Balkans. Merovingian kings rule Gaul and Gregory the Great's mission has reached Kent."),
 dict(year=700,label="700 AD",name="The Arab century",era="Umayyads, Khazars, Bulgars",
  narrative="Arab armies have taken Persia, Syria, Egypt and most of North Africa; in eleven years they will cross into Spain. Bulgars have settled south of the Danube, the Khazars rule the steppe, and Slavic tribes fill eastern Europe."),
 dict(year=800,label="800 AD",name="Charlemagne's empire",era="Carolingians, Abbasids, Vikings",
  narrative="On Christmas Day 800 Charlemagne is crowned emperor in Rome, ruling from the Pyrenees to the Elbe. The Abbasids rule from Baghdad, an Umayyad emir rules Córdoba, and Viking ships have begun raiding Britain and Ireland."),
 dict(year=900,label="900 AD",name="Fragmented Francia",era="Vikings, Magyars, Rus, Bulgarian Empire",
  narrative="The Carolingian empire has split into West, East and Middle Francia. Magyars have taken the Carpathian Basin, Rus princes rule Kyiv and Novgorod, Alfred's heirs are reconquering England, and Simeon's Bulgaria rivals Byzantium."),
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
    p={**p, **ENRICH.get(p['id'],{})}
    d={k:v for k,v in p.items() if k!='images'}
    d.update(images=imgs, extentsByTick={}, stories=p['story'], philosophy=p['ideas'], artIdeas=p['art']+"\n\n"+p['ideas'])
    pols.append(d)
cache_f.write_text(json.dumps(cache,indent=1,ensure_ascii=False))
pack={"tabId":"early-medieval","tabLabel":"Early Medieval","defaultYear":600,"ticks":TICKS,
 "notes":"Early Medieval polities, 400–900 AD. Borders from historical-basemaps (A. Ourednik, GPL-3.0), clipped to Natural Earth land; large unnamed dataset areas are assigned only where the people are well attested, the rest is left unassigned. Peoples and tribal confederations had fluid, not linear, borders. Sources: Encyclopaedia Britannica; P. Heather, The Fall of the Roman Empire; C. Wickham, The Inheritance of Rome (2009); per-polity sources in each profile's 'sources' field.",
 "polities":pols}
(REPO/'data/kingdom-eras/early-medieval.json').write_text(json.dumps(pack,ensure_ascii=False,indent=1))
print(len(pols))
