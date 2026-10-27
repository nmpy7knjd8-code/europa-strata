"""Deepen thin 1815/1914 basemap profiles and fix an off-topic Genoa image (data only)."""
import json, urllib.parse
from pathlib import Path
R = Path(__file__).resolve().parent.parent
def img(f, cap, role):
    return {"src": "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(f) + "?width=640",
            "caption": cap, "alt": cap, "role": role}
B = "Encyclopaedia Britannica"
E = {
 "brunswick": dict(
  d="A Guelph duchy in Lower Saxony, restored in 1813 after six years inside Napoleon’s Kingdom of Westphalia. Its ‘Black Duke’ fell at Quatre Bras in 1815; a revolt in 1830 drove out his son Charles II and burned the Braunschweig palace. Brunswick joined the North German Confederation in 1867 and the German Empire in 1871.",
  story="In 1809 Duke Frederick William led his black-uniformed ‘Black Brunswickers’ on a fighting march across Germany to the North Sea and escaped to England; they returned to fight in Spain and at Waterloo. Millais painted the legend in The Black Brunswicker (1860).",
  imgs=[img("William Corden the Younger (1819-1900) - Frederick William, Duke of Brunswick and Wolfenbüttel (1771-1815) - RCIN 404134 - Royal Collection.jpg","Frederick William, the ‘Black Duke’ of Brunswick","leader"),
        img("John Everett Millais The Black Brunswicker.jpg","Millais, The Black Brunswicker (1860)","art")],
  src=[f"{B}, “Brunswick”", f"{B}, “Frederick William, duke of Brunswick”"]),
 "hamburg": dict(
  d="Hamburg was a free Hanseatic city and became a sovereign member of the German Confederation in 1815. Annexed by France in 1810 and besieged under Marshal Davout in 1813–14, it rebuilt as Germany’s largest port. A great fire destroyed much of the old town in 1842, and the city joined the German customs union only in 1888.",
  story="Hamburg is still a city-state of Germany today. Its neo-Renaissance Rathaus, finished in 1897, was built for a senate that still governs the city.",
  imgs=[img("Hamburg, Rathaus -- 2016 -- 4175.jpg","Hamburg Rathaus, seat of the senate","culture"),
        img("Alsterblick Hamburg.jpg","Hamburg across the Alster","story")],
  src=[f"{B}, “Hamburg”"]),
 "bremen": None, "lubeck": None,
}
E["bremen"] = dict(
  d="A free Hanseatic city on the Weser that kept its sovereignty in the German Confederation in 1815. Because the river was silting up, Bremen bought land at the Weser mouth and founded Bremerhaven in 1827, which became one of Europe’s main emigrant ports to America.",
  story="The stone Roland of 1404 in front of the town hall stood for the city’s liberties; the Rathaus and Roland are a UNESCO World Heritage Site (2004).",
  imgs=[img("Bremen, Roland -- 2021 -- 6347.jpg","Bremen’s Roland statue (1404)","culture"),
        img("Bremen, Rathaus -- 2021 -- 6357.jpg","Bremen town hall","art")],
  src=[f"{B}, “Bremen”", "UNESCO World Heritage List, “Town Hall and Roland on the Marketplace of Bremen”"])
E["lubeck"] = dict(
  d="The former ‘Queen of the Hanse’, Lübeck was occupied by the French after the battle of Lübeck in 1806 and annexed to France in 1811. Restored as a free city in 1815, it kept its independence until Prussia absorbed it in 1937.",
  story="Thomas Mann, born in Lübeck in 1875, drew on its merchant families for Buddenbrooks (1901). The Holstentor gate of 1478 still guards the old town.",
  imgs=[img("Holstentor in Lübeck 2015.jpg","Holstentor, Lübeck (1478)","culture")],
  src=[f"{B}, “Lübeck”"])
E["krakow"] = dict(
  d="A free city under the joint protection of Austria, Prussia and Russia, created at the Congress of Vienna in 1815. With the Jagiellonian University and a small rural territory, it was the last independent fragment of Poland. Austria annexed it as the Grand Duchy of Kraków after the uprising of 1846.",
  story="It was the last independent Polish territory before 1918. In the February 1846 uprising the radical Edward Dembowski was killed leading a procession against Austrian troops.",
  imgs=[img("Edward Dembowski during Kraków Uprising 1846.PNG","Edward Dembowski in the Kraków Uprising, 1846","story"),
        img("Coat of arms of the Kraków Uprising.svg","Emblem of the 1846 Kraków Uprising","culture")],
  src=[f"{B}, “Kraków”", "N. Davies, God’s Playground: A History of Poland, vol. 2 (1981)"])
E["lucca"] = dict(
  d="A duchy created at the Congress of Vienna for Maria Luisa of Bourbon, the former queen of Etruria, as compensation until Parma passed to her line. Her son Charles Louis ruled from 1824; in 1847 he ceded Lucca to Tuscany and took Parma.",
  story="Lucca’s Renaissance walls survive intact and were turned into a tree-lined public promenade in the nineteenth century.",
  imgs=[img("Queen of Etruria Maria Luisa with her son Charles Louis.jpg","Maria Luisa of Bourbon with her son Charles Louis","leader"),
        img("Lucca.city walls01.jpg","The walls of Lucca","culture")],
  src=[f"{B}, “Lucca”"])
E["hesse-kassel"] = dict(
  d="The Electorate of Hesse (Kurhessen), restored in 1813 under Elector William I. Its rulers kept the title of elector even after the Holy Roman Empire had gone. It sided with Austria in 1866 and was annexed by Prussia.",
  story="The Brothers Grimm worked in Kassel while collecting their fairy tales. Wilhelmshöhe palace later held the captured Napoleon III in 1870–71.",
  imgs=[img("11-10-15-kassel-by-RalfR-19.jpg","Wilhelmshöhe, Kassel","art")],
  src=[f"{B}, “Hesse-Kassel”"])
E["hesse-darmstadt"] = dict(
  d="The Grand Duchy of Hesse, a grand duchy since 1806, gained Rhenish Hesse with Mainz in 1816 and received a constitution in 1820. It joined the German Empire in 1871.",
  story="Under Grand Duke Ernst Ludwig, Darmstadt’s Mathildenhöhe artists’ colony (founded 1899) became a centre of Jugendstil.",
  imgs=[img("Darmstadt-Schloss Marktplatz.jpg","Residenzschloss, Darmstadt","culture")],
  src=[f"{B}, “Hesse”"])
E["nassau"] = dict(
  d="The Duchy of Nassau (1806–1866), ruled from Wiesbaden and the riverside palace of Biebrich. It backed Austria in 1866 and was annexed by Prussia.",
  story="Its last duke, Adolphe, became Grand Duke of Luxembourg in 1890, which is why Luxembourg’s ruling house is still Nassau.",
  imgs=[img("Schloss Biebrich, Wiesbaden-Biebrich, 150905, ako.jpg","Biebrich Palace, seat of the dukes of Nassau","culture")],
  src=[f"{B}, “Nassau”"])
E["oldenburg"] = dict(
  d="A North Sea duchy annexed by France in 1811 and restored in 1813; it was raised to a grand duchy in 1815. It joined the German Empire in 1871 and kept its grand dukes until 1918.",
  imgs=[img("Schloss Oldenburg um 1840.jpg","Oldenburg palace, c. 1840","culture")],
  src=[f"{B}, “Oldenburg”"])
E["meck-schwerin"] = dict(
  d="A Baltic grand duchy from 1815. It kept its old Estates constitution of 1755 and had no modern written constitution until 1918.",
  story="Schwerin Castle, rebuilt in 1845–57 on its island in the lake, became the showpiece of the grand dukes.",
  imgs=[img("Schwerin Castle (1).jpg","Schwerin Castle","art")],
  src=[f"{B}, “Mecklenburg”"])
E["lippe"] = dict(
  d="The Principality of Lippe, ruled from Detmold in the Teutoburg Forest, survived as a sovereign member of the German Confederation and the German Empire until 1918.",
  story="The Hermannsdenkmal near Detmold, finished in 1875, honours Arminius’s victory over Rome in AD 9.",
  imgs=[img("Detmold - Residenzschloss 640.jpg","Residenzschloss, Detmold","culture")],
  src=[f"{B}, “Lippe”"])
E["waldeck"] = dict(
  d="The Principality of Waldeck, ruled from Arolsen, was a tiny member of the German Confederation. From 1868 Prussia ran its administration by treaty while its princes kept the throne.",
  imgs=[img("Schloss Arolsen 20100622.jpg","Arolsen palace, seat of the princes of Waldeck","culture")],
  src=[f"{B}, “Waldeck”"])
E["iceland-1914"] = dict(
  d="Iceland in 1914 was under the Danish crown with home rule. The Althing was restored as an advisory body in 1845 and given legislative powers in 1874; home rule came in 1904 with Hannes Hafstein as minister. Iceland became a sovereign kingdom in personal union with Denmark in 1918 and a republic in 1944.",
  story="Jón Sigurðsson (1811–1879) led the campaign for self-government; his birthday, 17 June, is Iceland’s national day.",
  imgs=[img("Portrait of Jón Sigurdsson.jpg","Jón Sigurðsson, leader of the independence movement","leader"),
        img("Alþingishúsið.jpg","Althing house, Reykjavík (1881)","culture")],
  src=[f"{B}, “Iceland: History”"])

p = R / "data/kingdom-eras/basemap-profiles.json"
data = json.loads(p.read_text())
for prof in data["profiles"]:
    e = E.get(prof["id"])
    if not e: continue
    prof["summary"] = prof["description"] = e["d"]
    if "story" in e: prof["story"] = e["story"]
    prof["images"] = e["imgs"]
    for s in e["src"]:
        if s not in prof["sources"]: prof["sources"].append(s)
p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")

p = R / "data/kingdom-eras/early-modern.json"
raw = p.read_text(); data = json.loads(raw)
g = next(x for x in data["polities"] if x["id"] == "genoa")
g["images"] = [im for im in g["images"] if "Rembrandt" not in im["src"]]
g["images"].insert(2, img("Sir Peter Paul Rubens - Marchesa Brigida Spinola Doria - Google Art Project.jpg",
                          "Rubens, Marchesa Brigida Spinola Doria (1606) — Genoese patrician portrait", "art"))
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
