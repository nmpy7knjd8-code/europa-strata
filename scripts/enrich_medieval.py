#!/usr/bin/env python3
"""Insert medieval+ timeline periods and enrich polity/region detail."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "timeline.json"

REGION_IDS = [
    "iberia",
    "britain",
    "france",
    "central",
    "scandinavia",
    "italy",
    "balkans",
    "eastern",
]


def deep(o):
    return copy.deepcopy(o)


def layer(id_, label, color, countries, role="dominant", opacity=0.82, note=""):
    return {
        "id": id_,
        "label": label,
        "color": color,
        "countries": countries,
        "role": role,
        "opacity": opacity,
        "note": note,
    }


def polity(name, summary, conflicts, leaders="", religion="", culture="", story=""):
    return {
        "name": name,
        "summary": summary,
        "conflicts": conflicts,
        "leaders": leaders,
        "religion": religion,
        "culture": culture,
        "story": story,
    }


def enrich_polity(p: dict, **fields):
    p = deep(p)
    for k, v in fields.items():
        if v:
            p[k] = v
    # Ensure keys exist
    for k in ("leaders", "religion", "culture", "story"):
        p.setdefault(k, "")
    return p


def bump_desc(region: dict, text: str):
    region = deep(region)
    region["description"] = text
    return region


# ——— New periods built from neighbors ———

def make_vikings(frankish, high):
    """c. 1000 AD — Viking Age peak, Capetians, Ottonians, Cordoba fall, early Piasts."""
    p = deep(frankish)
    p.update(
        {
            "id": "vikings",
            "label": "Viking Age & Millennium Kingdoms",
            "era": "North Sea, Capetians, Ottonians",
            "yearLabel": "c. 1000 AD",
            "yearApprox": 1000,
            "tickYear": "1000 AD",
            "narrative": (
                "Around the year 1000, Europe’s map is a patchwork of consolidating Christian kingdoms "
                "and still-pagan or newly converted frontiers. The Viking Age peaks and turns toward "
                "settlement and royal conversion (Denmark, Norway, Sweden; Danelaw memory in England; "
                "Normandy; Dublin). West Francia is Capetian; East Francia is Ottonian/Salian Holy Roman "
                "Empire; Cordoba’s caliphate fragments into taifas; Byzantium under the Macedonian dynasty "
                "is a high medieval power; Piast Poland and Árpád Hungary enter Latin Christendom; "
                "Kievan Rus’ Christianizes under Vladimir. Genetics remain early-medieval continua — "
                "the drama is kingship, conversion, and saga, not a new deep ancestry component."
            ),
            "culturesNote": (
                "Cnut’s North Sea empire forming; Capetian France; Ottonian–Salian Reich; "
                "taifa Iberia; Macedonian Byzantium; Piast Poland; Kievan Rus’; Normandy."
            ),
            "linguistics": (
                "Old Norse / emerging Scandinavian vernaculars; Old English late West Saxon; "
                "Old French; Old High German / Latin chancery; Arabic & Romance in Iberia; "
                "Greek; Church Slavonic & Old East Slavic; Latin liturgy across the west."
            ),
        }
    )

    # Regions — longer descriptions
    base_r = high["regions"]  # closer culturally for some; blend with frankish ancestry
    fr = frankish["regions"]
    p["regions"] = {
        "iberia": bump_desc(
            fr["iberia"],
            "The Umayyad Caliphate of Córdoba collapses after 1031 into rival taifa kingdoms while "
            "northern Christian realms — León–Castile, Navarre, Catalonia/Aragon, Portugal’s County — "
            "press the frontier of the Reconquista. Arabic learning, Hebrew poetry, and Romance speech "
            "interleave in cities; Mozarabic Christians and Jewish communities mediate culture. "
            "Demographically still an early-medieval mix with North African layers in the south — "
            "politics and confession, not a new Paleolithic strand, define the age.",
        ),
        "britain": bump_desc(
            fr["britain"],
            "England after Alfred’s heirs faces renewed Norse pressure; Æthelred’s failures set the stage "
            "for Swein and Cnut. The Danelaw’s legal and linguistic imprint persists even as West Saxon "
            "kingship claims the island. Scotland’s Alba, Welsh kingdoms, and Irish polities (with Norse "
            "towns like Dublin) form a North Atlantic chessboard of raid, ransom, and royal baptism. "
            "Stories of Olaf Tryggvason, Brian Boru (Clontarf 1014), and English martyr-kings sit atop "
            "an Anglo-Saxon–Brittonic–Norse gene pool already in place.",
        ),
        "france": bump_desc(
            fr["france"],
            "Hugh Capet’s dynasty (from 987) holds a modest royal demesne around Paris while great "
            "princes — Normandy, Flanders, Aquitaine, Toulouse, Anjou — dwarf the crown in practice. "
            "Viking Normandy has become a Latin-Christian duchy launching energy into England and the "
            "Mediterranean. Monasteries (Cluny’s reform orbit) reshape piety; Romance speech hardens "
            "toward Old French. Ancestry is Frankish-era continuity; the novelty is Capetian sacral kingship "
            "and feudal fragmentation.",
        ),
        "central": bump_desc(
            fr["central"],
            "The Ottonian and early Salian emperors claim Rome and the Reich: stem duchies, Italian "
            "expeditions, and Slavic marches (Billungs, early eastward pressure). Bohemia under the "
            "Přemyslids and Poland under Bolesław Chrobry negotiate baptism, imperial recognition, and "
            "frontier war. Magyars, settled since the 10th century, become a Christian kingdom under "
            "Stephen I (crowned 1000/1001). Latin Christendom’s eastern edge is being drawn in real time.",
        ),
        "scandinavia": bump_desc(
            fr["scandinavia"],
            "Denmark, Norway, and Sweden crystallize as kingdoms amid late Viking expeditions. Conversion "
            "from above (Harold Bluetooth’s claim; Olaf Tryggvason; Olaf Haraldsson / St Olaf) collides "
            "with local cults and jarl power. Longships still reach the British Isles, Normandy’s kin, "
            "and the eastern rivers toward Rus’. Sagas later remember this as the heroic age — "
            "archaeogenetics sees continuity from earlier Nordic Iron/Viking samples, not a continent-wide replacement.",
        ),
        "italy": bump_desc(
            fr["italy"],
            "Northern Italy is a mosaic of imperial cities, marches, and Lombard memory under Ottonian "
            "oversight; Rome’s papacy is a prize in imperial politics; the south remains Byzantine and, "
            "in Sicily, under Islamic rule heading toward Norman conquest in the next century. "
            "Trade revival begins in Venetian and Amalfitan circuits. Latin, Greek, and Arabic zones "
            "overlap; ancestry is late antique–early medieval Italian continua.",
        ),
        "balkans": bump_desc(
            fr["balkans"],
            "Byzantium under Basil II (the ‘Bulgar-slayer’) breaks the First Bulgarian Empire and briefly "
            "reasserts Balkan hegemony, even as Slavic and Albanian-speaking countrysides persist beneath "
            "Greek administration. Croatia and other west Balkan polities navigate papacy, Byzantium, and "
            "Hungary. Orthodox liturgy and Church Slavonic shape Slavic Christian culture. Genetics track "
            "Balkan early-medieval mixes; the story is imperial reconquest and conversion.",
        ),
        "eastern": bump_desc(
            fr["eastern"],
            "Kievan Rus’ under Vladimir the Great adopts Byzantine Christianity (c. 988), tying the Dnieper "
            "route to Constantinople’s prestige. Pechenegs and steppe neighbors press the forest-steppe edge; "
            "Varangian legends still color elite identity. Further east and south, Khazar afterlives and "
            "Turkic steppe politics continue. Deep ancestry remains steppe–farmer–forager ternary with "
            "eastern mobility — the millennium’s change is baptism and princely federation.",
        ),
    }
    # keep ancestry from frankish (already in bump_desc copies)

    p["mapLayers"] = [
        layer("england-late-as", "Late Anglo-Saxon England", "#3a4a5a", ["GBR"], "dominant"),
        layer("celtic-fringe-v", "Celtic kingdoms", "#5a6a4a", ["IRL", "GBR"], "fringe", 0.45),
        layer("normandy", "Normandy", "#2a3a4a", ["FRA"], "incoming", 0.55),
        layer("capetian-v", "Capetian royal France", "#1a1a1a", ["FRA", "BEL"], "dominant", 0.7),
        layer("ottonian", "Ottonian–Salian Reich", "#4a3a2a", ["DEU", "AUT", "CHE", "NLD", "BEL", "LUX", "CZE"], "dominant"),
        layer("piast", "Piast Poland", "#6a4a3a", ["POL"], "dominant"),
        layer("hungary-stephen", "Árpád Hungary", "#7a5a3a", ["HUN", "SVK"], "dominant"),
        layer("denmark-v", "Kingdom of Denmark", "#3f5a6a", ["DNK"], "dominant"),
        layer("norway-v", "Kingdom of Norway", "#2f4a5a", ["NOR"], "dominant"),
        layer("sweden-v", "Kingdom of Sweden", "#4f6a7a", ["SWE"], "dominant"),
        layer("taifa", "Andalusi taifas", "#5a4a2a", ["ESP"], "dominant", 0.75),
        layer("christian-north", "Christian northern Iberia", "#4a5a3a", ["ESP", "PRT"], "incoming", 0.55),
        layer("byz-macedonian", "Macedonian Byzantium", "#5a2a3a", ["GRC", "BGR", "MKD", "ALB", "TUR"], "dominant"),
        layer("kievan", "Kievan Rus’", "#6a3a3a", ["UKR", "BLR", "RUS"], "dominant"),
        layer("croatia-v", "Croatian realm", "#5a4a4a", ["HRV", "BIH"], "dominant", 0.7),
        layer("italy-imperial", "Imperial & communal Italy", "#4a4a4a", ["ITA"], "dominant", 0.65),
        layer("sicily-islamic", "Islamic Sicily (late)", "#5a4a3a", ["ITA"], "fringe", 0.4),
    ]

    p["polities"] = VIKINGS_POLITIES
    return p


def make_late_medieval(high, early):
    """c. 1400 AD — HYW, Black Death aftermath, Ottoman rise, PLC forming."""
    p = deep(high)
    p.update(
        {
            "id": "late-medieval",
            "label": "Late Medieval",
            "era": "Plague, dynasties, Ottomans",
            "yearLabel": "c. 1400 AD",
            "yearApprox": 1400,
            "tickYear": "1400 AD",
            "narrative": (
                "The later Middle Ages open under the shadow of the Black Death (from 1347) and close "
                "toward gunpowder states and Renaissance courts. England and France bleed through the "
                "Hundred Years’ War; the Avignon papacy and Schism fracture Latin Christendom’s prestige; "
                "Burgundy flowers as a princely superpower; Iberian crowns push Granada; the Ottomans "
                "cross into Europe and crush Serbian and Byzantine power toward 1453; Poland and Lithuania "
                "join in personal union against the Teutonic Order and the steppe; Muscovy gathers Russian "
                "lands after the Golden Horde’s weakening. Culture: Gothic perpendicular and Flamboyant, "
                "vernacular literature (Chaucer, Dante’s afterlife, chivalric orders), and intensified "
                "devotional religion. Genetics: plague kills on a vast scale but does not invent new deep "
                "components — regional continua persist with mobility along war and trade."
            ),
            "culturesNote": (
                "Hundred Years’ War realms; Burgundy; Crown of Aragon & Castile; Holy Roman mosaic; "
                "Jagiellon Poland–Lithuania; Ottoman Rumelia; Muscovy; Italian city-states."
            ),
            "linguistics": (
                "Middle English rising in state use; Middle French; Early New High German; "
                "Italian vernaculars vs Latin; Castilian/Catalan/Portuguese; Church Slavonic & Ruthenian; "
                "Ottoman Turkish administration over Greek/Slavic/Albanian speakers."
            ),
        }
    )

    hr = high["regions"]
    er = early["regions"]
    p["regions"] = {
        "iberia": bump_desc(
            hr["iberia"],
            "Castile and Aragon (with Catalonia and Valencia) dominate Christian Iberia; Portugal is an "
            "Atlantic kingdom; Nasrid Granada survives as Islam’s last Iberian foothold under tribute and "
            "raid. Courtly culture mixes crusading ideology with Mediterranean commerce. Jewish and Muslim "
            "minorities remain crucial — and increasingly precarious — to urban economies. Ancestry is "
            "medieval Iberian continua with North African and earlier layers; politics is dynastic union "
            "building toward the Catholic Monarchs.",
        ),
        "britain": bump_desc(
            hr["britain"],
            "Plantagenet and then Lancastrian England fights for the French crown while Welsh revolt "
            "(Owain Glyndŵr) and Scottish wars flare. The Black Death empties manors and raises labor’s "
            "price; vernacular English (Chaucer) claims literary prestige beside French and Latin. "
            "Ireland remains a patchwork of English pale and Gaelic lordships. Genetics: plague mortality "
            "and mobility, not a new ancestral strand — continuity from high medieval Britain with "
            "aristocratic French ties.",
        ),
        "france": bump_desc(
            hr["france"],
            "Valois France fractures under English occupation, civil war (Armagnac–Burgundian), and "
            "Jacquerie social revolt, then slowly reconsolidates with gunpowder, taxes, and Joan of Arc’s "
            "mythic campaign. Burgundy’s dukes build a glittering state from Flanders to the Jura. "
            "Cathedrals, mystery plays, and royal sacral ideology define culture. Demography rebounds "
            "unevenly after plague on a Frankish–medieval French gene pool.",
        ),
        "central": bump_desc(
            hr["central"],
            "The Holy Roman Empire is elective and plural: Luxemburg and early Habsburg emperors, "
            "Bohemian crown lands heading toward Hussite revolution, Swiss confederate victories, "
            "Teutonic Order vs Poland–Lithuania (Grünwald/Tannenberg 1410). German towns of the Hansa "
            "knit the Baltic. Latin and German law, Gothic art, and university theology (Prague, Vienna) "
            "shape elite culture. Ancestry: central European medieval continua.",
        ),
        "scandinavia": bump_desc(
            hr["scandinavia"],
            "The Kalmar Union (from 1397) binds Denmark, Norway, and Sweden under one monarch in theory, "
            "with Swedish resistance never far away. Hanseatic merchants dominate Bergen and Baltic trade; "
            "Norwegian royal power wanes. Christianity is firmly Latin; vernacular laws and sagas persist "
            "in manuscript. Genetics track Nordic medieval populations — union is political, not a population replacement.",
        ),
        "italy": bump_desc(
            hr["italy"],
            "Visconti Milan, republican Florence, papal states, Naples, and maritime Venice/Genoa invent "
            "Renaissance patronage even before 1400’s end — humanism, vernacular epic, and mercenary "
            "condottieri. The south remains an Angevin then Aragonese prize. Urban density and plague "
            "shape demography; ancestry is Italian medieval continua with eastern Mediterranean trade contacts.",
        ),
        "balkans": bump_desc(
            hr["balkans"],
            "Serbian power peaks then falters (Kosovo 1389 in memory and politics); Bulgaria fragments; "
            "Byzantium is a rump around Constantinople; Ottoman beys and sultans take Gallipoli, Adrianople, "
            "and push north. Orthodox churches keep Slavic and Greek literacy under rising Islamic rule. "
            "This is conquest and conversion pressure on Balkan medieval ancestries — a political–religious "
            "transformation with gene flow along armies and slave routes, not a Mesolithic reset.",
        ),
        "eastern": bump_desc(
            hr["eastern"],
            "The Golden Horde’s grip loosens; Moscow’s princes collect lands ‘of Rus’’ while Lithuania "
            "rules vast Ruthenian Orthodox populations under a pagan-then-Catholic elite. Jogaila’s union "
            "with Poland (1386) creates a dual realm facing Teutonic and Muscovite rivals. Steppe politics "
            "still matter; deep genetics remain eastern European continua with Turkic–Mongol elite layers.",
        ),
    }

    p["mapLayers"] = [
        layer("england-hyw", "Lancastrian / late Plantagenet England", "#3a5a48", ["GBR"], "dominant"),
        layer("scotland-lm", "Kingdom of Scotland", "#4a6a58", ["GBR"], "fringe", 0.45),
        layer("ireland-lm", "Gaelic & English Ireland", "#5a6a4a", ["IRL"], "dominant", 0.7),
        layer("france-valois", "Valois France", "#2a2a2a", ["FRA", "BEL"], "dominant", 0.75),
        layer("burgundy", "Burgundian lands", "#4a2a3a", ["FRA", "BEL", "NLD", "LUX"], "incoming", 0.55),
        layer("hre-lm", "Holy Roman Empire", "#5a4a3a", ["DEU", "AUT", "CHE", "CZE", "NLD", "BEL"], "dominant", 0.7),
        layer("poland-lith", "Poland–Lithuania (union)", "#6a4a2a", ["POL", "LTU", "BLR", "UKR"], "dominant", 0.75),
        layer("kalmar", "Kalmar Union Scandinavia", "#3f5a6a", ["DNK", "NOR", "SWE"], "dominant", 0.8),
        layer("castile-lm", "Crown of Castile", "#7a5a2a", ["ESP"], "dominant", 0.7),
        layer("aragon-lm", "Crown of Aragon", "#6a4a3a", ["ESP", "ITA"], "incoming", 0.5),
        layer("portugal-lm", "Kingdom of Portugal", "#5a6a3a", ["PRT"], "dominant"),
        layer("granada-lm", "Nasrid Granada", "#5a4a2a", ["ESP"], "fringe", 0.4),
        layer("italy-states", "Italian powers", "#4a4a4a", ["ITA"], "dominant", 0.7),
        layer("ottoman-lm", "Ottoman advance", "#5a2a2a", ["GRC", "BGR", "MKD", "ALB", "SRB", "TUR"], "incoming", 0.75),
        layer("byz-rump", "Byzantine rump", "#6a3a4a", ["GRC", "TUR"], "substrate", 0.4),
        layer("muscovy", "Muscovy", "#6a3a3a", ["RUS"], "dominant", 0.75),
        layer("hungary-lm", "Kingdom of Hungary", "#7a5a3a", ["HUN", "SVK", "HRV"], "dominant", 0.7),
        layer("teutonic", "Teutonic Order Prussia", "#4a3a2a", ["POL", "LTU"], "fringe", 0.35),
    ]

    p["polities"] = LATE_MEDIEVAL_POLITIES
    return p


def make_reformation(late, early):
    """c. 1550 AD — Reformation, Habsburgs, Ottoman peak, Muscovy, Age of Discovery."""
    p = deep(early)
    p.update(
        {
            "id": "reformation",
            "label": "Reformation & Renaissance",
            "era": "Confessions, empires, print",
            "yearLabel": "c. 1550 AD",
            "yearApprox": 1550,
            "tickYear": "1550 AD",
            "narrative": (
                "By the mid-16th century Europe is split by confession and stitched by dynastic empire. "
                "Luther, Calvin, and the Catholic Council of Trent redraw belief; print multiplies argument; "
                "Habsburgs claim Spain’s global monarchy and the imperial title; Valois then early Bourbon "
                "France fights Habsburg encirclement and its own Wars of Religion; Tudor England breaks with "
                "Rome; the Ottomans under Süleyman dominate the Balkans and menace Vienna; Ivan IV’s Muscovy "
                "becomes an autocratic Orthodox empire; the Polish–Lithuanian Commonwealth is a noble republic "
                "of many faiths; Dutch revolt against Philip II is beginning. Overseas Iberian empires pull "
                "silver and souls into European politics. Genetics still sit on medieval continua — "
                "conversion and empire move people, but WHG–EEF–steppe deep structure remains."
            ),
            "culturesNote": (
                "Habsburg Spain & Austria; Valois France; Tudor England; Lutheran North; "
                "Ottoman Rumelia; Muscovy; PLC; Italian Mannerism; Portuguese & Spanish oceans."
            ),
            "linguistics": (
                "Early Modern English; Middle/early modern French; Early New High German; "
                "Castilian imperial standard; Italian literary language; Polish & Ruthenian; "
                "Church Slavonic/Russian chancery; Ottoman Turkish; Latin still scholarly."
            ),
        }
    )

    er = early["regions"]
    p["regions"] = {
        "iberia": bump_desc(
            er["iberia"],
            "Spain under Charles V and Philip II is a composite global monarchy: Castile’s silver fleets, "
            "Aragon’s Mediterranean inheritance, Portuguese dynastic entanglement (Iberian Union from 1580). "
            "Catholic reform, Inquisition, and expulsion/forced conversion of Muslims and Jews reshape "
            "society after Granada’s fall (1492). Culture: Golden Age letters and severe Habsburg piety. "
            "Ancestry: medieval Iberia plus Atlantic/imperial contacts — not a new ternary corner.",
        ),
        "britain": bump_desc(
            er["britain"],
            "Tudor England — Henry VIII’s break with Rome, Edwardine Protestantism, Mary’s Catholic "
            "restoration, Elizabeth’s settlement — invents a national church and fights Spain’s Armada "
            "decade. Scotland’s Reformation (Knox) and Ireland’s Tudor conquest wars create three "
            "different confessional trajectories on closely related islands. Print, Bible English, and "
            "Renaissance humanism redefine elite culture on a late medieval English gene pool.",
        ),
        "france": bump_desc(
            er["france"],
            "Valois France oscillates between Italian Wars glory and catastrophic Wars of Religion "
            "(Catholic League vs Huguenots) after the 1560s. Royal sacral power meets Calvinist nobles "
            "and Parisian radicalism; St Bartholomew’s Day becomes a European trauma story. Art and "
            "chateaux of the Renaissance coexist with confessional massacre. Demography is French "
            "medieval continuity under extreme political violence.",
        ),
        "central": bump_desc(
            er["central"],
            "The Holy Roman Empire after the Peace of Augsburg (1555) legalizes cuius regio, eius religio "
            "for Lutheran and Catholic princes — a truce before the Thirty Years’ War. Habsburgs hold "
            "Austria, Bohemia, Hungary’s remnant against Ottomans; German towns print pamphlets; Swiss "
            "cantons host Zwingli/Calvin’s orbits. Culture: confessional schooling, vernacular Bible, "
            "and Mannerist courts. Ancestry: central European continua.",
        ),
        "scandinavia": bump_desc(
            er["scandinavia"],
            "Denmark–Norway and Sweden become Lutheran monarchies; Gustav Vasa’s Sweden breaks Kalmar "
            "dependency and builds a fiscal-military state. Church lands fund kings; vernacular Bibles "
            "standardize speech. Baltic rivalry with Poland and Muscovy replaces union politics. "
            "Genetics: Nordic continuity through Reformation institutional change.",
        ),
        "italy": bump_desc(
            er["italy"],
            "Italian wars make the peninsula a Habsburg–Valois battlefield; Spanish Naples and Milan, "
            "papal Rome’s Counter-Reformation, Venetian maritime republic, and Tuscan ducal courts "
            "define politics. High Renaissance and Mannerism radiate artistic norms across Europe even "
            "as political independence wanes. Ancestry: Italian urban–rural medieval mixes with "
            "Spanish/Imperial elite overlays.",
        ),
        "balkans": bump_desc(
            er["balkans"],
            "Ottoman rule is entrenched across much of the Balkans: timar cavalry, millet confessional "
            "autonomy for Orthodox Christians and Jews, Islamization uneven by region (stronger in "
            "parts of Bosnia, Albania). Hungarian kingdom is split among Habsburg, Ottoman, and "
            "Transylvanian pieces after Mohács (1526). Culture: Orthodox monasteries, Sufi orders, "
            "and frontier epics. Genetics: Balkan continua plus Ottoman-era mobility.",
        ),
        "eastern": bump_desc(
            er["eastern"],
            "Ivan IV (‘the Terrible’) crowns a tsardom, conquers Kazan and Astrakhan, and opens a "
            "violent chapter of autocracy and expansion. The Polish–Lithuanian Commonwealth (Union of "
            "Lublin 1569) is a vast elective noble republic tolerating multiple faiths at elite level "
            "while binding Ruthenian lands. Cossack frontiers and Tatar raids frame the steppe edge. "
            "Deep ancestry remains eastern European; the novelty is tsarist and Commonwealth institutions.",
        ),
    }

    p["mapLayers"] = [
        layer("spain-hab", "Spanish Habsburg monarchy", "#6a3a2a", ["ESP", "BEL", "NLD", "ITA"], "dominant", 0.75),
        layer("portugal-ref", "Portuguese empire", "#5a6a3a", ["PRT"], "dominant"),
        layer("france-valois-r", "Valois France", "#2a2a2a", ["FRA"], "dominant"),
        layer("england-tudor", "Tudor England", "#3a5a48", ["GBR"], "dominant"),
        layer("ireland-tudor", "Tudor Ireland conquest", "#5a6a4a", ["IRL"], "incoming", 0.55),
        layer("scotland-ref", "Kingdom of Scotland", "#4a6a58", ["GBR"], "fringe", 0.4),
        layer("hre-confessional", "Confessional HRE", "#5a4a3a", ["DEU", "AUT", "CHE", "CZE"], "dominant", 0.7),
        layer("dutch-revolt", "Low Countries (revolt beginning)", "#4a3a5a", ["NLD", "BEL"], "incoming", 0.5),
        layer("sweden-vasa", "Vasa Sweden", "#3f5a6a", ["SWE", "FIN"], "dominant"),
        layer("denmark-nor-r", "Denmark–Norway", "#2f4a5a", ["DNK", "NOR"], "dominant"),
        layer("plc-ref", "Polish–Lithuanian Commonwealth", "#6a4a2a", ["POL", "LTU", "BLR", "UKR"], "dominant"),
        layer("muscovy-ivan", "Tsardom of Muscovy", "#6a3a3a", ["RUS"], "dominant"),
        layer("ottoman-peak", "Ottoman Empire", "#5a2a2a", ["GRC", "BGR", "MKD", "ALB", "SRB", "ROU", "HUN", "TUR", "HRV"], "dominant", 0.8),
        layer("habsburg-east", "Austrian Habsburgs", "#5a3a3a", ["AUT", "HUN", "CZE", "SVK", "HRV"], "incoming", 0.55),
        layer("italy-spanish", "Spanish Italy & Papal States", "#4a4a4a", ["ITA"], "dominant", 0.7),
        layer("switzerland-r", "Swiss Confederation", "#5a4a4a", ["CHE"], "dominant", 0.65),
    ]

    p["polities"] = REFORMATION_POLITIES
    return p


# ——— Polity libraries ———

VIKINGS_POLITIES = {
    "GBR": polity(
        "England under Æthelred → Cnut",
        "Late West Saxon kingship strained by renewed Viking armies; by the 1010s Denmark’s Cnut rules a North Sea empire including England.",
        "Norse invasions; Welsh and Scottish frontier wars; succession crises after Edgar and Edward the Martyr.",
        leaders="Æthelred II (‘Unready’); Edmund Ironside; Swein Forkbeard; Cnut the Great; Emma of Normandy.",
        religion="Latin Christian kingdom with lingering pagan Norse arrivals converting under royal pressure; cult of local saints.",
        culture="Old English law codes, monastic reform memory (Benedictine), burh towns, and skaldic/Norse contact culture in the Danelaw.",
        story="Danegeld paid to buy off armies becomes a moral tale of weak kingship; Cnut’s empire briefly joins England to Denmark and Norway — remembered in chronicle and later legend as both conquest and ordered Christian rule.",
    ),
    "IRL": polity(
        "Irish over-kingships & Norse towns",
        "Gaelic túatha and great dynasties (Uí Néill, Dál Cais) compete while Norse-Gaelic ports (Dublin, Waterford) trade and raid.",
        "Brian Boru’s coalition vs Norse-Dublin and Leinster rivals; endless cattle-tribute politics.",
        leaders="Brian Boru; Máel Sechnaill; Sitric Silkbeard of Dublin.",
        religion="Christian Ireland with powerful monasteries; Norse towns gradually Christianized.",
        culture="Filid poetry, high crosses, illuminated manuscripts; hybrid Norse-Gaelic urban culture.",
        story="Clontarf (1014) becomes Ireland’s great battle-myth: Brian falls at the moment of victory over a Dublin-Norse–Leinster alliance — less ‘national liberation’ than dynastic epic, but endlessly retold.",
    ),
    "FRA": polity(
        "Capetian France & Normandy",
        "Hugh Capet’s heirs hold Îée-de-France prestige more than territory; dukes of Normandy are Europe’s most dynamic princes.",
        "Feudal private war; Viking memory along rivers; southern principalities nearly independent.",
        leaders="Hugh Capet; Robert II; Richard II of Normandy; later William the Bastard (still a child/young duke by century’s turn).",
        religion="Latin Christianity reformed by Cluniac monasticism; royal sacral anointing.",
        culture="Emerging Old French epic world; castle-building; monastic schools.",
        story="The Capetians survive by hereditary sacral kingship while Normandy invents the disciplined cavalry duchy that will conquer England in 1066 — a millennium hinge between Viking settlement and high medieval statecraft.",
    ),
    "DEU": polity(
        "Ottonian–Salian Holy Roman Empire",
        "German kings claim imperial coronation at Rome, rule through stem duchies, and push missions and marches east.",
        "Slavic frontier wars; Italian campaigns; Magyar wars earlier in the century give way to Hungarian Christian monarchy as neighbor.",
        leaders="Otto III; Henry II; Conrad II (Salian).",
        religion="Imperial Christianity: emperor as protector of the Church, soon colliding with reforming papacy.",
        culture="Ottonian art and illuminated gospels; Latin literacy; palace-chapel ideology (Aachen memory).",
        story="Otto III’s Roman-imperial dream and Henry II’s saintly kingship frame a Reich that is neither nation-state nor mere fiction — elective, sacral, and permanently entangled with Italy.",
    ),
    "DNK": polity(
        "Kingdom of Denmark",
        "Bluetooth’s Christian claim matures into a kingdom projecting power into England and the Baltic.",
        "Rivalry with Norway/Sweden; Wendish coasts; English conquest politics.",
        leaders="Harold Bluetooth (memory); Swein Forkbeard; Cnut; Estridsson dynasty beginnings.",
        religion="Royal conversion to Latin Christianity; pagan holdouts in places.",
        culture="Jelling stones as dynasty-and-conversion monuments; ship levies; runic and Latin transition.",
        story="The Jelling inscription’s boast — ‘made the Danes Christian’ — is political theology in stone; Cnut’s English crown makes Denmark briefly a North Sea imperial center.",
    ),
    "NOR": polity(
        "Kingdom of Norway",
        "Coastal kingship forged by force and baptism; Iceland and Atlantic isles in Norwegian orbit.",
        "Civil wars among claimants; English and Danish entanglement.",
        leaders="Olaf Tryggvason; Olaf Haraldsson (St Olaf); Cnut’s overlorship phases.",
        religion="Aggressive royal Christianization against local cults.",
        culture="Skaldic verse; later saga memory; fjord levies and merchant farmers.",
        story="St Olaf’s fall at Stiklestad (1030) turns a hard king into Norway’s eternal martyr — conversion sealed by death-story as much as by law.",
    ),
    "SWE": polity(
        "Kingdom of Sweden",
        "Uppsala kings and regional assemblies inch toward Christian monarchy later than Denmark/Norway.",
        "Eastern Viking routes; Finnish coasts; Danish rivalry.",
        leaders="Olof Skötkonung (traditionally first Christian king); regional jarls.",
        religion="Pagan cult center at Uppsala persists in memory as baptism spreads unevenly.",
        culture="Mälaren valley power; runestones; trade toward Rus’.",
        story="Sweden’s conversion is slower and more regional — a reminder that ‘Viking Age’ is not one synchronized baptism.",
    ),
    "ESP": polity(
        "Andalusi taifas & northern Christian kingdoms",
        "After Córdoba’s caliphal collapse, taifa courts glitter while León–Castile, Navarre, and Catalan counts advance.",
        "Fitna civil wars; Christian tribute systems (parias); shifting frontiers.",
        leaders="Almanzor (late caliphal memory); taifa kings of Seville/Toledo; Alfonso V of León; Sancho of Navarre.",
        religion="Islam in the south; Latin Christianity in the north; Jews as cultural brokers in both.",
        culture="Arabic poetry and science; Mozarabic Christians; Romanesque beginnings in the north.",
        story="The fall of the caliphate turns one of Europe’s richest courts into competing city-kingdoms — brilliance and vulnerability that Christian kings exploit through parias and siege.",
    ),
    "PRT": polity(
        "County of Portugal",
        "A frontier county of León on the Atlantic edge of the Reconquista, not yet a fully independent kingdom (that crystallizes in the 12th century).",
        "Raids vs Andalusi neighbors; loyalty politics toward León.",
        leaders="Counts of Portugal under León’s shadow (e.g. Menendo González era memory; later Henry of Burgundy still ahead).",
        religion="Latin Christian frontier society.",
        culture="Atlantic agrarian frontier; pilgrimage roads beginning to matter.",
        story="Portugal’s later independence is seeded in this county’s frontier identity — a small Christian lordship facing the taifa world.",
    ),
    "ITA": polity(
        "Imperial Italy, Rome, Byzantine & Islamic south",
        "North and center: emperors, popes, and cities; south: Byzantines and Muslim Sicily before Norman conquest.",
        "Crescentii/ Tusculani Roman factions; imperial–papal tension; Arab raids.",
        leaders="Ottonian emperors in Italy; popes of the age; Byzantine catepans; Kalbid emirs in Sicily.",
        religion="Latin Christianity vs Greek Orthodoxy vs Islam on one peninsula.",
        culture="Manuscript centers; early communal stirrings; Mediterranean trade of Amalfi/Venice.",
        story="Italy at the millennium is Europe’s religious crossroads — three civilizations on one boot — soon to be remade by Norman adventurers.",
    ),
    "POL": polity(
        "Piast Poland",
        "Mieszko I’s baptism (966) and Bolesław Chrobry’s kingship place Poland inside Latin Christendom’s political club.",
        "Wars with the Reich, Bohemia, and Kievan Rus’; pagan reaction crises.",
        leaders="Mieszko I; Bolesław I the Brave; early Piast bishops.",
        religion="Latin Christianity newly established; pagan uprisings still possible.",
        culture="Gniezno as sacral center; warrior-duke retinues; missionary politics.",
        story="The Gniezno meeting (1000) with Otto III becomes Poland’s foundational European recognition scene — crown, relics, and imperial friendship as statecraft.",
    ),
    "HUN": polity(
        "Árpád Hungary under Stephen I",
        "Magyar dukes become a Christian kingdom; Stephen’s crown binds the Carpathian basin to Latin Europe.",
        "Internal conversion conflicts; German and Polish neighbor politics; steppe remnant pressures.",
        leaders="Géza; Stephen I (St Stephen); early queens and German alliances.",
        religion="Forced and negotiated Christianization; dioceses founded; pagan revolts later in the century.",
        culture="Nomad-origin elite adopting European kingship; Latin clergy; county administration beginnings.",
        story="Stephen’s crown (sent from the pope in tradition) is Hungary’s origin myth of Christian statehood — a steppe people choosing Latin Europe.",
    ),
    "UKR": polity(
        "Kievan Rus’",
        "Vladimir’s baptism aligns Rus’ with Byzantine Orthodoxy; Kiev sits on the Dnieper trade route ‘from the Varangians to the Greeks.’",
        "Pecheneg wars; succession among Rurikid princes; Byzantine alliance and friction.",
        leaders="Vladimir the Great; Yaroslav the Wise (rising); Varangian retinues.",
        religion="Byzantine Orthodox conversion; earlier pagan and diverse faiths among elites.",
        culture="Church Slavonic literacy; Scandinavian-Slavic elite fusion; iconic church building.",
        story="The Primary Chronicle’s tale of choosing a faith — testing Islam, Judaism, Western and Eastern Christianity — is literary statecraft: Orthodoxy as civilizational choice.",
    ),
    "RUS": polity(
        "Northern Rus’ & Novgorod orbit",
        "Forest towns and river routes of northern Rus’ linked to Kiev’s federation and Scandinavian trade.",
        "Tribute politics among tribes and princes; eastern Finnish/Uralic neighbors.",
        leaders="Local Rurikid princes; Novgorod posadnik traditions forming.",
        religion="Christianization spreading north from Kiev unevenly.",
        culture="Fur trade; wooden towns; bilingual contact zones.",
        story="Novgorod’s later republican myth has roots in this river-road world where merchants and princes bargain under loose Kievan suzerainty.",
    ),
    "GRC": polity(
        "Byzantine Empire (Macedonian apex)",
        "Basil II’s Byzantium is a military and fiscal superpower reclaiming the Balkans and projecting into the Caucasus and Italy.",
        "Bulgarian wars; Fatimid frontier; internal court factions.",
        leaders="Basil II; Constantine VIII; military aristocracy.",
        religion="Greek Orthodoxy as imperial ideology; missionary work among Slavs.",
        culture="Macedonian Renaissance learning; Constantinople’s ceremonial majesty.",
        story="Basil’s blinding of Bulgarian captives (as told) is the dark legend of reconquest — empire restored by terror and administration.",
    ),
    "BGR": polity(
        "First Bulgarian Empire (final phase)",
        "Samuel’s Bulgaria fights Basil II until catastrophic defeat and Byzantine annexation.",
        "Existential war with Byzantium; shifting capitals and mountain resistance.",
        leaders="Samuel of Bulgaria; last Cometopuli.",
        religion="Slavic Orthodoxy with Bulgarian patriarchal memory.",
        culture="Slavic liturgy; fortress warfare in the western Balkans.",
        story="The end of the First Empire becomes a national epic of resistance — historically a Byzantine reconquest that remaps the Balkans for generations.",
    ),
}

LATE_MEDIEVAL_POLITIES = {
    "GBR": polity(
        "Kingdom of England (Hundred Years’ War)",
        "English kings claim the French crown; longbow armies win Crécy and Agincourt; domestic politics slide toward the Wars of the Roses.",
        "Hundred Years’ War vs France; Scottish wars; Owain Glyndŵr’s Welsh revolt; later York–Lancaster civil war.",
        leaders="Edward III; the Black Prince; Richard II; Henry IV; Henry V; Henry VI.",
        religion="Latin Christianity under strain of papal Schism; Lollard dissent around Wycliffe’s Bible.",
        culture="Chaucer’s English; chivalric orders (Garter); perpendicular Gothic; growing parliamentary bargaining.",
        story="Agincourt (1415) becomes England’s mud-and-longbow miracle story — a outnumbered army’s victory that Tudor memory later wraps in nation-myth, even as the French war is eventually lost.",
    ),
    "IRL": polity(
        "Lordship of Ireland & Gaelic polities",
        "English royal lordship holds a pale around Dublin while Gaelic and gaelicized Anglo-Irish lords dominate much of the island.",
        "Bruce invasion memory; local succession wars; crown neglect during French campaigns.",
        leaders="English lieutenants; great earls (Ormond, Desmond, Kildare rising); Gaelic kings of Tyrone/Thomond etc.",
        religion="Latin Christian; distinctive Gaelic church customs under reforming pressure.",
        culture="Bardic poetry; Brehon law zones; hybrid marcher culture.",
        story="Ireland’s late medieval story is unfinished conquest — enough English law to claim the island, not enough state to hold it.",
    ),
    "FRA": polity(
        "Valois France & Burgundy",
        "France nearly disintegrates under English invasion and civil war, then reconquers with artillery, taxes, and Joan’s charismatic campaign.",
        "Hundred Years’ War; Armagnac–Burgundian feud; urban and peasant revolts.",
        leaders="Charles V; Charles VI; Charles VII; Joan of Arc; Philip the Good of Burgundy.",
        religion="Catholic kingdom; Gallican tensions with papacy; popular saint-cult around Joan.",
        culture="Flamboyant Gothic; courtly romance; emerging royal standing army.",
        story="Joan of Arc — peasant visionary who lifts the siege of Orléans and crowns Charles VII — is burned by the English then rehabilitated; France’s sacred rescue narrative.",
    ),
    "DEU": polity(
        "Holy Roman Empire (late medieval)",
        "Elective emperors, imperial cities, and princely territories; Golden Bull order; Hussite wars shake Bohemia.",
        "Hussite crusades; Swiss victories vs Habsburgs; princely feuds; Ottoman pressure on the southeast later.",
        leaders="Charles IV; Wenceslaus; Sigismund; early Habsburgs (Albert II, Frederick III).",
        religion="Catholic mainstream; Hussite reform in Bohemia (Utraquists/Taborites); conciliar movement.",
        culture="Hansa trade; Gothic town halls; universities; vernacular German mysticism.",
        story="Jan Hus’s burning at Constance (1415) ignites Bohemia — a proto-Reformation of communion in both kinds, wagon-fort war, and Czech vernacular faith.",
    ),
    "CZE": polity(
        "Lands of the Bohemian Crown",
        "Luxemburg emperors make Prague a capital of empire; Hussite revolution then reshapes Bohemian politics and confession.",
        "Hussite wars vs crusading Europe; internal Utraquist–Catholic settlement struggles.",
        leaders="Charles IV; Wenceslaus IV; Jan Hus; Jan Žižka; George of Poděbrady (later).",
        religion="Hussitism as national-religious movement inside/against Latin Christendom.",
        culture="Czech vernacular liturgy and song; Prague university; Gothic St Vitus.",
        story="Žižka’s blind generalship and wagon forts become Czech martial legend — peasants and townsmen beating knightly crusades.",
    ),
    "POL": polity(
        "Kingdom of Poland (Jagiellon union)",
        "Jogaila’s marriage union with Lithuania creates a dual power that breaks Teutonic expansion at Grünwald (1410).",
        "Teutonic wars; Muscovite and Tatar frontiers via Lithuania; noble liberty rising.",
        leaders="Władysław II Jagiełło; Vytautas the Great; later Jagiellon kings.",
        religion="Catholic Poland with vast Orthodox Ruthenian populations under Lithuanian rule; pagan Lithuania’s conversion.",
        culture="Latin and Ruthenian chanceries; knightly culture; growing szlachta identity.",
        story="Grünwald/Tannenberg — a multinational Polish–Lithuanian–Ruthenian victory over the Teutonic Order — becomes Central Europe’s great anti-crusader epic.",
    ),
    "LTU": polity(
        "Grand Duchy of Lithuania",
        "Europe’s last great pagan polity converts via Polish union yet rules mostly Orthodox Ruthenian lands from Vilnius.",
        "Teutonic crusades; rivalry and cooperation with Muscovy; Tatar alliances/wars.",
        leaders="Jogaila (Władysław II); Vytautas; earlier Gediminids.",
        religion="Catholic conversion of the elite; Orthodox majority in Ruthenian lands; residual pagan memory.",
        culture="Multiethnic duchy; Lithuanian dynasty over Slavic law codes; forest-and-steppe geopolitics.",
        story="Vytautas at the height of his power almost builds a Lithuanian empire from Baltic to Black Sea — a briefly plausible alternate Eastern Europe.",
    ),
    "DNK": polity(
        "Kalmar Union (Danish center)",
        "Margaret I’s architecture unites Denmark, Norway, and Sweden under one monarch — Danish-led in practice.",
        "Swedish rebellions; Hanseatic wars; Norwegian dependency.",
        leaders="Margaret I; Eric of Pomerania; later Christian I.",
        religion="Latin Christian monarchies under Roman obedience.",
        culture="Baltic trade; royal castles; German merchant influence in towns.",
        story="Margaret I — ‘lady king’ of the North — engineers Scandinavia’s only durable medieval union, remembered as both peace project and Danish domination.",
    ),
    "SWE": polity(
        "Sweden under / against Kalmar",
        "Swedish councils accept union then repeatedly rebel; Sture party later champions autonomy.",
        "Danish royal power; Hanseatic Stockholm politics; Finnish eastern frontier vs Novgorod/Muscovy.",
        leaders="Swedish regents (Sture line later); Engelbrekt’s revolt memory (1430s).",
        religion="Catholic; vernacular piety.",
        culture="Mining (Bergslagen); freeholding farmers; national chronicle beginnings.",
        story="Engelbrekt’s uprising becomes Sweden’s folk-hero revolt against union taxes and foreign bailiffs — a rehearsal of Vasa independence.",
    ),
    "NOR": polity(
        "Norway in the Kalmar Union",
        "Norwegian royalty fades; the kingdom is the weaker partner under Danish monarchs and Hanseatic Bergen.",
        "Hansa dominance; black-death demographic shock earlier; loss of Atlantic vigor.",
        leaders="Danish-Norwegian union kings; local magnates.",
        religion="Catholic archbishopric of Nidaros still prestigious.",
        culture="Saga manuscript culture persists; stockfish trade.",
        story="Norway’s late medieval arc is quiet tragedy: from independent sea kingdom to junior union partner — reversed only centuries later.",
    ),
    "ESP": polity(
        "Castile & Aragon; Nasrid Granada",
        "Trastámara dynasties rule Castile and Aragon; Granada survives as a tributary Islamic emirate.",
        "Civil wars in Castile; Mediterranean expansion of Aragon (Sicily, Sardinia, Naples ambitions); frontier war with Granada.",
        leaders="John I / Henry III of Castile; Ferdinand I of Aragon; Yusuf/Nasrid emirs.",
        religion="Catholic majorities; Jewish communities under rising pressure; Islam in Granada.",
        culture="Alhambra’s late flowering; Castilian chivalric chronicle; Catalan commercial empire.",
        story="The Alhambra’s lyric courts exist beside a shrinking Islamic polity — beauty as the last act before 1492’s conquest.",
    ),
    "PRT": polity(
        "Kingdom of Portugal (Aviz)",
        "After the 1385 crisis, Aviz kings secure independence from Castile and look toward Africa (Ceuta 1415).",
        "Castilian claims; Moroccan raids; Atlantic exploration beginnings under Henry the Navigator’s generation.",
        leaders="John I; Prince Henry the Navigator; Duarte.",
        religion="Crusading Catholicism turned toward Africa.",
        culture="Atlantic seamanship; Gothic Batalha monastery as dynasty monument.",
        story="Aljubarrota (1385) saves Portuguese independence; Ceuta opens the African door that becomes the Age of Discovery.",
    ),
    "ITA": polity(
        "Italian regional states",
        "Milan, Florence, Venice, the Papacy, and Naples balance in the ‘Italic League’ pattern — brilliant, fragile, mercenary.",
        "Condottieri wars; Ottoman naval pressure on Venice; Angevin/Aragonese fight for Naples.",
        leaders="Gian Galeazzo Visconti; Cosimo de’ Medici (rising); Venetian doges; rival popes in Schism’s wake.",
        religion="Catholic; conciliar crisis; popular confraternities.",
        culture="Early humanism; Dante/Petrarch/Boccaccio’s legacy; civic patronage.",
        story="Italian cities invent Renaissance modernity while failing to invent a durable Italian state — culture without unification.",
    ),
    "GRC": polity(
        "Byzantine rump & Latin leftovers → Ottoman conquest",
        "Constantinople’s empire is a shadow waiting for 1453; Frankish and Venetian remnants linger in islands and ports.",
        "Ottoman siege pressure; civil wars; Western union diplomacy (Florence 1439) that divides Orthodox opinion.",
        leaders="Manuel II; John VIII; Constantine XI (mid-century); Ottoman Murad II / Mehmed II.",
        religion="Orthodoxy under existential threat; bitter debate over union with Rome.",
        culture="Late Byzantine scholarship fleeing westward; monastic Hesychasm.",
        story="The fall of Constantinople (1453) — Mehmed’s cannon vs Constantine XI’s last stand — ends the Roman imperial story in Greek dress and becomes Christendom’s great lament.",
    ),
    "SRB": polity(
        "Serbian lands after the empire",
        "Post-Dušan fragmentation; Kosovo battle memory; eventual Ottoman subjugation of Serbian despots.",
        "Ottoman advance; Hungarian alliances; internal magnate splits.",
        leaders="Prince Lazar (memory of Kosovo); despot Stefan Lazarević; later Durad Branković.",
        religion="Serbian Orthodoxy as identity under pressure.",
        culture="Epic poetry cycle of Kosovo; monastery patronage (Morava school).",
        story="Kosovo Polje (1389) becomes Serbia’s central martyrdom epic — historically messy, culturally absolute.",
    ),
    "BGR": polity(
        "Bulgarian lands under Ottoman conquest",
        "Second Bulgarian Empire’s fragments fall to Ottoman campaigns in the late 14th century.",
        "Ottoman conquest; resistance and boyar accommodation.",
        leaders="Last Shishmanids; local notables under early Ottoman rule.",
        religion="Orthodoxy under the millet-to-be; Islamization limited at first.",
        culture="Tarnovo literary memory; then Ottoman provincial order.",
        story="The end of medieval Bulgarian statehood is told as nightfall before centuries of foreign rule — a national narrative forged later, rooted in real conquest.",
    ),
    "RUS": polity(
        "Grand Principality of Moscow",
        "Moscow ‘gathers the Russian lands,’ contests Novgorod, and maneuvers between Horde overlords and Lithuania.",
        "Wars with Novgorod, Tver, Lithuania; tribute and rebellion vs the Horde (Ugra 1480 still ahead as symbolic end).",
        leaders="Dmitry Donskoy; Vasily I; Vasily II; Ivan III (later in century).",
        religion="Orthodox metropolitanate shifting toward Moscow; monastic colonization of the north.",
        culture="Icon painting; chronicle writing; fortress kremlins.",
        story="Kulikovo (1380) — Dmitry’s victory over a Horde commander — becomes Russia’s first great liberation myth, even though Horde power returns afterward.",
    ),
    "UKR": polity(
        "Ruthenian lands under Lithuania",
        "Former Kievan territories largely ruled from Vilnius; Orthodox boyars under Lithuanian/Polish union politics.",
        "Tatar raids; Muscovite claims on ‘Rus’ heritage’; local princely remnants.",
        leaders="Lithuanian grand dukes; Ruthenian princes (Ostroski later prominence).",
        religion="Orthodoxy majority; Catholic elite conversion pressures after Krewo/Horodło.",
        culture="Ruthenian chancery language; fortress towns; steppe border life.",
        story="Who inherits Kiev’s legacy — Moscow or Lithuania’s Rus’ — is the ideological war of the late medieval east.",
    ),
    "HUN": polity(
        "Kingdom of Hungary (Anjou → Luxemburg/Habsburg claims)",
        "A major Central European kingdom facing Ottoman pressure on its southern frontier after Serbian collapse.",
        "Ottoman raids; succession crises; baron leagues.",
        leaders="Louis I the Great (memory); Sigismund of Luxemburg; later Hunyadi (mid-century).",
        religion="Catholic realm with Orthodox minorities in the south/east.",
        culture="Chivalric court; Gothic Buda; multiethnic nobility.",
        story="Hungary casts itself as Christendom’s shield; the 15th-century Hunyadi wars turn that claim into cannon-smoke reality.",
    ),
    "NLD": polity(
        "Burgundian Netherlands",
        "Flanders and the Low Countries under Burgundian dukes become Europe’s richest urban–textile zone.",
        "Urban revolts; French/English war entanglement; later Habsburg inheritance.",
        leaders="Philip the Bold; John the Fearless; Philip the Good.",
        religion="Dense parish Catholicism; early reform currents still underground.",
        culture="Early Netherlandish painting; cloth towns; pragmatic urban liberties.",
        story="Burgundy’s court — Order of the Golden Fleece, dazzling chronicles — makes the Low Countries a capital of European splendor without being a ‘nation’ yet.",
    ),
    "CHE": polity(
        "Swiss Confederation",
        "Alpine cantons defeat Habsburg knights and become a fact of European military life.",
        "Habsburg wars; Burgundian wars (later 15th c.); internal canton politics.",
        leaders="Cantonal elites; legendary William Tell as later national myth layered on real battles (Morgarten, Sempach).",
        religion="Catholic; local saints and fierce communal autonomy.",
        culture="Peasant-soldier reputation; chronicles of liberty.",
        story="Sempach and Morgarten are Switzerland’s founding battle-stories: infantry and terrain beating aristocratic cavalry.",
    ),
    "AUT": polity(
        "Habsburg Austrian lands",
        "Habsburgs consolidate Alpine duchies and begin their long game for empire and Burgundian inheritance.",
        "Swiss losses; Bohemian/Hungarian dynastic contests; Ottoman shadow later.",
        leaders="Rudolf IV (memory); Albert II; Frederick III (‘AEIOU’).",
        religion="Catholic dynastic piety.",
        culture="Vienna as rising residence; dynastic marriage strategy elevated to art.",
        story="Frederick III’s cryptic AEIOU and Maximilian’s later Burgundian wedding embody Habsburg doctrine: marry, inherit, outlast.",
    ),
    "TUR": polity(
        "Ottoman Sultanate in Europe",
        "From Rumelian bases the Ottomans become a European great power before taking Constantinople.",
        "Wars with Serbia, Bulgaria, Hungary, Byzantium, Venice; Anatolian rivals.",
        leaders="Bayezid I; Mehmed I; Murad II; Mehmed II.",
        religion="Sunni Islam as state; dhimmi system for Christians and Jews.",
        culture="Ghazi warrior ethos evolving into imperial bureaucracy; endowment (waqf) cities.",
        story="The lightning rise from frontier beylik to breaker of Constantinople reorders Europe’s mental map — Islam as a Central European neighbor.",
    ),
}

REFORMATION_POLITIES = {
    "GBR": polity(
        "Tudor England (& Reformation Scotland)",
        "Henry VIII’s royal supremacy, Edward’s Protestant turn, Mary’s Catholic restoration, and Elizabeth’s settlement create a confessional rollercoaster; Scotland adopts a Calvinist kirk.",
        "Rough Wooing vs Scotland; Irish Tudor conquest wars; rivalry with Spain culminating in the Armada (1588).",
        leaders="Henry VIII; Edward VI; Mary I; Elizabeth I; Mary Queen of Scots; John Knox.",
        religion="Church of England via statute; Catholic underground; Puritan pressure; Scottish Presbyterianism.",
        culture="Vernacular Bible and Book of Common Prayer; emerging public theatre (Elizabethan); humanist schools.",
        story="The Armada — storm, fireships, and propaganda — becomes Protestant England’s deliverance myth; Mary Queen of Scots’ scaffold is the tragic counter-story of Catholic royalty.",
    ),
    "IRL": polity(
        "Tudor Ireland",
        "Surrender-and-regrant and plantation beginnings aim to anglicize Gaelic lordships; resistance culminates later in the Nine Years’ War.",
        "Desmond rebellions; Shane O’Neill; crown vs Gaelic alliances.",
        leaders="Tudor deputies; Shane O’Neill; earls of Desmond; Hugh O’Neill (later).",
        religion="Catholic population under a Protestant state church newly claimed.",
        culture="Gaelic learned orders under pressure; Pale Englishness vs Gaelic polarity hardening.",
        story="Ireland becomes England’s first long colonial laboratory — Reformation plus conquest, with consequences lasting centuries.",
    ),
    "FRA": polity(
        "Valois France in the Wars of Religion",
        "Italian Wars prestige collapses into Catholic–Huguenot civil wars; monarchy nearly dissolves before Bourbon recovery.",
        "Habsburg wars; eight Wars of Religion; St Bartholomew’s Massacre; Catholic League vs Henry of Navarre.",
        leaders="Francis I; Henry II; Catherine de’ Medici; Henry III; Henry IV (Navarre).",
        religion="Catholic majority; Calvinist Huguenot minority with noble leadership; politiques seeking peace.",
        culture="Renaissance chateaux; Rabelais/Montaigne; militant confessional print.",
        story="St Bartholomew’s Day (1572) — wedding turned massacre — scars Europe; Henry IV’s later ‘Paris is worth a mass’ pragmatism ends the nightmare (Edict of Nantes 1598).",
    ),
    "ESP": polity(
        "Spanish Habsburg world monarchy",
        "Charles V and Philip II rule Spain, much of Italy, the Low Countries, and American silver — Catholic champion and bankrupt giant.",
        "Dutch Revolt; Ottoman Mediterranean war (Lepanto 1571); English war; French Habsburg rivalry; Morisco revolt.",
        leaders="Charles V; Philip II; Duke of Alba; Don John of Austria.",
        religion="Tridentine Catholicism; Inquisition; missionary empire.",
        culture="Golden Age literature beginnings; Escorial austerity; global bureaucracy.",
        story="Lepanto is sung as Christian naval triumph; the Dutch Revolt and Armada failure show the limits of Spanish universal monarchy.",
    ),
    "PRT": polity(
        "Portuguese Empire (& Iberian Union ahead)",
        "Portugal’s Asian and Brazilian routes still enrich the crown; dynastic crisis will hand the realm to Philip II in 1580.",
        "Ottoman and local Asian rivals; French/English interlopers; Moroccan disaster at Alcácer Quibir (1578).",
        leaders="John III; Sebastian I; Cardinal-King Henry.",
        religion="Catholic missionary orders (Jesuits) as empire’s soft power.",
        culture="Camões’ epic of discovery (Os Lusíadas, 1572); Atlantic Creole ports.",
        story="Sebastian’s death in Morocco becomes the sebastianismo myth — a lost king who will return — while Spain absorbs the Portuguese crown.",
    ),
    "DEU": polity(
        "Confessional Holy Roman Empire",
        "Augsburg’s peace freezes Lutheran and Catholic princely choice; Calvinists remain legally awkward; print culture never freezes.",
        "Princely rivalries; Ottoman wars on Habsburg borders; prelude tensions to 1618.",
        leaders="Charles V (earlier); Ferdinand I; Lutheran princes (Saxon/Electorates); Protestant Union / Catholic League seeds.",
        religion="Lutheran / Catholic official duality; Calvinist expansion; Anabaptist memory of persecution.",
        culture="Vernacular Bible; Lutheran chorale; university confessionalization; Dürer’s legacy into Mannerism.",
        story="Luther at Worms (‘here I stand’ in later wording) remains the origin scene; Augsburg 1555 is the exhausted compromise that only postpones a continental war.",
    ),
    "NLD": polity(
        "Habsburg Netherlands → Dutch Revolt",
        "Rich urban provinces revolt against Philip II’s taxes, troops, and heresy laws; a republic is being born.",
        "Iconoclastic Fury; Alba’s Council of Blood; siege warfare; William of Orange’s leadership.",
        leaders="William the Silent; Philip II’s governors (Alba, Requesens, Parma); Beggars (Geuzen).",
        religion="Calvinist revolt core; large Catholic populations; radical tolerance experiments in places.",
        culture="Early capitalist trade; print and pamphlets; art before the Golden Age bloom.",
        story="The Sea Beggars’ capture of Brielle (1572) is the revolt’s spark-story — a ragged naval rebel act that unravels Spanish authority in Holland and Zeeland.",
    ),
    "CHE": polity(
        "Swiss Confederation (Reformation)",
        "Zwingli’s Zurich and Calvin’s Geneva make Switzerland a laboratory of Reformed religion beside Catholic cantons.",
        "Kappel wars between confessions; mercenary export continues.",
        leaders="Ulrich Zwingli; John Calvin; Catholic Waldstätten elites.",
        religion="Reformed vs Catholic cantonal split — a miniature Europe.",
        culture="Disciplined consistory religion; citizen-soldier myth; printing.",
        story="Calvin’s Geneva — refuge for exiles and exporter of pastors — punches far above its Alpine weight in Atlantic Protestantism.",
    ),
    "ITA": polity(
        "Italian states under Habsburg hegemony",
        "Spanish Milan and Naples, papal Counter-Reformation Rome, Tuscan dukes, and Venice define a politically subordinated, culturally radiant Italy.",
        "French residual wars; Ottoman–Venetian sea war; heresy trials.",
        leaders="Cosimo I de’ Medici; papal reformers (Paul III →); Spanish viceroys; Venetian doges.",
        religion="Tridentine Catholicism; Index and Inquisition; Jewish ghettos formalized in places.",
        culture="Late Renaissance/Mannerism; early scientific circles; opera’s eve.",
        story="Rome rebrands as Caput Mundi of Catholic reform while Machiavelli’s earlier mirror of princes teaches Europe a colder politics than the popes prefer.",
    ),
    "SWE": polity(
        "Vasa Sweden",
        "Gustav Vasa’s hereditary Lutheran monarchy breaks Kalmar and builds a resource state from church lands and copper.",
        "Danish wars; peasant risings (Dacke); Baltic competition with Russia/Poland.",
        leaders="Gustav Vasa; Eric XIV; John III.",
        religion="Lutheran state church; residual Catholic liturgy fights under John III.",
        culture="National chronicle; fortress modernisation; Finnish eastern marches.",
        story="Gustav’s rebellion against Kristian II (Stockholm Bloodbath memory) is Sweden’s independence epic — blood, tax, and Bible.",
    ),
    "DNK": polity(
        "Denmark–Norway (Lutheran)",
        "Oldenburg kings run a Lutheran dual monarchy controlling the Øresund toll — Europe’s choke point to the Baltic.",
        "Swedish independence wars; Baltic rivalry; Norwegian incorporation.",
        leaders="Christian III; Frederick II.",
        religion="Lutheran Reformation imposed after civil war (Count’s Feud).",
        culture="Sound Toll wealth; Renaissance Kronborg; Norwegian dependency.",
        story="Whoever holds the Sound Toll taxes half of northern Europe’s grain and naval stores — Denmark’s geopolitical superpower trick.",
    ),
    "NOR": polity(
        "Norway under Denmark",
        "A kingdom without its own resident dynasty; Reformation arrives via Copenhagen.",
        "Danish governors; trade under Hansa then Danish control.",
        leaders="Danish viceroys; local nobles diminished.",
        religion="Lutheran reform from above.",
        culture="Continuing vernacular life; loss of archbishopric independence.",
        story="Norway’s Reformation is an email from Copenhagen — institutional change without a local Luther.",
    ),
    "POL": polity(
        "Polish–Lithuanian Commonwealth",
        "Union of Lublin (1569) creates a vast elective republic of nobles, multiethnic and (at elite level) multi-confessional.",
        "Muscovite wars; Baltic contests with Sweden; Ottoman/Tatar south; noble liberty vs royal power.",
        leaders="Sigismund II Augustus; later Henry Valois / Stephen Báthory (election politics).",
        religion="Catholic, Orthodox, Protestant, and Jewish communities under the Warsaw Confederation’s famous tolerance act (1573).",
        culture="Szlachta golden liberty; Latin and Polish Renaissance; Ruthenian borders.",
        story="The Commonwealth’s noble democracy — liberum ideas before the word — is Europe’s alternate modernity: huge, tolerant, and hard to mobilize.",
    ),
    "LTU": polity(
        "Lithuania within the Commonwealth",
        "The Grand Duchy retains law and identity inside the Lublin union while sharing foreign policy and elective kingship with Poland.",
        "Muscovite pressure; internal integration with Polish institutions.",
        leaders="Sigismund Augustus as both; Lithuanian magnate families (Radziwiłł).",
        religion="Catholicizing elites; Orthodox and Protestant magnates; Jewish towns.",
        culture="Lithuanian Statutes; bilingual elite world.",
        story="Lublin is both marriage and partial erasure — Lithuanian statehood persists in law while European maps increasingly say ‘Poland.’",
    ),
    "RUS": polity(
        "Tsardom of Russia (Ivan IV)",
        "Ivan IV crowns himself tsar, conquers Muslim khanates on the Volga, then unleashes the Oprichnina’s terror.",
        "Livonian War vs Poland/Sweden; Crimean Tatar sack of Moscow (1571); internal blood purge.",
        leaders="Ivan IV (‘the Terrible’); advisers then victims of the Oprichnina; Yermak’s Cossack Siberia beginnings.",
        religion="Orthodox autocracy; Moscow as ‘Third Rome’ ideology rising.",
        culture="Onion-dome votive architecture; chronicle and terror; eastward conquest.",
        story="Ivan’s killing of his own son (in later tradition) and the Oprichnina make him Europe’s archetype of sacred tyranny — expansion and self-devouring power.",
    ),
    "UKR": polity(
        "Ukrainian lands: Commonwealth borderland",
        "Ruthenian provinces of the Commonwealth; Cossack militarized frontiers against Tatars and as royal/noble instruments.",
        "Tatar slave raids; magnate estates; emerging Cossack political identity (rebellions later in the 17th c.).",
        leaders="Wisniowiecki and other magnates; Cossack starshyna forming; Crimean khans as raid-neighbors.",
        religion="Orthodoxy under pressure of Catholic/Uniate projects (Brest 1596 just ahead/around this horizon).",
        culture="Steppe frontier epic; church brotherhoods; bilingual Polish–Ruthenian elite zone.",
        story="The Cossack — freeman warrior of the Dnieper cataracts — becomes Ukraine’s lasting social myth, born on this violent border.",
    ),
    "HUN": polity(
        "Hungary divided (Ottoman / Habsburg / Transylvania)",
        "After Mohács, the medieval kingdom splits into Habsburg Royal Hungary, Ottoman central occupation, and the Principality of Transylvania.",
        "Ottoman–Habsburg wars; Transylvanian diplomacy between sultans and emperors.",
        leaders="Ferdinand I Habsburg; János Szapolyai’s line; Ottoman pashas of Buda; Transylvanian princes.",
        religion="Catholic Habsburg west; Protestant strength in Transylvania’s famous tolerance diet; Orthodox Romanians; Islam in Ottoman zones.",
        culture="Frontier fortress warfare; multi-confessional Transylvania as outlier.",
        story="Mohács (1526) — two hours that kill a king and shatter a kingdom — is Hungary’s national catastrophe date.",
    ),
    "AUT": polity(
        "Austrian Habsburg core",
        "Vienna’s Habsburgs defend and administer the Danube frontier while claiming the imperial title and Spanish kinship.",
        "Ottoman sieges (1529 memory); German princely politics; Bohemian crown lands.",
        leaders="Ferdinand I; Maximilian II; Spanish kin Philip II.",
        religion="Catholic dynasty with temporarily tolerant Maximilian; Jesuit education rising.",
        culture="Danubian court; defensive military frontier (Grenze).",
        story="The 1529 Ottoman siege of Vienna teaches Europe that the Turk can reach the heart of the Reich — fear as policy.",
    ),
    "GRC": polity(
        "Ottoman Greece",
        "Greek lands under Ottoman provinces; Orthodox Patriarchate in Constantinople as millet head; islands partly Venetian.",
        "Venetian–Ottoman wars; local bandit/klepht beginnings; tax and conversion pressures.",
        leaders="Ecumenical Patriarchs; Ottoman governors; Venetian captains in the islands.",
        religion="Greek Orthodoxy under Islamic sovereignty; crypto-Christianity debates in places.",
        culture="Post-Byzantine painting; folk song; diaspora merchants.",
        story="The ‘secret school’ legend of keeping Greek letters alive under Ottoman rule is later nation-myth — literacy and liturgy did persist, unevenly, through church structures.",
    ),
    "BGR": polity(
        "Ottoman Bulgaria",
        "Bulgarian lands as Ottoman provinces; Orthodox church life continues under the Patriarchate.",
        "Local uprisings occasional; integration into Ottoman fiscal systems.",
        leaders="Ottoman officials; Orthodox bishops; local çorbacı notables.",
        religion="Orthodoxy; gradual Islamization in some regions.",
        culture="Village Christian culture; Ottoman townscapes.",
        story="Bulgarian national revival is centuries away; this is the long Ottoman night of later historiography — daily life more continuous than the metaphor suggests.",
    ),
    "SRB": polity(
        "Ottoman Serbia (& Habsburg fringe)",
        "Serbian lands largely Ottoman; patriarchate of Peć sometimes restored as communal focus; migrations north toward Habsburg lands begin in pulses.",
        "Ottoman–Habsburg wars; local knez autonomy pockets.",
        leaders="Ottoman pashas; Serbian patriarchs; hajduk outlaw-heroes in folk song.",
        religion="Southern Slavic Orthodoxy under millet structures.",
        culture="Epic gusle poetry; monastery refuges.",
        story="The hajduk — outlaw resistance figure — becomes the folk counter-state when there is no Serbian kingdom on the map.",
    ),
    "TUR": polity(
        "Ottoman imperial center",
        "Süleyman’s empire straddles three continents; Istanbul is a world capital of law, architecture, and war.",
        "Safavid wars; Habsburg frontier; Mediterranean rivalry with Spain/Venice; Indian Ocean contests with Portugal.",
        leaders="Süleyman the Magnificent; grand viziers (e.g. Rüstem, Sokollu); Hürrem Sultan in court politics.",
        religion="Sunni Islam (Hanafi law); protected Christian and Jewish millets; Sufi orders.",
        culture="Sinan’s mosques; kanun law beside sharia; multilingual palace.",
        story="Süleyman before Vienna and at Mohács makes the sultan Europe’s indispensable villain and diplomat — the ‘Magnificent’ as mirror to Charles V.",
    ),
    "BEL": polity(
        "Southern Netherlands (Spanish)",
        "The Catholic southern provinces reconquered by Parma remain under Spanish Habsburgs as Antwerp’s golden age wanes.",
        "Dutch Revolt warfare; religious cleansing northward migration of Protestants.",
        leaders="Duke of Parma (Alexander Farnese); Spanish governors.",
        religion="Tridentine Catholic restoration.",
        culture="Flemish painting still luminous; commercial shift toward Amsterdam.",
        story="Antwerp’s fall and Protestant exodus help invent Amsterdam’s boom — a tale of two Low Countries.",
    ),
}


def enrich_existing_polities(period: dict, extra: dict[str, dict]):
    pols = period.setdefault("polities", {})
    for iso, fields in extra.items():
        if iso in pols:
            pols[iso] = enrich_polity(pols[iso], **fields)
        elif "name" in fields:
            pols[iso] = enrich_polity(fields)
        # else: skip incomplete stubs for ISOs without an existing polity row


FRANKISH_EXTRA = {
    "FRA": dict(
        leaders="Charlemagne; Louis the Pious; later Charles the Bald (West Francia).",
        religion="Latin Christian empire; forced Saxon conversion; alliance and tension with the papacy.",
        culture="Carolingian Renaissance — palace school, minuscule script, liturgical reform.",
        story="The imperial crowning at Rome (800) and the Saxon Wars define Carolingian power: sacred empire built with the sword. Verdun (843) then splits the dream among grandsons.",
    ),
    "DEU": dict(
        leaders="Louis the German; Arnulf; early stem-duke politics after Verdun.",
        religion="Latin Christianity; missionary pushes east.",
        culture="East Frankish lordship; monastic centers; frontier marches.",
        story="East Francia becomes the kernel of the later Holy Roman Empire — a kingdom born from treaty lines at Verdun.",
    ),
    "GBR": dict(
        leaders="Alfred the Great; Edward the Elder; Æthelstan; Norse kings in York/Dublin orbit.",
        religion="Latin Christian Anglo-Saxon kingdoms; pagan Norse arrivals converting unevenly.",
        culture="Alfredian translation program; burhs; epic and chronicle (Anglo-Saxon Chronicle).",
        story="Alfred’s refuge in the marshes and reconquest become England’s founding resistance story against the Great Heathen Army.",
    ),
    "ESP": dict(
        leaders="Emirs/caliphs of Córdoba; Alfonso II of Asturias; counts of Barcelona.",
        religion="Islam in Al-Andalus; northern Christian kingdoms; Jewish communities.",
        culture="Córdoba’s libraries and mosques; Asturian churches; frontier raid culture (razzias).",
        story="Almanzor’s raids (late 10th c. still ahead of this tick’s heart) haunt Christian memory — Córdoba as both civilization and threat.",
    ),
    "ITA": dict(
        leaders="Charlemagne as Lombard king; popes; Byzantine officials in the south.",
        religion="Latin papacy vs Greek south; Islamic Sicily rising in the 9th c.",
        culture="Lombard law memory; Roman ceremonial; Mediterranean trade seeds.",
        story="The Donation ideology and papal–Frankish alliance remake Italy into the empire’s sacred theater.",
    ),
    "NOR": dict(
        leaders="Sea-kings and local petty kings before Harald Fairhair’s unification traditions.",
        religion="Norse paganism dominant; Christian contact via raid and trade.",
        culture="Shipburial elite display; skaldic praise; thing assemblies.",
        story="The Viking launch from fjords toward Ireland, Francia, and beyond begins Norway’s global hour.",
    ),
    "DNK": dict(
        leaders="Early historically foggy kings culminating toward Bluetooth’s line.",
        religion="Pagan with Christian missions (Ansgar’s memory).",
        culture="Trading towns (Hedeby); ship levies.",
        story="Denmark sits at the mouth of Baltic–North Sea violence and trade — the workshop of the Viking Age.",
    ),
    "SWE": dict(
        leaders="Uppsala kings in later tradition; Rus’ expedition leaders.",
        religion="Pagan cults; eastern contact religions along trade routes.",
        culture="Eastern river routes; proto-urban Birka.",
        story="Swedish Vikings as ‘Rus’’ in eastern sources link the Mälaren to the Black Sea.",
    ),
}

HIGH_MED_EXTRA = {
    "GBR": dict(
        leaders="Henry II; Eleanor of Aquitaine; Richard I; John; Edward I (later in the long high-medieval arc).",
        religion="Latin Christianity; Becket conflict as church-vs-crown archetype; Jewish communities until 1290 expulsion.",
        culture="Angevin law (common law beginnings); Gothic cathedrals; Arthurian romance fashion; Magna Carta politics.",
        story="Becket’s murder in Canterbury (1170) and Magna Carta (1215) become England’s twin stories of sacred blood and baronial bridle on kings.",
    ),
    "FRA": dict(
        leaders="Philip II Augustus; Louis IX (St Louis); Philip IV the Fair.",
        religion="Catholic monarchy; Albigensian Crusade in the south; university theology in Paris.",
        culture="Gothic invention (Saint-Denis to Chartres); troubadour/trouvère song; royal bureaucracy.",
        story="Philip Augustus wins Bouvines (1214) and takes Normandy — Capetian France becomes a real territorial kingdom, not only a sacred title.",
    ),
    "DEU": dict(
        leaders="Frederick Barbarossa; Frederick II; elective princes.",
        religion="Catholic empire; investiture aftershocks; crusading emperors.",
        culture="Minnesang; Kaiser myth; Italian–German political double life.",
        story="Barbarossa’s legend — drowned on crusade, sleeping in a mountain in folklore — outlives the political failure to fully master Italy.",
    ),
    "ESP": dict(
        leaders="Alfonso VIII of Castile; James I of Aragon; Ferdinand III; Nasrid founders in Granada.",
        religion="Reconquista Catholicism; Islam in Al-Andalus; Jewish Golden Age fading under pressure.",
        culture="Toledo translation networks; Cantigas; military orders (Santiago, Calatrava).",
        story="Las Navas de Tolosa (1212) breaks Almohad power — the hinge battle of the Iberian Middle Ages.",
    ),
    "ITA": dict(
        leaders="Frederick II in the south; papal rivals; Venetian doges; communal podestà.",
        religion="Papacy at the height of claims; mendicant orders (Francis, Dominic).",
        culture="Communal towers; early universities; vernacular poetry toward Dante.",
        story="Francis of Assisi’s renunciation and the mendicant revolution remake popular piety from Umbrian roads to European cities.",
    ),
    "POL": dict(
        leaders="High medieval Piasts; fragmentation among duchies then reunification under Władysław Łokietek / Casimir the Great (long arc).",
        religion="Latin Christianity; monastic orders; Jewish settlement invited in law (Casimir tradition).",
        culture="Knightly culture; Magdeburg law towns.",
        story="Casimir the Great’s later reputation — ‘found Poland of wood, left it of stone’ — crowns the high-medieval Polish arc.",
    ),
}

EARLY_MODERN_EXTRA = {
    "GBR": dict(
        leaders="Elizabeth I (late); James VI & I; Charles I; Cromwell; William & Mary (long 17th-c. arc around the 1600 tick).",
        religion="Protestant settlements; Puritan revolution; Catholic minorities; Scottish kirk conflicts.",
        culture="Shakespearean stage; scientific circles toward the Royal Society; Atlantic colonization.",
        story="The Civil War and regicide of Charles I shock Europe — a king tried by his people — before Restoration and Glorious Revolution redefine monarchy.",
    ),
    "FRA": dict(
        leaders="Henry IV; Richelieu; Louis XIV (later flowering from mid-century).",
        religion="Edict of Nantes coexistence then later revocation trajectory; Catholic reform.",
        culture="Classical French taste forming; absolutist administration.",
        story="Richelieu’s state-within-the-state and the siege of La Rochelle dramatize the taming of armed faith for royal sovereignty.",
    ),
    "ESP": dict(
        leaders="Philip III; Philip IV; Olivares; continuing Habsburg line.",
        religion="Baroque Catholicism; Inquisition still active.",
        culture="Cervantes; Velázquez; imperial overstretch.",
        story="Don Quixote (1605) laughs a tired empire into world literature while silver fleets and bankruptcies continue offstage.",
    ),
    "DEU": dict(
        leaders="Ferdinand II; Gustavus Adolphus (as intervention); Wallenstein; Peace of Westphalia princes.",
        religion="Catholic, Lutheran, Calvinist legally recognized after 1648; enormous war trauma.",
        culture="Devastation and rebuilding; early Pietism seeds; territorial absolutisms.",
        story="The Thirty Years’ War — Europe’s dress rehearsal for total war — ends in Westphalia’s patchwork peace that teaches cuius regio on a ruined map.",
    ),
    "NLD": dict(
        leaders="Oldenbarnevelt; Maurice of Nassau; later Johan de Witt / William III arc.",
        religion="Public Calvinism with notable practical tolerance in cities.",
        culture="Dutch Golden Age art (Rembrandt, Vermeer); global VOC capitalism.",
        story="A republic of US merchants defeats Spain and paints light onto canvas — Europe’s miracle of bourgeois power.",
    ),
    "RUS": dict(
        leaders="Boris Godunov; Time of Troubles claimants; Romanov founding (Michael).",
        religion="Orthodox; patriarchal institution; Uniate conflict to the west.",
        culture="After Troubles consolidation; icons and bells; serfdom hardening.",
        story="The Time of Troubles — famine, false Dmitrys, Polish occupation of Moscow — ends with a new Romanov dynasty elected from desperation.",
    ),
    "SWE": dict(
        leaders="Gustavus Adolphus; Christina; Charles X/XI beginnings.",
        religion="Lutheran great power.",
        culture="Military innovation; Baltic empire; Uppsala learning.",
        story="Gustavus Adolphus — ‘Lion of the North’ — dies at Lützen as Sweden briefly decides Germany’s fate.",
    ),
    "TUR": dict(
        leaders="Ahmed I; Köprülü viziers later; sultans of the post-Süleyman plateau.",
        religion="Sunni imperial Islam; millet continuities.",
        culture="Tulip-era still ahead; classical Ottoman architecture’s afterglow; Mediterranean and Central European war rhythm.",
        story="Ottoman pressure and Habsburg defense set the tempo of southeastern European life long after Süleyman’s death.",
    ),
    "POL": dict(
        leaders="Sigismund III Vasa; Władysław IV; John II Casimir (Deluge era).",
        religion="Catholic Counter-Reformation strengthening; Orthodox and Protestant nobles under pressure.",
        culture="Sarmatian noble ideology; elected monarchy; huge multiethnic realm.",
        story="The mid-17th-century Deluge — Swedish invasion devastating the Commonwealth — marks the turn from golden liberty to long decline.",
    ),
    "ITA": dict(
        leaders="Spanish viceroys; popes; Savoy dukes; Venetian doges.",
        religion="Baroque Catholicism; scientific trials (Galileo).",
        culture="Baroque art and music; Galilean science under constraint.",
        story="Galileo’s trial becomes modernity’s parable of science vs authority — more complicated historically, irresistible as story.",
    ),
}


MODERN_EXTRA = {
    "GBR": dict(
        leaders="Victoria to present constitutional monarchs; PMs from Gladstone/Disraeli memory to contemporary cabinets.",
        religion="Plural: Anglican establishment legacy, free churches, Catholic and non-Christian communities, widespread secularization.",
        culture="Industrial then post-industrial society; global English; welfare state and its critics.",
        story="From workshop of the world and empire to Brexit-era European renegotiation — continuity of parliamentary myth under radical economic change.",
    ),
    "FRA": dict(
        leaders="Republican presidents and earlier revolutionary/Napoleonic memory still structuring politics.",
        religion="Laïcité as state doctrine over Catholic heritage; growing religious pluralism.",
        culture="Republican school; universalist claims; global art/philosophy prestige.",
        story="1789’s legacy — rights and terror alike — remains France’s master story, replayed in every crisis of the republic.",
    ),
    "DEU": dict(
        leaders="Post-1945 democratic leadership in FRG/Berlin Republic; memory of Bismarck, Weimar, and Nazi criminality as negative foundation.",
        religion="Catholic/Protestant inheritances; large secular and immigrant communities.",
        culture="Social market economy; Vergangenheitsbewältigung; European integration engine.",
        story="Auschwitz and division, then Ostpolitik and reunification (1990): Germany’s modern identity is responsibility before glory.",
    ),
    "ESP": dict(
        leaders="From Franco’s dictatorship to parliamentary monarchy (Juan Carlos → Felipe VI) and democratic parties.",
        religion="Catholic culture under rapid secularization; regional identities.",
        culture="Transition culture; autonomous communities; EU membership remaking economy.",
        story="The Pact of Forgetting and its unraveling — how a democracy buries and then reopens civil-war memory.",
    ),
    "ITA": dict(
        leaders="Post-war republican politics; earlier Mussolini as negative founding memory; EU-era premiers.",
        religion="Catholic society and Vatican neighbor; secularization.",
        culture="Design, film, regional cuisines as soft power; industrial north / agrarian south historic split.",
        story="From Fascism’s fall and resistance myth to ‘il sorpasso’ and recurring political instability — creativity beside fragile parties.",
    ),
    "POL": dict(
        leaders="Solidarność generation; post-1989 democratic leaders; EU-era politics.",
        religion="Catholicism as resistance identity under communism, contested in pluralism since.",
        culture="Romantic independence tradition; EU mobility; war memory (WW2).",
        story="Shipyard strikes in Gdańsk (1980) begin the crack in the Eastern Bloc — a trade union that helped end an empire.",
    ),
    "RUS": dict(
        leaders="Soviet general secretaries in memory; Yeltsin; Putin-era presidency.",
        religion="Orthodox revival after Soviet atheism; minorities of many faiths.",
        culture="High literary canon; petro-state geopolitics; Soviet memory wars.",
        story="1991’s flag over the Kremlin ends the USSR; the post-Soviet story is unresolved empire, oligarchy, and war — still rewriting Europe’s map.",
    ),
    "SWE": dict(
        leaders="Constitutional monarchs; Social Democratic architects of the folkhem; contemporary coalition politics.",
        religion="Lutheran heritage under deep secularization; new religious diversity.",
        culture="Welfare model; design; non-alignment tradition under pressure.",
        story="The folkhem — ‘people’s home’ — is Sweden’s modern founding myth of equality, now debated in an age of migration and insecurity.",
    ),
    "UKR": dict(
        leaders="Post-1991 presidents; Maidan-era civic leadership; wartime presidency.",
        religion="Orthodox jurisdictions in flux; Greek Catholic west; pluralism.",
        culture="Language politics; Cossack memory; European aspiration.",
        story="Maidan (2014) and full-scale invasion (2022) make Ukraine’s sovereignty the defining European story of the early 21st century.",
    ),
    "TUR": dict(
        leaders="Atatürk’s republican founding memory; elected governments; Erdoğan-era presidency.",
        religion="Secular republic over Muslim society; contested laicism.",
        culture="Between Europe and Middle East; Ottoman nostalgia vs republican modernity.",
        story="Gallipoli and the War of Independence found the republic; EU accession’s stall and Middle Eastern wars keep Turkey’s European question open.",
    ),
    "GRC": dict(
        leaders="Post-junta democratic leaders; EU-era premiers through debt crisis.",
        religion="Greek Orthodoxy as cultural establishment; secular youth.",
        culture="Classical heritage tourism; shipping; crisis cinema and politics.",
        story="The 2010s debt crisis — austerity, protest, near-Grexit — tests whether European solidarity is real.",
    ),
    "NLD": dict(
        leaders="Constitutional monarchs; coalition prime ministers; EU founding role.",
        religion="Protestant/Catholic pillars secularized into ‘anything goes’ tolerance myth and its critics.",
        culture="Trade, design, managed landscape; colonial memory debates.",
        story="From pillarization to progressive showcase to migration politics — the Netherlands as Europe’s laboratory of liberal order.",
    ),
}


MIGRATION_EXTRA = {
    "ITA": dict(
        leaders="Odoacer; Theodoric the Great; Justinian’s generals (Belisarius, Narses).",
        religion="Arian Gothic elites over Catholic Romans; Byzantine Orthodoxy in reconquest.",
        culture="Senatorial Roman continuity under Gothic rule; Ravenna mosaics.",
        story="Theodoric’s long peace and the Gothic War’s devastation bookend Italy’s transformation from Western Empire to early medieval patchwork.",
    ),
    "GBR": dict(
        leaders="Traditional heptarchy kings; later narrative figures (Vortigern, Arthur as legend — not documentary).",
        religion="British Christianity in the west; incoming Anglo-Saxon paganism then conversion (Augustine 597 still near this horizon).",
        culture="Post-Roman material simplicity; epic memory forming; Irish missions.",
        story="The Adventus Saxonum — migration, war, and settlement — becomes England’s origin debate: invasion myth vs gradual cultural change.",
    ),
    "FRA": dict(
        leaders="Clovis; Merovingian kings; early mayors of the palace.",
        religion="Clovis’s Catholic baptism allies Franks with Gallo-Roman bishops against Arian rivals.",
        culture="Lex Salica; warrior retinues; Gallo-Roman villa afterlives.",
        story="Clovis’s baptism is France’s oldest royal conversion story — a pagan warlord choosing Catholic Rome’s prestige.",
    ),
    "ESP": dict(
        leaders="Visigothic kings at Toledo; earlier Vandal passage memory.",
        religion="Visigothic Arianism then conversion to Catholicism (Reccared); Jewish policy harshening.",
        culture="Toledo councils; fusion law codes; Roman infrastructure reuse.",
        story="Visigothic Spain’s unity-under-Toledo is later remembered as the Christian kingdom Islam will overrun in 711 — an origin told backward from al-Andalus.",
    ),
    "DEU": dict(
        leaders="Merovingian frontier kings; Alamannic and Bavarian dukes; Thuringian rulers.",
        religion="Pagan districts beside Christian Frankish power; Irish/Anglo-Saxon missions coming.",
        culture="Row-grave horizons; warrior burials; forest-agrarian society.",
        story="East of the Rhine is not ‘Germany’ yet — a mosaic of peoples being pulled into Frankish Christianity.",
    ),
    "POL": dict(
        leaders="Archaeological cultures more than named kings (Wielbark).",
        religion="Pagan; Christianity centuries away.",
        culture="Wielbark burial rite changes; amber and trade.",
        story="Wielbark’s link to Gothic migrations is archaeology’s great detective story — cemeteries hinting at peoples later famous on the Black Sea and in Italy.",
    ),
    "UKR": dict(
        leaders="Gothic and steppe elites in Chernyakhov horizons; Hunnic overlords.",
        religion="Diverse; Christian missions limited; steppe cults.",
        culture="Multi-ethnic Chernyakhov villages; Hunnic shock mobility.",
        story="The Hunnic storm empties and remakes the Pontic edge — Attila’s Europe begins in these grasslands.",
    ),
    "GRC": dict(
        leaders="Eastern Roman (Byzantine) emperors — Arcadius to Justinian’s eve.",
        religion="Imperial Christianity defining orthodoxy through councils.",
        culture="Constantinople as New Rome; Greek civic life under Christian empire.",
        story="While the West fragments, the East still taxes, debates theology, and calls itself Roman — continuity as the Balkans’ baseline.",
    ),
}


def expand_region_descriptions(period: dict, texts: dict[str, str]):
    for rid, text in texts.items():
        if rid in period.get("regions", {}):
            period["regions"][rid]["description"] = text


HIGH_REGION_TEXTS = {
    "britain": (
        "Norman conquest installs a French-speaking military elite atop an English population; by 1200 the Angevin/Plantagenet "
        "realm ties England to half of France until Capetian reconquest. Magna Carta politics, common-law growth, Gothic "
        "cathedrals, and crusading culture define the age. Wales faces Edwardian conquest later in the century; Scotland "
        "fights for independence; Ireland’s lordship remains incomplete. Genetics: elite Norman input on an early medieval "
        "English majority — institutions and language contact change faster than deep ancestry."
    ),
    "france": (
        "Capetian kings from Philip Augustus onward turn a sacred demesne into a territorial state: Normandy seized, "
        "Languedoc crushed in the Albigensian Crusade, Louis IX’s holy monarchy, Paris university theology. Gothic "
        "architecture radiates from Île-de-France. Occitan culture suffers political defeat without total demographic "
        "replacement. Ancestry remains medieval French continua under intensifying royal fiscal-military power."
    ),
    "iberia": (
        "Las Navas de Tolosa breaks Almohad hegemony; Castile and Aragon expand; Portugal consolidates Atlantic "
        "independence; Granada endures as Islam’s last peninsula foothold. Toledo’s translation culture, military orders, "
        "and convivencia under strain shape society. Demography mixes Christian northerners, Andalusi Muslims, and Jews — "
        "politics of conquest and confession on medieval Iberian ancestries."
    ),
    "central": (
        "The Hohenstaufen drama, elective empire, eastward German settlement (Ostsiedlung), Přemyslid/Luxemburg Bohemia, "
        "and Piast Poland’s fragmentation-and-reunion fill Central Europe. Towns under Magdeburg law, Minnesang, and "
        "crusading orders on the Baltic define culture. Genetics track medieval German, Slavic, and Magyar continua with "
        "settler mobility — not a new deep component."
    ),
    "scandinavia": (
        "Christian kingdoms of Denmark, Norway, and Sweden integrate into Latin Europe: archbishoprics, written laws, "
        "crusades toward Finland and the eastern Baltic. Old Norse literary culture flowers in Icelandic manuscripts. "
        "Ancestry is Nordic medieval continuity after Viking-Age consolidations."
    ),
    "italy": (
        "Communal cities, papal monarchy, Frederick II’s Sicilian state, and maritime republics (Venice, Genoa) make Italy "
        "Europe’s political laboratory. Mendicant orders remake piety; universities and vernacular poetry rise toward Dante. "
        "Ancestry: Italian medieval urban–rural mixes with Mediterranean trade contacts."
    ),
    "balkans": (
        "Byzantium’s Komnenian then Palaiologan struggles; Second Bulgarian Empire; Serbian rise under Nemanjići; Hungarian "
        "oversight in Croatia. Orthodox and Catholic frontiers harden. Genetics: Balkan medieval continua; the story is "
        "empire, schism, and Slavic kingship."
    ),
    "eastern": (
        "Kievan Rus’ fragments under princely feuds then Mongol conquest (1237–40); successor principalities and the "
        "Golden Horde reorders the east; Lithuania expands into Ruthenian lands. Church Slavonic culture persists under "
        "steppe suzerainty. Deep ancestry unchanged in kind; political gravity shifts toward Moscow and Vilnius later."
    ),
}


def main():
    data = json.loads(PATH.read_text())
    periods = data["periods"]
    by_id = {p["id"]: p for p in periods}

    # Enrich existing medieval-adjacent periods
    enrich_existing_polities(by_id["migration"], MIGRATION_EXTRA)
    enrich_existing_polities(by_id["frankish"], FRANKISH_EXTRA)
    enrich_existing_polities(by_id["high-medieval"], HIGH_MED_EXTRA)
    expand_region_descriptions(by_id["high-medieval"], HIGH_REGION_TEXTS)
    enrich_existing_polities(by_id["early-modern"], EARLY_MODERN_EXTRA)
    enrich_existing_polities(by_id["modern"], MODERN_EXTRA)

    # Ensure every polity in those periods has the new keys
    for pid in ("migration", "frankish", "high-medieval", "early-modern", "modern"):
        for iso, pol in by_id[pid].get("polities", {}).items():
            for k in ("leaders", "religion", "culture", "story"):
                pol.setdefault(k, "")

    vikings = make_vikings(by_id["frankish"], by_id["high-medieval"])
    late = make_late_medieval(by_id["high-medieval"], by_id["early-modern"])
    reformation = make_reformation(late, by_id["early-modern"])

    # Rebuild period list (strip prior inserts so re-runs stay clean)
    insert_ids = {"vikings", "late-medieval", "reformation"}
    base = [p for p in periods if p["id"] not in insert_ids]
    new_periods = []
    for p in base:
        new_periods.append(p)
        if p["id"] == "frankish":
            new_periods.append(vikings)
        if p["id"] == "high-medieval":
            new_periods.append(late)
            new_periods.append(reformation)
    data["periods"] = new_periods

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("periods:", len(data["periods"]))
    for p in data["periods"]:
        npol = len(p.get("polities") or {})
        print(f"  {p['tickYear']:10} {p['id']:18} polities={npol:3} layers={len(p.get('mapLayers') or [])}")


if __name__ == "__main__":
    main()
