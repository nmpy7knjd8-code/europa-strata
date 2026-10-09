#!/usr/bin/env python3
"""Tag existing images with roles and add leader / religion photos."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "timeline.json"


def commons(filename: str, width: int = 800) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + quote(filename)
        + f"?width={width}"
    )


def img(filename: str, caption: str, role: str) -> dict:
    return {
        "src": commons(filename),
        "alt": caption,
        "caption": caption,
        "role": role,
    }


# Curated public Wikimedia assets
L = {
    "augustus": img(
        "Statue-Augustus.jpg",
        "Augustus of Prima Porta — Roman imperial portrait statue",
        "leader",
    ),
    "caesar": img(
        "Cesar-saalburg-2.jpg",
        "Julius Caesar (modern bust after ancient types)",
        "leader",
    ),
    "pericles": img(
        "Pericles Pio-Clementino Inv269.jpg",
        "Pericles — classical Athenian leader (Roman copy of Greek bust)",
        "leader",
    ),
    "alexander": img(
        "Alexander the Great mosaic.jpg",
        "Alexander the Great — Battle of Issus mosaic detail, Pompeii",
        "leader",
    ),
    "justinian": img(
        "Meister von San Vitale in Ravenna 003.jpg",
        "Justinian I — mosaic panel, San Vitale, Ravenna",
        "leader",
    ),
    "theodora": img(
        "Theodora mosaik san vitale.jpg",
        "Empress Theodora — mosaic panel, San Vitale, Ravenna",
        "leader",
    ),
    "charlemagne": img(
        "Charlemagne statue at St. Peter's Basilica.jpg",
        "Charlemagne — statue at St. Peter’s Basilica, Vatican",
        "leader",
    ),
    "alfred": img(
        "King Alfred the Great - Statue in Wantage.jpg",
        "Alfred the Great — statue in Wantage",
        "leader",
    ),
    "cnut": img(
        "Cnut the Great - MS Royal 14 B VI.jpg",
        "Cnut the Great — medieval manuscript portrait",
        "leader",
    ),
    "william": img(
        "Bayeux Tapestry scene23 William.jpg",
        "William of Normandy — Bayeux Tapestry",
        "leader",
    ),
    "frederick": img(
        "Friedrich II. und Adler.jpg",
        "Frederick II — medieval depiction with imperial eagle",
        "leader",
    ),
    "louis_ix": img(
        "Saint Louis.jpg",
        "Louis IX (Saint Louis) — French royal saint-king portrait type",
        "leader",
    ),
    "isabella": img(
        "Isabel la Católica (Juan de Barroeta).jpg",
        "Isabella I of Castile — portrait",
        "leader",
    ),
    "charles_v": img(
        "Kaiser Karl V. mit Hund (Jakob Seisenegger) - Kunsthistorisches Museum Wien.jpg",
        "Charles V — Habsburg emperor with dog (Seisenegger)",
        "leader",
    ),
    "elizabeth": img(
        "Elizabeth I Armada Portrait British School.jpg",
        "Elizabeth I — Armada Portrait",
        "leader",
    ),
    "luther": img(
        "Martin Luther by Cranach-restoration.jpg",
        "Martin Luther — Cranach portrait",
        "leader",
    ),
    "philip_ii": img(
        "Portrait of Philip II of Spain by Sofonisba Anguissola - 002b.jpg",
        "Philip II of Spain — Sofonisba Anguissola",
        "leader",
    ),
    "suleiman": img(
        "EmperorSuleiman.jpg",
        "Suleiman the Magnificent — Ottoman imperial portrait",
        "leader",
    ),
    "gustav_vasa": img(
        "Gustav Vasa.jpg",
        "Gustav Vasa — founder of modern Swedish monarchy",
        "leader",
    ),
    "napoleon": img(
        "Jacques-Louis David - The Emperor Napoleon in His Study at the Tuileries - Google Art Project.jpg",
        "Napoleon in His Study — Jacques-Louis David",
        "leader",
    ),
    "sutton_hoo": img(
        "Sutton Hoo helmet 2016.png",
        "Sutton Hoo helmet — Migration-age royal regalia",
        "leader",
    ),
    "theodoric_tomb": img(
        "Mausoleum of Theodoric (Ravenna) - Exterior.jpg",
        "Mausoleum of Theodoric, Ravenna — Ostrogothic royal tomb",
        "leader",
    ),
    "vladimir": img(
        "Vladimir the Great.jpg",
        "Vladimir the Great — Kievan Rus’ baptizer (later icon type)",
        "leader",
    ),
    "attila": img(
        "Attila by Delacroix.jpg",
        "Attila — later romantic depiction (not a contemporary portrait)",
        "leader",
    ),
}

R = {
    "stonehenge": img(
        "Stonehenge Heel Stone.jpg",
        "Stonehenge — Atlantic megalithic ritual landscape",
        "religion",
    ),
    "sun_chariot": img(
        "Solvogn bagside.jpg",
        "Trundholm sun chariot — Nordic Bronze Age ritual object",
        "religion",
    ),
    "kurgan": img(
        "Kurgan stelae, Tanais.jpg",
        "Kurgan / steppe stelae — burial and ritual monuments",
        "religion",
    ),
    "pantheon": img(
        "Pantheon Rome 04 2016 6410.jpg",
        "Pantheon, Rome — Roman temple architecture",
        "religion",
    ),
    "parthenon": img(
        "The Parthenon in Athens.jpg",
        "Parthenon, Athens — classical temple",
        "religion",
    ),
    "mithras": img(
        "CIMRM 415, Mithras tauroctony from Rome, Baths of Trajan.jpg",
        "Mithras tauroctony relief — Roman mystery cult ritual scene",
        "religion",
    ),
    "pantocrator": img(
        "Christ Pantocrator mosaic from Hagia Sophia 2744 x 2900 pixels 3.1 MB.jpg",
        "Christ Pantocrator — mosaic, Hagia Sophia",
        "religion",
    ),
    "san_vitale": img(
        "Ravenna San Vitale interior.jpg",
        "San Vitale, Ravenna — early Byzantine church interior",
        "religion",
    ),
    "book_kells": img(
        "KellsFol032vChristEnthroned.jpg",
        "Book of Kells — Christ Enthroned folio (Insular Gospel art)",
        "religion",
    ),
    "jelling": img(
        "Jelling stones. Denmark.JPG",
        "Jelling stones — Danish royal Christian conversion monument",
        "religion",
    ),
    "chartres": img(
        "Chartres - cathédrale - ND de la belle verrière.jpg",
        "Chartres Cathedral — stained glass (Notre-Dame de la Belle Verrière)",
        "religion",
    ),
    "alhambra": img(
        "Patio de los Leones (Alhambra, Granada).jpg",
        "Court of the Lions, Alhambra — Nasrid Islamic palace-ritual architecture",
        "religion",
    ),
    "cordoba": img(
        "Mosque–Cathedral of Córdoba (Spain) 03.jpg",
        "Mosque–Cathedral of Córdoba — hypostyle prayer hall",
        "religion",
    ),
    "reliquary": img(
        "Karlsschrein Frontseite.JPG",
        "Shrine of Charlemagne — medieval Christian reliquary",
        "religion",
    ),
    "icon_rublev": img(
        "Rublev Trinity.jpg",
        "Rublev’s Trinity — Orthodox icon",
        "religion",
    ),
    "luther_theses": img(
        "95Thesen.jpg",
        "Ninety-five Theses — Reformation print culture",
        "religion",
    ),
    "st_peters": img(
        "St. Peter's Basilica facade, Rome, Italy.jpg",
        "St. Peter’s Basilica — Counter-Reformation Rome",
        "religion",
    ),
    "uppsala": img(
        "Gamla Uppsala burial mounds.jpg",
        "Gamla Uppsala mounds — northern ritual/burial landscape",
        "religion",
    ),
    "celtic_cauldron": img(
        "Gundestrupkedlen-0001.jpg",
        "Gundestrup cauldron — Iron Age ritual vessel",
        "religion",
    ),
    "scythian_gold": img(
        "Scythian gold pectoral Tovsta Mohyla (detail 4).jpg",
        "Scythian gold pectoral — elite ritual / funerary metalwork",
        "religion",
    ),
    "nebra": img(
        "Nebra Scheibe.jpg",
        "Nebra sky disc — Bronze Age cosmographic ritual object",
        "religion",
    ),
}

# periodId -> iso -> {leaders: [keys], religion: [keys]}
ASSIGN = {
    "middle-neolithic": {
        "GBR": {"religion": ["stonehenge"]},
        "IRL": {"religion": ["stonehenge"]},
        "FRA": {"religion": ["stonehenge"]},
        "ESP": {"religion": ["stonehenge"]},
        "DNK": {"religion": ["stonehenge"]},
        "SWE": {"religion": ["stonehenge"]},
    },
    "yamnaya": {
        "UKR": {"religion": ["kurgan"]},
        "RUS": {"religion": ["kurgan"]},
        "MDA": {"religion": ["kurgan"]},
        "ROU": {"religion": ["kurgan"]},
    },
    "beaker-corded": {
        "GBR": {"religion": ["stonehenge"]},
        "DEU": {"religion": ["nebra"]},
        "DNK": {"religion": ["nebra"]},
        "SWE": {"religion": ["nebra"]},
        "POL": {"religion": ["nebra"]},
    },
    "nordic-bronze": {
        "DNK": {"religion": ["sun_chariot"]},
        "SWE": {"religion": ["sun_chariot", "uppsala"]},
        "NOR": {"religion": ["sun_chariot"]},
        "DEU": {"religion": ["nebra"]},
    },
    "iron-age": {
        "FRA": {"religion": ["celtic_cauldron"]},
        "DEU": {"religion": ["celtic_cauldron"]},
        "DNK": {"religion": ["celtic_cauldron"]},
        "GBR": {"religion": ["celtic_cauldron"]},
        "UKR": {"religion": ["scythian_gold"]},
        "GRC": {"leaders": ["pericles"], "religion": ["parthenon"]},
        "ITA": {"religion": ["parthenon"]},
    },
    "classical": {
        "ITA": {"leaders": ["augustus"], "religion": ["pantheon"]},
        "GBR": {"leaders": ["augustus"], "religion": ["mithras"]},
        "FRA": {"leaders": ["augustus"], "religion": ["mithras"]},
        "ESP": {"leaders": ["augustus"], "religion": ["pantheon"]},
        "DEU": {"leaders": ["augustus"], "religion": ["mithras"]},
        "GRC": {"leaders": ["pericles", "augustus"], "religion": ["parthenon"]},
        "TUR": {"leaders": ["augustus"], "religion": ["pantheon"]},
    },
    "migration": {
        "ITA": {"leaders": ["theodoric_tomb", "justinian"], "religion": ["san_vitale"]},
        "GBR": {"leaders": ["sutton_hoo"], "religion": ["book_kells"]},
        "FRA": {"leaders": ["sutton_hoo"], "religion": ["san_vitale"]},
        "ESP": {"leaders": ["theodoric_tomb"], "religion": ["san_vitale"]},
        "DEU": {"leaders": ["sutton_hoo"], "religion": ["san_vitale"]},
        "UKR": {"leaders": ["attila"], "religion": ["scythian_gold"]},
        "GRC": {"leaders": ["justinian", "theodora"], "religion": ["pantocrator"]},
        "TUR": {"leaders": ["justinian"], "religion": ["pantocrator"]},
    },
    "frankish": {
        "FRA": {"leaders": ["charlemagne"], "religion": ["reliquary"]},
        "DEU": {"leaders": ["charlemagne"], "religion": ["reliquary"]},
        "ITA": {"leaders": ["charlemagne"], "religion": ["san_vitale"]},
        "GBR": {"leaders": ["alfred"], "religion": ["book_kells"]},
        "ESP": {"leaders": ["charlemagne"], "religion": ["cordoba"]},
        "DNK": {"leaders": ["cnut"], "religion": ["jelling"]},
        "SWE": {"religion": ["uppsala", "jelling"]},
        "NOR": {"religion": ["jelling"]},
    },
    "vikings": {
        "GBR": {"leaders": ["cnut", "alfred"], "religion": ["jelling"]},
        "DNK": {"leaders": ["cnut"], "religion": ["jelling"]},
        "NOR": {"leaders": ["cnut"], "religion": ["jelling"]},
        "SWE": {"leaders": ["cnut"], "religion": ["uppsala", "jelling"]},
        "FRA": {"leaders": ["william"], "religion": ["reliquary"]},
        "UKR": {"leaders": ["vladimir"], "religion": ["icon_rublev"]},
        "GRC": {"leaders": ["justinian"], "religion": ["pantocrator"]},
        "TUR": {"leaders": ["justinian"], "religion": ["pantocrator"]},
        "ITA": {"leaders": ["charlemagne"], "religion": ["pantocrator"]},
        "DEU": {"leaders": ["charlemagne"], "religion": ["reliquary"]},
        "ESP": {"religion": ["cordoba", "alhambra"]},
    },
    "high-medieval": {
        "GBR": {"leaders": ["william"], "religion": ["chartres"]},
        "FRA": {"leaders": ["louis_ix"], "religion": ["chartres"]},
        "DEU": {"leaders": ["frederick"], "religion": ["reliquary"]},
        "ITA": {"leaders": ["frederick"], "religion": ["st_peters"]},
        "ESP": {"leaders": ["isabella"], "religion": ["alhambra", "cordoba"]},
        "GRC": {"leaders": ["justinian"], "religion": ["pantocrator"]},
        "TUR": {"religion": ["pantocrator"]},
        "POL": {"religion": ["icon_rublev"]},
        "UKR": {"leaders": ["vladimir"], "religion": ["icon_rublev"]},
        "SWE": {"religion": ["uppsala"]},
        "DNK": {"religion": ["jelling"]},
    },
    "late-medieval": {
        "GBR": {"leaders": ["elizabeth"], "religion": ["chartres"]},
        "FRA": {"leaders": ["louis_ix"], "religion": ["chartres"]},
        "ESP": {"leaders": ["isabella"], "religion": ["alhambra"]},
        "DEU": {"leaders": ["charles_v"], "religion": ["reliquary"]},
        "ITA": {"religion": ["st_peters"]},
        "TUR": {"leaders": ["suleiman"], "religion": ["pantocrator"]},
        "GRC": {"leaders": ["suleiman"], "religion": ["pantocrator"]},
        "POL": {"religion": ["icon_rublev"]},
        "UKR": {"religion": ["icon_rublev"]},
    },
    "reformation": {
        "DEU": {"leaders": ["luther", "charles_v"], "religion": ["luther_theses"]},
        "GBR": {"leaders": ["elizabeth"], "religion": ["luther_theses"]},
        "FRA": {"leaders": ["charles_v"], "religion": ["luther_theses"]},
        "ESP": {"leaders": ["philip_ii", "charles_v"], "religion": ["st_peters"]},
        "ITA": {"leaders": ["charles_v"], "religion": ["st_peters"]},
        "SWE": {"leaders": ["gustav_vasa"], "religion": ["luther_theses"]},
        "DNK": {"leaders": ["luther"], "religion": ["luther_theses"]},
        "NOR": {"leaders": ["luther"], "religion": ["luther_theses"]},
        "POL": {"leaders": ["luther"], "religion": ["luther_theses"]},
        "TUR": {"leaders": ["suleiman"], "religion": ["pantocrator"]},
        "GRC": {"leaders": ["suleiman"], "religion": ["pantocrator"]},
    },
    "early-modern": {
        "FRA": {"leaders": ["napoleon"], "religion": ["st_peters"]},
        "GBR": {"leaders": ["elizabeth"], "religion": ["st_peters"]},
        "ESP": {"leaders": ["philip_ii"], "religion": ["st_peters"]},
        "DEU": {"leaders": ["charles_v"], "religion": ["luther_theses"]},
        "ITA": {"religion": ["st_peters"]},
        "SWE": {"leaders": ["gustav_vasa"], "religion": ["luther_theses"]},
        "TUR": {"leaders": ["suleiman"], "religion": ["pantocrator"]},
        "GRC": {"leaders": ["suleiman"], "religion": ["pantocrator"]},
        "POL": {"religion": ["icon_rublev"]},
        "UKR": {"religion": ["icon_rublev"]},
    },
    "modern": {
        "FRA": {"leaders": ["napoleon"], "religion": ["st_peters"]},
        "ITA": {"religion": ["st_peters", "pantheon"]},
        "GBR": {"religion": ["st_peters"]},
        "GRC": {"religion": ["parthenon"]},
        "TUR": {"religion": ["pantocrator"]},
    },
}


def infer_role(img: dict) -> str:
    if img.get("role"):
        return img["role"]
    t = f"{img.get('caption','')} {img.get('alt','')} {img.get('src','')}".lower()
    if any(
        k in t
        for k in (
            "augustus",
            "charlemagne",
            "theodoric",
            "sutton hoo",
            "helmet",
            "portrait",
            "statue",
            "bust",
            "emperor",
            "prima porta",
            "luther",
            "elizabeth",
            "napoleon",
            "caesar",
            "pericles",
            "justinian",
            "theodora",
            "william",
            "cnut",
            "alfred",
            "suleiman",
            "philip",
            "charles v",
            "gustav",
            "vladimir",
            "attila",
            "isabella",
            "frederick",
            "louis",
        )
    ):
        return "leader"
    if any(
        k in t
        for k in (
            "altar",
            "icon",
            "temple",
            "pantocrator",
            "cathedral",
            "mosque",
            "church",
            "gospel",
            "kells",
            "bible",
            "ritual",
            "kurgan",
            "sun chariot",
            "megalith",
            "stonehenge",
            "reliqu",
            "hagia",
            "chartres",
            "alhambra",
            "jelling",
            "pantheon",
            "parthenon",
            "mithras",
            "cauldron",
            "nebra",
            "sky disc",
            "trinity",
            "theses",
        )
    ):
        return "religion"
    if any(
        k in t
        for k in (
            "book",
            "manuscript",
            "folio",
            "tapestry",
            "chronicle",
            "poem",
            "dante",
            "shakespeare",
            "venus",
            "meninas",
            "monet",
        )
    ):
        return "literature"
    return "art"


def merge_images(existing: list[dict], extra: list[dict]) -> list[dict]:
    seen = {e.get("src") for e in existing if e.get("src")}
    out = list(existing)
    for e in extra:
        if e["src"] in seen:
            # upgrade role if we have a stronger curated role
            for old in out:
                if old.get("src") == e["src"]:
                    old["role"] = e.get("role") or old.get("role") or infer_role(old)
                    if e.get("caption"):
                        old.setdefault("caption", e["caption"])
                        old.setdefault("alt", e["alt"])
            continue
        out.append(e)
        seen.add(e["src"])
    return out


def main() -> None:
    data = json.loads(PATH.read_text())
    added = 0
    tagged = 0
    for period in data["periods"]:
        pid = period["id"]
        table = ASSIGN.get(pid, {})
        for iso, pol in (period.get("polities") or {}).items():
            images = pol.get("images") or []
            for im in images:
                before = im.get("role")
                im["role"] = infer_role(im)
                if im["role"] != before:
                    tagged += 1
            spec = table.get(iso) or table.get("*")
            if not spec:
                pol["images"] = images
                continue
            extras: list[dict] = []
            for key in spec.get("leaders") or []:
                extras.append(dict(L[key]))
            for key in spec.get("religion") or []:
                extras.append(dict(R[key]))
            before_n = len(images)
            images = merge_images(images, extras)
            added += max(0, len(images) - before_n)
            pol["images"] = images
    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Tagged/updated roles on {tagged} images; added {added} leader/religion images.")


if __name__ == "__main__":
    main()
