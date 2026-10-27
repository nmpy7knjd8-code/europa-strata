#!/usr/bin/env python3
"""Add detail (images, story vignettes, fuller summaries) to the thinnest
High Medieval / Renaissance profiles. Data only; uses existing fields.
Idempotent: re-running replaces the same fields with the same values."""
import json, pathlib, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
FP = "https://commons.wikimedia.org/wiki/Special:FilePath/"

def img(file, caption, role, width=640):
    return {"src": f"{FP}{urllib.parse.quote(file)}?width={width}", "caption": caption, "alt": caption, "role": role}

def st(title, text):
    return {"title": title, "text": text}

BASEMAP = {
 "bosnia-1400": dict(
  summary="Ban Tvrtko I had himself crowned king in 1377 and for a time also ruled much of the Dalmatian coast. Silver and lead mines such as Srebrenica made Bosnia rich, and Ragusan merchants carried its ore to the Adriatic. After Tvrtko died in 1391 great nobles held the real power. The Ottomans conquered the kingdom in 1463 and executed its last king.",
  culture="Carved stećci tombstones; Bosnian Cyrillic (bosančica) charters; mining towns worked by Saxon miners and Ragusan traders.",
  stories=[st("Stećci", "Thousands of stećci still stand across Bosnia. Radimlja near Stolac is among the best-known cemeteries."),
           st("The silver town", "Srebrenica takes its name from silver (srebro); its mines fed Ragusan and Venetian trade."),
           st("The last king", "Stephen Tomašević surrendered at Ključ in 1463 and was executed on Mehmed II’s orders.")],
  images=[img("Radimlja necropolis near Stolac.JPG", "Radimlja necropolis — stećci tombstones near Stolac", "culture"),
          img("Zlatnik - Tvrtko I Kotromanić.jpg", "Gold coin of Tvrtko I — Bosnia’s first king", "leader")]),
 "kazan": dict(
  summary="Kazan was a Tatar khanate on the middle Volga, founded around 1438 by Ulugh Muhammad, a deposed khan of the Golden Horde. It controlled Volga trade and raided Muscovite lands, while Moscow repeatedly tried to place its own candidates on the throne. Ivan IV stormed Kazan in 1552 and annexed the khanate.",
  stories=[st("St Basil’s", "St Basil’s Cathedral on Red Square was built in 1555–1561 to celebrate Ivan IV’s capture of Kazan."),
           st("Kingmakers in Moscow", "From the 1480s Moscow repeatedly installed and removed khans in Kazan before choosing conquest.")],
  images=[img("Facial Chronicle - b.21, p. 264 - Kazan.jpg", "Kazan in the Illustrated Chronicle of Ivan IV", "story"),
          img("Söyembikä Tower in 2018.jpg", "Kazan Kremlin and the Söyembikä Tower", "culture")]),
 "mamluks": dict(
  stories=[st("Ain Jalut", "In 1260 Qutuz and Baybars defeated a Mongol army in Galilee, the Mongols’ first major defeat in the region."),
           st("Sultan Hasan’s mosque", "The vast Mosque-Madrasa of Sultan Hasan in Cairo was built in 1356–1363, soon after the Black Death."),
           st("Qaitbay’s fort", "Qaitbay built a fortress at Alexandria in 1477 on the site of the ruined Pharos lighthouse.")],
  images=[img("Mosque-Madrassa of Sultan Hassan.jpg", "Mosque-Madrasa of Sultan Hasan, Cairo (1356–1363)", "religion"),
          img("Citadel of Qaitbay 014.JPG", "Citadel of Qaitbay, Alexandria (1477)", "art")]),
 "trebizond": dict(
  stories=[st("Last of the Greek empires", "Trebizond outlasted Constantinople by eight years and surrendered to Mehmed II in 1461."),
           st("Marriage diplomacy", "Trebizond’s princesses married Turkmen rulers; Theodora Komnene became the wife of Uzun Hasan of the Aq Qoyunlu.")],
  images=[img("Fresco of Comneni at Agia Theotokos, near Trebizond - Texier Charles - 1864.jpg", "Komnenian rulers in a church fresco near Trebizond (drawn 1864)", "leader"),
          img("Fresco in apse of St. Sophia's, Trebizond.jpg", "Apse fresco of Hagia Sophia, Trebizond (drawn 1864)", "religion")]),
 "georgia-medieval": dict(
  stories=[st("The Knight in the Panther’s Skin", "Shota Rustaveli’s epic dates from Tamar’s reign."),
           st("Gelati", "David the Builder founded Gelati monastery in 1106 as a centre of learning; he is buried at its gate.")],
  images=[img("Tamar's fresco at Vardzia.jpg", "Queen Tamar in the Vardzia cave-monastery fresco", "leader"),
          img("Gelati Monastery 1.jpg", "Gelati monastery, founded by David the Builder (1106)", "religion")]),
 "timurids": dict(
  stories=[st("Ankara", "In 1402 Timur defeated and captured the Ottoman sultan Bayezid I, nearly breaking the young Ottoman state."),
           st("The astronomer-prince", "Ulugh Beg’s observatory at Samarkand was built in the 1420s; its star catalogue was among the most accurate before the telescope.")],
  images=[img("Gur-e Amir 01.jpg", "Gur-e Amir, Timur’s mausoleum in Samarkand", "art"),
          img("Ulugh Beg Observatory 01.jpg", "Remains of Ulugh Beg’s observatory, Samarkand", "science")]),
 "bulgaria-medieval": dict(
  stories=[st("Tarnovo", "Ivan Asen II’s Tarnovo was a centre of Slavic Orthodox learning."),
           st("Boyana", "The frescoes of Boyana Church near Sofia, dated 1259, are a landmark of medieval Bulgarian painting.")],
  images=[img("Tsarevets Veliko Tarnovo.jpg", "Tsarevets hill, Tarnovo — fortress of the Second Bulgarian Empire", "culture"),
          img("Boyana Church Mural Paintings.jpg", "Boyana Church murals (1259)", "art")]),
 "brittany": dict(
  stories=[st("Two French crowns", "Anne of Brittany married Charles VIII and then Louis XII of France."),
           st("Nantes castle", "Duke Francis II rebuilt the castle at Nantes from 1466, and Anne continued the work.")],
  images=[img("NantesChateau 08.jpg", "Château des ducs de Bretagne, Nantes", "culture")]),
 "toulouse": dict(
  stories=[st("Muret", "In 1213 Simon de Montfort defeated Peter II of Aragon and Raymond VI at Muret; Peter was killed."),
           st("The stone that killed Montfort", "Simon de Montfort was killed besieging Toulouse in 1218, reportedly by a stone from a siege engine."),
           st("Carcassonne", "The crusaders took Carcassonne in 1209, early in the Albigensian Crusade.")],
  images=[img("Seal of Raymond VII, comte de Toulouse.png", "Seal of Raymond VII, count of Toulouse", "leader"),
          img("Carcassonne Cite.jpg", "Carcassonne, taken by the crusaders in 1209 (walls much restored)", "story")]),
 "volga-bulgaria": dict(
  stories=[st("Ibn Fadlan", "Ibn Fadlan’s report on his journey also describes the Rus traders he met."),
           st("Bolghar after the Mongols", "Bolghar was rebuilt under the Golden Horde; most of its standing ruins date from that later period.")],
  images=[img("Small minaret, Bolgar.JPG", "Ruins at Bolghar (Golden Horde period, 1300s)", "culture")]),
 "cyprus-medieval": dict(
  stories=[st("Last Latin kingdom", "Lusignan Cyprus outlived the fall of Acre in 1291 and became the last Latin kingdom of the crusader East."),
           st("Bellapais", "The Gothic abbey of Bellapais was built mainly in the 1200s and 1300s under Lusignan patronage.")],
  images=[img("Bellapais Abbey Cyprus.jpg", "Bellapais Abbey — Lusignan Gothic", "religion"),
          img("Kolossi Castle 01.JPG", "Kolossi Castle, Hospitaller keep rebuilt in 1454", "culture")]),
 "ilkhanate": dict(
  stories=[st("A world history", "Rashid al-Din’s world history was written for the Ilkhans."),
           st("Soltaniyeh", "Öljeitü built a new capital at Soltaniyeh; his domed mausoleum there was completed around 1312.")],
  images=[img("Dome of Soltaniyeh, 2010.jpg", "Mausoleum of Öljeitü, Soltaniyeh (c. 1312)", "art")]),
 "croatia-1100": dict(
  stories=[st("Baška tablet", "The Baška tablet (c. 1100) is one of the oldest Croatian inscriptions, written in Glagolitic and naming King Zvonimir.")],
  images=[img("Bascanska ploca.jpg", "Baška tablet (c. 1100), Glagolitic inscription", "literature")]),
}

RENAISSANCE_IMAGES = {
 "navarre": [img("Palacio de Olite.JPG", "Royal palace of Olite — court of Charles III the Noble", "art")],
 "spanish-netherlands": [img("Museum Plantin-Moretus Printing Press.jpg", "Plantin’s Antwerp printing house (now Museum Plantin-Moretus)", "science")],
}

def main():
    bp = ROOT / "data/kingdom-eras/basemap-profiles.json"
    d = json.loads(bp.read_text(encoding="utf-8"))
    by = {p["id"]: p for p in d["profiles"]}
    for pid, add in BASEMAP.items():
        p = by[pid]
        for k, v in add.items():
            p[k] = v
            if k == "summary":
                p["description"] = v
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rp = ROOT / "data/kingdom-eras/renaissance.json"
    r = json.loads(rp.read_text(encoding="utf-8"))
    for p in r["polities"]:
        for im in RENAISSANCE_IMAGES.get(p["id"], []):
            if im["src"] not in [i["src"] for i in p["images"]]:
                p["images"].append(im)
    rp.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
