#!/usr/bin/env python3
"""Add literature / art blurbs + material-culture images to every polity."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "timeline.json"

# Curated Wikimedia Commons thumbs (public domain / free licenses).
# Format: id -> {src, alt, caption}
IMG = {
    "loschbour": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Cheddar%20Man%2C%20National%20History%20Museum%2C%20London.jpg?width=640",
        "alt": "Forager-age facial reconstruction (Cheddar Man) — Mesolithic Europe’s human face",
        "caption": "Forager-age facial reconstruction (Cheddar Man) — Mesolithic Europe’s human face",
    },
    "magdalenian": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/La%20Madeleine%20bison%20licking%20its%20flank.jpg?width=640",
        "alt": "Magdalenian bison carving — Ice Age art you can hold",
        "caption": "Magdalenian bison carving — Ice Age art you can hold",
    },
    "cardial": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Cer%C3%A1mica%20cardial-La%20Sarsa%20%28Espa%C3%B1a%29.jpg?width=640",
        "alt": "Cardial impressed pottery — Neolithic sea-farmers’ clay signature",
        "caption": "Cardial impressed pottery — Neolithic sea-farmers’ clay signature",
    },
    "lbk": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Schkeuditz%20Kumpf%201%2002.jpg?width=640",
        "alt": "Linearbandkeramik vessel — inland farming’s spiral-banded clay",
        "caption": "Linearbandkeramik vessel — inland farming’s spiral-banded clay",
    },
    "megalith": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Stonehenge%20Heel%20Stone.jpg?width=640",
        "alt": "Stonehenge — Atlantic megalithic theatre of stone",
        "caption": "Stonehenge — Atlantic megalithic theatre of stone",
    },
    "yamnaya_kurgan": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Kurgan%20stelae%2C%20Tanais.jpg?width=640",
        "alt": "Kurgan / steppe stelae world — burial monuments of pastoral power",
        "caption": "Kurgan / steppe stelae world — burial monuments of pastoral power",
    },
    "wheel": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/0854%20Ein%20Krug%20aus%20Bronocice%2C%203.550%20v.%20Chr..JPG?width=640",
        "alt": "Bronocice pot — early European wagon image",
        "caption": "Bronocice pot — early European wagon image",
    },
    "corded": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Corded%20Ware%20culture.jpg?width=640",
        "alt": "Corded Ware ceramics — cord as decoration and identity",
        "caption": "Corded Ware ceramics — cord as decoration and identity",
    },
    "battleaxe": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Drawing%20of%20a%20finnish%20battle%20axe%20during%20the%20Corded%20War%20Culture.png?width=640",
        "alt": "Stone battle-axe type of the Corded Ware north",
        "caption": "Stone battle-axe type of the Corded Ware north",
    },
    "beaker": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Bell%20Beaker%20artefacts%2C%20Spain.jpg?width=640",
        "alt": "Bell Beaker assemblage — drinking fashion of a migration age",
        "caption": "Bell Beaker assemblage — drinking fashion of a migration age",
    },
    "bronze_sword": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Bronze%20swords-MGR%20Lyon-IMG%209734.jpg?width=640",
        "alt": "Bronze Age sword — portable authority in metal",
        "caption": "Bronze Age sword — portable authority in metal",
    },
    "solar_chariot": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Solvogn%20bagside.jpg?width=640",
        "alt": "Trundholm sun chariot — Bronze Age sun theology",
        "caption": "Trundholm sun chariot — Bronze Age sun theology",
    },
    "rock_art": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Tanum%20Vitlycke%20unesco%20IMG%204733%20ship.jpg?width=640",
        "alt": "Tanum rock carvings — ships and blades in Swedish granite",
        "caption": "Tanum rock carvings — ships and blades in Swedish granite",
    },
    "hallstatt": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Hochdorf%20dagger%20with%20gold%20foil.jpg?width=640",
        "alt": "Hochdorf gold dagger — Hallstatt elite metalwork",
        "caption": "Hochdorf gold dagger — Hallstatt elite metalwork",
    },
    "celtic_helmet": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Ceremonial%20Celtic%20Helmet%20from%20III%20century%20BC%20Gaul%20%28Agris%20Charente%29.jpg?width=640",
        "alt": "Agris helmet — Celtic parade armor as sculpture",
        "caption": "Agris helmet — Celtic parade armor as sculpture",
    },
    "scythian": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Scythian%20gold%20pectoral%20Tovsta%20Mohyla%20%28detail%204%29.jpg?width=640",
        "alt": "Scythian gold — steppe animal style at its richest",
        "caption": "Scythian gold — steppe animal style at its richest",
    },
    "greek_vase": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Exekias%20-%20ABV%20146%2021%20-%20Dionysos%20reclining%20in%20a%20ship%20-%20fight%20-%20M%C3%BCnchen%20AS%208729%20-%2002.jpg?width=640",
        "alt": "Exekias’s Dionysus cup — myth painted as black-figure verse",
        "caption": "Exekias’s Dionysus cup — myth painted as black-figure verse",
    },
    "roman_armor": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Lorica%20segmentata%20remains%20and%20recreation.jpg?width=640",
        "alt": "Lorica segmentata — Rome’s industrial armour aesthetic",
        "caption": "Lorica segmentata — Rome’s industrial armour aesthetic",
    },
    "augustus": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Statue-Augustus.jpg?width=640",
        "alt": "Augustus of Prima Porta — empire wearing a god’s calm",
        "caption": "Augustus of Prima Porta — empire wearing a god’s calm",
    },
    "sutton_hoo": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Sutton%20Hoo%20helmet%202016.png?width=640",
        "alt": "Sutton Hoo helmet — Migration-age kingship in iron and myth",
        "caption": "Sutton Hoo helmet — Migration-age kingship in iron and myth",
    },
    "theodoric": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Mausoleum%20of%20Theodoric%20%28Ravenna%29%20-%20Exterior.jpg?width=640",
        "alt": "Mausoleum of Theodoric — Gothic geometry after Rome",
        "caption": "Mausoleum of Theodoric — Gothic geometry after Rome",
    },
    "book_kells": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/KellsFol032vChristEnthroned.jpg?width=640",
        "alt": "Book of Kells — Insular Gospel art as labyrinth",
        "caption": "Book of Kells — Insular Gospel art as labyrinth",
    },
    "charlemagne": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Charlemagne%20Agostino%20Cornacchini%20Vatican.jpg?width=640",
        "alt": "Charlemagne in Vatican stone — Carolingian imperial memory",
        "caption": "Charlemagne in Vatican stone — Carolingian imperial memory",
    },
    "viking_ship": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Osebergskipet%202016.jpg?width=640",
        "alt": "Oseberg ship — Viking Age oak as vessel and tomb",
        "caption": "Oseberg ship — Viking Age oak as vessel and tomb",
    },
    "viking_helmet": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Gjermundbu%20helmet%20-%20cropped.jpg?width=640",
        "alt": "Gjermundbu helmet — a real Viking helm (no horns)",
        "caption": "Gjermundbu helmet — a real Viking helm (no horns)",
    },
    "bayeux": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Bayeux%20Tapestry%20scene57%20Harold%20death.jpg?width=640",
        "alt": "Bayeux Tapestry — embroidery as war chronicle",
        "caption": "Bayeux Tapestry — embroidery as war chronicle",
    },
    "chartres": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Cath%C3%A9drale%20Notre-Dame%20%28Chartres%29%20%282%29.jpg?width=640",
        "alt": "Chartres Cathedral — High Gothic light as theology",
        "caption": "Chartres Cathedral — High Gothic light as theology",
    },
    "icon": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Christ%20Pantocrator%20Deesis%20mosaic%20Hagia%20Sophia.jpg?width=640",
        "alt": "Christ Pantocrator, Hagia Sophia — mosaic gaze of empire",
        "caption": "Christ Pantocrator, Hagia Sophia — mosaic gaze of empire",
    },
    "knight": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Late%20medieval%20armour%20complete%20%28gothic%20plate%20armour%29.jpg?width=640",
        "alt": "Late medieval plate armour — the body as fortress",
        "caption": "Late medieval plate armour — the body as fortress",
    },
    "joan": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Jeanne%20d%20Arc%281412-1431%29%20Miniaturmalerei%2015%20Jahrhundert.jpg?width=640",
        "alt": "Joan of Arc miniature — visionary as painted myth",
        "caption": "Joan of Arc miniature — visionary as painted myth",
    },
    "alhambra": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Pavillon%20Cour%20des%20Lions%20Alhambra%20Granada%20Spain.jpg?width=640",
        "alt": "Court of the Lions, Alhambra — Nasrid paradise architecture",
        "caption": "Court of the Lions, Alhambra — Nasrid paradise architecture",
    },
    "botticelli": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Sandro%20Botticelli%20046.jpg?width=640",
        "alt": "Botticelli’s Birth of Venus — Florence’s myth of beauty",
        "caption": "Botticelli’s Birth of Venus — Florence’s myth of beauty",
    },
    "luther": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Ninety-Five%20Theses%20WDL7497.png?width=640",
        "alt": "Ninety-five Theses — Reformation as print event",
        "caption": "Ninety-five Theses — Reformation as print event",
    },
    "armour_ren": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Parade%20armour.jpg?width=640",
        "alt": "Parade armour — Renaissance metal couture",
        "caption": "Parade armour — Renaissance metal couture",
    },
    "rembrandt": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/La%20ronda%20de%20noche%2C%20por%20Rembrandt%20van%20Rijn.jpg?width=640",
        "alt": "Rembrandt’s Night Watch — civic militia as light storm",
        "caption": "Rembrandt’s Night Watch — civic militia as light storm",
    },
    "velazquez": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Las%20Meninas%2C%20by%20Diego%20Vel%C3%A1zquez%2C%20from%20Prado%20in%20Google%20Earth.jpg?width=640",
        "alt": "Velázquez’s Las Meninas — the court looking back",
        "caption": "Velázquez’s Las Meninas — the court looking back",
    },
    "versailles": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Chateau%20Versailles%20Galerie%20des%20Glaces.jpg?width=640",
        "alt": "Hall of Mirrors, Versailles — absolutism as glass and gold",
        "caption": "Hall of Mirrors, Versailles — absolutism as glass and gold",
    },
    "industrial": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Philipp%20Jakob%20Loutherbourg%20d.%20J.%20002.jpg?width=640",
        "alt": "Coalbrookdale by Night — industry as sublime fire",
        "caption": "Coalbrookdale by Night — industry as sublime fire",
    },
    "impression": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Monet%20-%20Impression%2C%20Sunrise.jpg?width=640",
        "alt": "Monet’s Impression, Sunrise — modern seeing begins",
        "caption": "Monet’s Impression, Sunrise — modern seeing begins",
    },
    "icon_rublev": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Andrey%20Rublev%20-%20%D0%A1%D0%B2.%20%D0%A2%D1%80%D0%BE%D0%B8%D1%86%D0%B0%20-%20Google%20Art%20Project.jpg?width=640",
        "alt": "Rublev’s Trinity — Orthodox color at its quiet peak",
        "caption": "Rublev’s Trinity — Orthodox color at its quiet peak",
    },
    "ottoman_tile": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Iznik%20tiles%2C%20Istanbul%20Archaeological%20Museums.jpg?width=640",
        "alt": "Iznik tiles — Ottoman gardens fired onto walls",
        "caption": "Iznik tiles — Ottoman gardens fired onto walls",
    },
    "kilt": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Highlander-kilt.jpg?width=640",
        "alt": "Highland dress — tartan as identity and romance",
        "caption": "Highland dress — tartan as identity and romance",
    },
    "polish_hussar": {
        "src": "https://commons.wikimedia.org/wiki/Special:FilePath/Husarz%2C%20J%C3%B3zef%20Brandt%2C%201890.jpg?width=640",
        "alt": "Winged hussar — Commonwealth cavalry theatre",
        "caption": "Winged hussar — Commonwealth cavalry theatre",
    },
}

def imgs(*ids):
    out = []
    for i in ids:
        if i in IMG:
            out.append(dict(IMG[i]))
    return out


# period -> default arts package
PERIOD_DEFAULTS = {
    "mesolithic": {
        "literature": (
            "No written literature — meaning lived in seasonal rounds, place-names now lost, and "
            "oral lore we can only infer from ethnography and later myth residues. Think of fire-circle "
            "narrative, hunting songs, and cosmologies tied to rivers and herds rather than books."
        ),
        "art": (
            "Portable art and landscape marks: engraved bone, amber, microlith geometries, and the long "
            "afterglow of Paleolithic cave painting traditions. Dress is hide, fur, antler toggles; "
            "weaponry is bow, microlith-armed projectile, and wood-hafted axe."
        ),
        "images": ["magdalenian", "loschbour"],
    },
    "early-neolithic": {
        "literature": (
            "Still pre-literate in Europe. Story survives as ritual architecture and ceramic style: "
            "foundation deposits, house-burning rites, and the first farming songs we cannot hear — "
            "only the pots and longhouses that staged them."
        ),
        "art": (
            "Cardial/Impresso and LBK pottery as mobile art; polished stone axes as prestige tools; "
            "woven textiles beginning to replace pure hide economies. Figurines in some Balkan contexts "
            "hint at household cults."
        ),
        "images": ["cardial", "lbk"],
    },
    "middle-neolithic": {
        "literature": (
            "Megalithic Europe speaks in stone alignments and passage-grave orientations — a literature "
            "of astronomy and ancestry without alphabet. Later folklore about giants and stone tables "
            "is a distant echo, not a primary source."
        ),
        "art": (
            "Megalithic art (Breton carved stones, Irish kerbstones), TRB ceramics, jadeitite axe "
            "circulation. Dress inferred from textile impressions and ornaments of amber and copper at the edges."
        ),
        "images": ["megalith", "lbk"],
    },
    "yamnaya": {
        "literature": (
            "No Yamnaya texts. Comparative Indo-European poetics later reconstructs a world of sky gods, "
            "cattle wealth, and praise of patrons — a hypothetical echo chamber, not a recovered library. "
            "Treat reconstructed hymns as models, not quotations from the steppe."
        ),
        "art": (
            "Kurgans, stone stelae, early wagons, cord-decorated pots on the steppe edge. Dress: wool and "
            "leather pastoral kit; weaponry: tanged daggers, early metal, composite bows in the wider steppe kit."
        ),
        "images": ["yamnaya_kurgan", "wheel"],
    },
    "beaker-corded": {
        "literature": (
            "Still pre-literate. Meaning travels in burial theatre: single graves, gendered grave goods, "
            "drinking vessels. Later IE epic genres are centuries downstream — useful analogies, not Corded Ware novels."
        ),
        "art": (
            "Cord-impressed amphorae, battle-axes, Bell Beaker ‘archery packages,’ copper daggers, gold "
            "lunulae in the Atlantic. Fashion itself is the art: a pan-European lookbook of pots and weapons."
        ),
        "images": ["corded", "battleaxe", "beaker"],
    },
    "nordic-bronze": {
        "literature": (
            "No native scripts in the Nordic zone; meaning is cut into rock and cast in bronze. Later Eddic "
            "myth is a distant Iron/Viking-Age reframing — handle as comparative poetry, not Bronze Age reportage."
        ),
        "art": (
            "Sun chariots, lur horns, folding stools, ornate swords, and Bohuslän/Tanum rock art fleets. "
            "Dress: wool cloaks, belt plates, tutulus ornaments — the European Bronze Age at its most theatrical."
        ),
        "images": ["solar_chariot", "rock_art", "bronze_sword"],
    },
    "iron-age": {
        "literature": (
            "Celts enter Greek and Roman ethnography (Poseidonius, Caesar) while keeping their own oral "
            "learned classes — druids, bards, vates. Epic and law live in memory; we overhear them through "
            "hostile or fascinated classical prose. Further east, steppe peoples appear in Herodotus’s glittering hearsay."
        ),
        "art": (
            "La Tène curvilinear metalwork, Agris-style helmets, torcs, painted ceramics, Hallstatt elite wagons. "
            "Dress: colorful woolens, brooches, trousers on northern fighters that shocked toga-minded writers."
        ),
        "images": ["celtic_helmet", "hallstatt", "scythian"],
    },
    "classical": {
        "literature": (
            "Full literary blaze: Greek epic and drama already classic; Latin poetry and history rising "
            "(Virgil, Livy, Cicero). In the provinces, local languages persist under Latin/Greek prestige. "
            "This is the first period where clickable states can quote real verses, not only artifacts."
        ),
        "art": (
            "Marble idealism, frescoes, mosaics, military kit standardized into imperial style. Dress codes "
            "broadcast status — toga, stola, trousers as barbarian tell. Architecture is politics in colonnades."
        ),
        "images": ["greek_vase", "augustus", "roman_armor"],
    },
    "migration": {
        "literature": (
            "Latin letters continue in bishops’ cities; Gothic and other tongues carry oral epic. Later "
            "Beowulf and continental hero legends preserve a Migration-Age mood of hall, feud, and gold — "
            "composed afterward, remembering this world of warbands."
        ),
        "art": (
            "Cloisonné garnets, animal-style metalwork, spathae, shield bosses, and ship funerals. Dress: "
            "brooch sets that map gender and ethnicity in graves; Roman military fashion recycled by new kings."
        ),
        "images": ["sutton_hoo", "theodoric"],
    },
    "frankish": {
        "literature": (
            "Carolingian Latin renewal (Alcuin, Einhard’s Life of Charlemagne), vernacular beginnings, "
            "and in the isles the flowering of Old English and Insular Latin. Annals invent yearly time; "
            "hagiography invents holy celebrities."
        ),
        "art": (
            "Illuminated Gospels, palace chapels, spangenhelm lineages, pattern-welded swords. Dress: "
            "belt suites, silk from the east for elites, monastic habits as anti-fashion."
        ),
        "images": ["book_kells", "charlemagne", "viking_ship"],
    },
    "vikings": {
        "literature": (
            "Skaldic praise poetry, eddic myth in oral form, Anglo-Saxon chronicle prose, Arabic travel "
            "notices of the northmen, and Slavic Primary Chronicle seeds. This is an age of named poets "
            "and infamous nicknames — literature as reputation management."
        ),
        "art": (
            "Dragon-prowed ships, gripping-beast woodcarving, runestones as public text-art, richly "
            "dressed chamber graves. Weaponry: pattern-welded swords, axe, shield; dress: layered wool, "
            "silk trims, Thor’s-hammer pendants beside crosses."
        ),
        "images": ["viking_ship", "viking_helmet", "book_kells"],
    },
    "high-medieval": {
        "literature": (
            "Troubadour and minnesang lyric, chansons de geste, Arthurian romance, Norse kings’ sagas, "
            "Slavic and Byzantine court letters, Arabic Andalusi poetry. Universities invent the scholastic "
            "sentence; vernaculars invent the love song and the crusade boast."
        ),
        "art": (
            "Gothic cathedrals, illuminated psalters, heraldry as wearable graphic design, mail evolving "
            "toward coats of plates. Dress: bliauts, surcoats, veils — status cut in cloth."
        ),
        "images": ["chartres", "bayeux", "icon"],
    },
    "late-medieval": {
        "literature": (
            "Dante, Chaucer, Froissart’s chronicles, husite songs, Balkan epic cycles forming around Kosovo, "
            "humanist Latin returning in Italian cities. Vernaculars now carry philosophy, insult, and nation-feeling."
        ),
        "art": (
            "International Gothic, early Netherlandish oil, plate armour couture, Flamboyant stone lace. "
            "Dress becomes armor’s soft twin — dagged sleeves and gold chains for a plague-scarred aristocracy."
        ),
        "images": ["knight", "joan", "alhambra", "botticelli"],
    },
    "reformation": {
        "literature": (
            "Print multiplies argument: Luther’s German Bible, Calvin’s Institutes, Tudor scripture politics, "
            "Rabelaisian laughter, early essay and sonnet cultures. Pamphlets are the period’s missile type."
        ),
        "art": (
            "Confessional image wars — iconoclasm vs baroque persuasion beginning; parade armour as metal "
            "humanism; court portraiture fixing faces into ideology."
        ),
        "images": ["luther", "armour_ren", "velazquez"],
    },
    "early-modern": {
        "literature": (
            "Shakespearean theatre, Cervantes, classical French drama, Dutch and Spanish Golden Age prose, "
            "scientific letters. Europe invents the modern author-celebrity and the global report."
        ),
        "art": (
            "Baroque light storms, Dutch genre interiors, Versailles optics, Ottoman tile gardens still "
            "shaping southeastern eyes. Dress: ruffs, justaucorps, janissary spectacle — fashion as statecraft."
        ),
        "images": ["rembrandt", "velazquez", "versailles", "ottoman_tile"],
    },
    "modern": {
        "literature": (
            "National canons, modernist fracture, postcolonial argument, EU multilingual culture industries. "
            "Poetry and novels become the museum of feelings nations tell about themselves — and argue with."
        ),
        "art": (
            "From industrial sublime to Impressionism to contemporary biennales; folk costume revived as "
            "heritage; military uniform as the last total clothing system. Dress democratizes while brands feudalize desire."
        ),
        "images": ["industrial", "impression", "kilt"],
    },
}

# Extra per (period_id, iso) — elaborate overrides
SPECIAL = {
    ("beaker-corded", "GBR"): {
        "literature": (
            "Britain’s Beaker age leaves no texts, but it leaves a funerary grammar: beakers by the face, "
            "archer wrist-guards, copper knives. Later British poetry of barrows and ‘ancient Britons’ is "
            "Victorian dreamwork laid over this genomic rupture — read it as reception, not reportage. "
            "The real ‘literature’ is the grave as staged sentence: who drinks, who owns metal, who lies crouched."
        ),
        "art": (
            "Bell Beakers of Maritime and All-Over-Cord styles; gold lunulae and sun discs in the wider "
            "Insular package; flint arrowheads as jewelry of violence. Imagine dyed wool cloaks, leather "
            "archer kits, and the first widespread metallurgy glittering at funerals — fashion after a nearly "
            "total population turnover."
        ),
        "images": ["beaker", "battleaxe", "megalith"],
    },
    ("beaker-corded", "DEU"): {
        "literature": (
            "Corded Ware’s central European heartland speaks through single-grave choreography and cord "
            "decoration — a ceramic dialect. Later Germanic verse is a distant cousin at best; do not put "
            "Beowulf in a Corded Ware mouth. Praise of patrons and cattle may be older Indo-European habits, "
            "but here they are archaeological silence surrounding loud pots."
        ),
        "art": (
            "Cord-impressed amphorae, faceted battle-axes, hammer-headed pins. Male graves often shout with "
            "weapons; female kits with ornaments — a gendered art of the dead that structured living fashion."
        ),
        "images": ["corded", "battleaxe", "wheel"],
    },
    ("nordic-bronze", "SWE"): {
        "literature": (
            "Tanum’s rocks are a bronze epic without words: keels, blades, suns, mating couples, processions. "
            "Read the granite as stanza. Later Eddas remember a mythic north; these petroglyphs are the "
            "older, wordless libretto of ships and gods of light."
        ),
        "art": (
            "Petroglyph flotillas, belt plates, tutuli, folding stools, and bronze lurs. Elite dress was "
            "metallic punctuation on wool — a sun cult you could wear to a funeral pyre."
        ),
        "images": ["rock_art", "solar_chariot", "bronze_sword"],
    },
    ("nordic-bronze", "DNK"): {
        "literature": (
            "The Trundholm chariot is a one-object poem: a gilded sun pulled by a bronze horse on a ritual "
            "wagon. Oak-coffin burials with textiles preserve bodies as soft sculpture. No runes yet — "
            "meaning is metal and cloth."
        ),
        "art": (
            "Sun chariot, oak-coffin costumes (string skirts, wrap dresses), shaving knives, swords with "
            "horn hilts. Denmark’s Bronze Age is Europe’s best-dressed prehistoric cemetery."
        ),
        "images": ["solar_chariot", "bronze_sword", "rock_art"],
    },
    ("iron-age", "FRA"): {
        "literature": (
            "Gaul’s learned men kept law and lore unwritten by principle, says Caesar — so we meet them "
            "through his war diary and Greek ethnography. Bardic praise and druidic cosmology are real "
            "institutions glimpsed in hostile paraphrase. The land later grows troubadours; their ancestors "
            "here still sing in the air only."
        ),
        "art": (
            "La Tène bronze, painted pottery, mirror backs, the Agris helmet’s gold vinework. Trousers and "
            "checked woolens; torcs as neck sentences of rank. Chariots still flash in early La Tène parade "
            "before cavalry fully inherits their glamour."
        ),
        "images": ["celtic_helmet", "hallstatt"],
    },
    ("classical", "ITA"): {
        "literature": (
            "Rome’s voice: Virgil’s imperial nostalgia, Ovid’s metamorphoses, Catullus’s insults, Livy’s "
            "moral republic. Latin becomes the software of European memory for fifteen centuries. In the "
            "streets, Oscan and Greek still murmur — empire is multilingual under the toga’s brand."
        ),
        "art": (
            "Prima Porta politics, Pompeian fresco gardens, engineering as beauty (aqueduct, road, dome). "
            "Lorica, gladius, scutum — the legionary as modular sculpture. Elite dress weaponizes white wool."
        ),
        "images": ["augustus", "roman_armor", "greek_vase"],
    },
    ("classical", "GRC"): {
        "literature": (
            "Homer already antique; tragedy and philosophy still the curriculum of being Greek under Rome. "
            "Plutarch teaches parallel lives; Pausanias walks sanctuaries into prose. The eastern Mediterranean "
            "is a library with a navy."
        ),
        "art": (
            "Classical marble reused and copied for Roman patrons; painted pottery’s last great flourishes; "
            "theatre masks as portable faces of myth. Dress: himation elegance against Roman fashion pressure."
        ),
        "images": ["greek_vase", "augustus"],
    },
    ("migration", "GBR"): {
        "literature": (
            "Latin survives in British clergy; Old English poetry will later remember this age’s mood — "
            "halls, feud, sea-roads — in Beowulf and elegy. Oral formulaic verse is the period’s true press."
        ),
        "art": (
            "Sutton Hoo’s ship burial aesthetic (slightly later in the long Migration arc), cloisonné gold, "
            "pattern-welded blades. Dress: Germanic brooch pairs, woven bands, Roman recycling."
        ),
        "images": ["sutton_hoo", "viking_helmet"],
    },
    ("migration", "ITA"): {
        "literature": (
            "Cassiodorus and Boethius try to keep Latin thought alive under Gothic kings; the Consolation "
            "of Philosophy is a prison lamp. Ostrogothic Ravenna speaks in mosaic as much as in edict."
        ),
        "art": (
            "Theodoric’s mausoleum, Arian baptisteries, court dress mixing Roman purple and Gothic gold. "
            "Weaponry still late-Roman in cut, new in patronage."
        ),
        "images": ["theodoric", "roman_armor"],
    },
    ("frankish", "FRA"): {
        "literature": (
            "Einhard’s Charlemagne, capitularies as prose of power, monastic histories. The vernacular is "
            "gathering strength offstage for later chansons de geste that will reinvent this age as epic."
        ),
        "art": (
            "Aachen’s palace chapel memory, illuminated manuscripts, spurs and long swords of heavy cavalry "
            "becoming the Frankish brand. Dress: cloaks fastened for war assemblies; silk as diplomatic bribe."
        ),
        "images": ["charlemagne", "book_kells"],
    },
    ("frankish", "GBR"): {
        "literature": (
            "Alfred’s translation program — Pastoral Care, Boethius, Psalms — invents English as a language "
            "of state thought. The Anglo-Saxon Chronicle pins years like nails. Riddles and elegies glitter in Exeter’s book."
        ),
        "art": (
            "Insular manuscript carpet pages, Alfred Jewel glamour, burh earthworks as landscape art. "
            "Dress: West Saxon elite kits meeting Norse styles in the Danelaw contact zone."
        ),
        "images": ["book_kells", "sutton_hoo", "viking_ship"],
    },
    ("vikings", "NOR"): {
        "literature": (
            "Skalds mint kennings like jewelry; kings buy stanzas with rings. Later kings’ sagas will "
            "novelize this century — here the live form is praise screamed over mead."
        ),
        "art": (
            "Oseberg’s carved prow, gripping beasts, ship-burial textiles. Helmets rare; axes common; "
            "silk from the east on fjord bodies. Fashion is mobility made visible."
        ),
        "images": ["viking_ship", "viking_helmet"],
    },
    ("vikings", "DNK"): {
        "literature": (
            "Jelling stones are literature in runes — public theology of conquest and conversion. "
            "Skaldic networks tie Denmark to England’s courts under Cnut."
        ),
        "art": (
            "Jelling mounds and rune art, Mammen style axes, English plunder remounted as Danish prestige. "
            "Dress: North Sea elite cosmopolitanism — wool, fur, and baptismal politics."
        ),
        "images": ["viking_ship", "viking_helmet", "bayeux"],
    },
    ("vikings", "GBR"): {
        "literature": (
            "Chronicle entries of raids as horror serial; skaldic verses for Cnut’s court; Irish Sea "
            "sagas later remembering Dublin’s Norse. Place-names become a poem of settlement."
        ),
        "art": (
            "Hybrid Anglo-Scandinavian sculpture, hogbacks, weapon burials fading under Christian pressure. "
            "Dress codes collide in York’s streets — a fashion city of the millennium."
        ),
        "images": ["viking_ship", "sutton_hoo", "book_kells"],
    },
    ("high-medieval", "FRA"): (
        {
            "literature": (
                "Chrétien’s Arthurian laboratories, fabliaux laughter, university quodlibets, crusade "
                "chronicles. French becomes Europe’s prestige vernacular of romance — soft power before the word."
            ),
            "art": (
                "Chartres and Saint-Denis invent Gothic light theology; ivory Madonnas; heraldic surcoats. "
                "Mail hauberks, great helms, and horse caparisons turn war into movable stained glass."
            ),
            "images": ["chartres", "knight", "bayeux"],
        }
    ),
    ("high-medieval", "GBR"): {
        "literature": (
            "Latin court prose, Anglo-Norman romance, early Middle English stirring under French roofs. "
            "Magna Carta is a legal poem of clauses; chroniclers make kings into cautionary stanzas."
        ),
        "art": (
            "Early English Gothic, Opus Anglicanum embroidery exported like treasure, heraldry exploding "
            "after the Conquest’s memory. Mail, kite shields, and castles as the island’s brutal sculpture garden."
        ),
        "images": ["bayeux", "chartres", "knight"],
    },
    ("high-medieval", "ESP"): {
        "literature": (
            "Andalusi Arabic lyric, Hebrew Golden Age verse, Castilian epic beginnings (Poema de Mio Cid "
            "tradition), Toledo as translation engine. Three languages argue inside one peninsula’s music."
        ),
        "art": (
            "Mudéjar brick geometry, Romanesque pilgrimage roads, military-order castles, ivory and silk "
            "from Mediterranean workshops. Dress: Christian northern woolens facing Andalusi refinement."
        ),
        "images": ["alhambra", "knight"],
    },
    ("high-medieval", "ITA"): {
        "literature": (
            "Toward Dante’s century: civic chronicles, Franciscan song, Provençal fashion in Sicilian "
            "schools. Italy rehearses the vernacular cosmos."
        ),
        "art": (
            "Communal towers, panel painting beginnings, mendicant churches, armor of condottieri still ahead. "
            "Dress: mercantile display in dyes Byzantium and Flanders can envy."
        ),
        "images": ["botticelli", "icon", "knight"],
    },
    ("high-medieval", "GRC"): {
        "literature": (
            "Byzantine historiography and hymnography; court rhetoric as weapon. After 1204, exile "
            "literature mourns and schemes in Greek."
        ),
        "art": (
            "Mosaic and icon continuity, silk administration, military fashion of kataphraktoi memory. "
            "Hagia Sophia remains the building that teaches what empire looks like from inside light."
        ),
        "images": ["icon", "ottoman_tile"],
    },
    ("late-medieval", "FRA"): {
        "literature": (
            "Froissart’s pageantry prose, Christine de Pizan’s city of ladies, farce and mystery play, "
            "Joan’s trial record as involuntary saint’s life. French literature learns to process catastrophe."
        ),
        "art": (
            "Flamboyant Gothic, Burgundian court spectacle, early panel painting, full plate’s rise. "
            "Dress: poulaines and houppelandes — silhouettes as status algorithms after the plague."
        ),
        "images": ["joan", "knight", "chartres"],
    },
    ("late-medieval", "GBR"): {
        "literature": (
            "Chaucer’s pilgrimage comedy, Langland’s vision-politics, Gawain’s green-girdle ethics, "
            "Lollard English scripture anxiety. Middle English becomes capable of a nation talking to itself."
        ),
        "art": (
            "Perpendicular Gothic, alabaster saints, illuminated London, plate armour and longbow as "
            "English export brands. Dress: livery jackets turning politics into color blocks."
        ),
        "images": ["knight", "bayeux", "chartres"],
    },
    ("late-medieval", "ITA"): {
        "literature": (
            "Dante’s cosmos, Petrarch’s inwardness, Boccaccio’s human comedy — the Italian trecento "
            "rewires European imagination before oil paint finishes the job."
        ),
        "art": (
            "Giotto to early Renaissance panels, civic sculpture, armor of display, silk and armorers’ "
            "cities. Florence teaches Europe that bankers can buy eternity in fresco."
        ),
        "images": ["botticelli", "knight"],
    },
    ("late-medieval", "ESP"): {
        "literature": (
            "Cancionero lyric, Catalan chivalric romance, Arabic’s last Andalusi gardens of verse in Granada, "
            "chronicle as Reconquista screenplay."
        ),
        "art": (
            "Nasrid stucco heavens at the Alhambra, Isabeline Gothic beginnings, mudéjar persistence. "
            "Dress: frontier hybridity — silk and steel in the same wardrobe."
        ),
        "images": ["alhambra", "knight"],
    },
    ("late-medieval", "POL"): {
        "literature": (
            "Latin chronicles, Ruthenian chancery prose, oral epic on the Lithuanian–Teutonic frontier. "
            "Grünwald becomes a stanza nations will keep rewriting."
        ),
        "art": (
            "Brick Gothic, knightly culture shared with Christendom, Orthodox icons in the east of the union. "
            "Dress: European chivalric fashion on a multiethnic body politic."
        ),
        "images": ["knight", "polish_hussar", "icon_rublev"],
    },
    ("reformation", "DEU"): {
        "literature": (
            "Luther’s German — a literary big bang — plus Flugschriften, Meistergesang, and confessional "
            "hymn. The vernacular becomes a battlefield with chorales for artillery."
        ),
        "art": (
            "Cranach’s propaganda portraits, iconoclast whitewash vs Catholic splendor, landsknecht "
            "slash-and-puff costume as walking stained glass. Printmaking is the period’s true fresco."
        ),
        "images": ["luther", "armour_ren"],
    },
    ("reformation", "GBR"): {
        "literature": (
            "Tyndale’s English dangers, Cranmer’s Prayer Book music-prose, mid-Tudor polemics, sonnet "
            "culture warming toward Elizabethan theatre. Scripture in the mother tongue remakes inward life."
        ),
        "art": (
            "Whitewashed churches, Holbein’s embassy of faces, parade armour for a navy-minded crown. "
            "Dress: farthingales and ruffs — Protestant courts still addicted to silk geometry."
        ),
        "images": ["armour_ren", "luther", "bayeux"],
    },
    ("reformation", "ITA"): {
        "literature": (
            "Machiavelli already teaching cold statecraft; Castiglione’s courtier manners; poetic epic "
            "after Ariosto; Index lists as anti-library. Italy writes the rules even when Spain owns the boards."
        ),
        "art": (
            "Late Renaissance and Mannerism, Michelangelo’s overwhelming bodies, armorers of Milan, "
            "Tridentine image discipline. Dress: Spanish black elegance colonizing Italian color."
        ),
        "images": ["botticelli", "armour_ren"],
    },
    ("reformation", "ESP"): {
        "literature": (
            "Mystics (Teresa, John of the Cross), picaresque beginnings, imperial chronicle, censorship "
            "as co-author. Spanish prose learns to confess and to conquer in the same century."
        ),
        "art": (
            "Escorial granite theology, early Golden Age painting, Morisco ornament under suspicion. "
            "Dress: sober Habsburg black as the empire’s Instagram filter."
        ),
        "images": ["velazquez", "armour_ren", "alhambra"],
    },
    ("reformation", "TUR"): {
        "literature": (
            "Ottoman divan poetry, gazel lyric, narrative of gazi wars; Greek and Slavic Christian "
            "literatures continue under the patriarchate. Empire is a stack of canons."
        ),
        "art": (
            "Sinan’s domes, Iznik tiles, illuminated manuscripts, janissary dress as state costume drama. "
            "Weaponry: composite bow still noble beside firearms learning their manners."
        ),
        "images": ["ottoman_tile", "icon"],
    },
    ("early-modern", "NLD"): {
        "literature": (
            "Dutch Golden Age poetry and pamphlet storm, Spinoza’s dangerous clarity, travel writing from "
            "a planet-spanning VOC. A republic talks in print like a continuous town meeting."
        ),
        "art": (
            "Rembrandt’s militia theatre, Vermeer’s quiet rooms, marine painting as national self-portrait. "
            "Dress: black broadcloth wealth — Calvinist chic that fools no one about the money."
        ),
        "images": ["rembrandt", "armour_ren"],
    },
    ("early-modern", "FRA"): {
        "literature": (
            "Corneille/Racine classical severities, Molière’s social X-rays, early novel experiments, "
            "salon wit as political sport under intensifying monarchy."
        ),
        "art": (
            "Versailles as total artwork of kingship, academic painting rules, ballet as state ritual. "
            "Dress: justaucorps and ribbons — the body remade as court diagram."
        ),
        "images": ["versailles", "rembrandt"],
    },
    ("early-modern", "ESP"): {
        "literature": (
            "Cervantes invents the modern novel’s self-awareness; Lope’s theatre ocean; Quevedo’s barbs. "
            "An empire declining in cash still rich in sentences."
        ),
        "art": (
            "Velázquez’s mirror games, Zurbarán’s stark saints, still life as theology of objects. "
            "Dress and armor in portraits keep claiming a world already slipping."
        ),
        "images": ["velazquez", "rembrandt"],
    },
    ("early-modern", "GBR"): {
        "literature": (
            "Shakespeare’s late echoes into Jacobean drama, Metaphysical poets, Milton’s cosmic republicanism, "
            "early newspapers. English becomes greedy enough to hold a universe and a civil war."
        ),
        "art": (
            "Van Dyck’s court glamour, masque design, emerging scientific illustration. Dress: cavalier "
            "locks vs crop-headed piety — haircuts as civil war."
        ),
        "images": ["armour_ren", "rembrandt", "versailles"],
    },
    ("early-modern", "RUS"): {
        "literature": (
            "Chronographs, saint’s lives, Avvakum’s raw autobiography of schism — Russian prose learning "
            "to burn. Oral bylina epics still carry bogatyr heroes beside church books."
        ),
        "art": (
            "Onion domes, iconostasis gold, growing baroque borrowings, fur and pearl parade of boyars. "
            "Weaponry: sabre and increasingly gunpowder on steppe edges."
        ),
        "images": ["icon_rublev", "polish_hussar"],
    },
    ("modern", "FRA"): {
        "literature": (
            "From Balzac’s social zoology to Baudelaire’s crowds, Camus’s refusals, and global Francophone "
            "echoes — French letters as Europe’s long seminar on modernity."
        ),
        "art": (
            "Impressionism’s optical coup, fashion as export religion, cinema’s early capitals. Dress: "
            "haute couture invents seasons; the street invents attitude."
        ),
        "images": ["impression", "industrial"],
    },
    ("modern", "GBR"): {
        "literature": (
            "Industrial novels, modernist experiment, postcolonial English, and poetry that still argues "
            "with Shakespeare’s ghost in every classroom."
        ),
        "art": (
            "Turner to Britart, BBC polish, subcultural style explosions (punk, rave). Highland romanticism "
            "rebrands tartan after clearance and empire."
        ),
        "images": ["industrial", "impression", "kilt"],
    },
    ("modern", "DEU"): {
        "literature": (
            "Goethe’s shadow, Kafka’s bureaucrats, postwar Trümmerliteratur, and novels that treat memory "
            "as a moral technology. German is a language haunted by its own clarity."
        ),
        "art": (
            "Bauhaus reason, Expressionist scream, memorial architecture, techno’s civic night churches. "
            "Dress: from dirndl revival politics to Berlin black."
        ),
        "images": ["industrial", "impression"],
    },
    ("modern", "ITA"): {
        "literature": (
            "Leopardi to Ferrante — Italian prose of beauty and fracture; film scripts as national literature "
            "with better lighting."
        ),
        "art": (
            "Futurism’s speed worship, neorealist streets, design (Olivetti to Memphis) as soft power. "
            "Dress: Milan invents desire’s logistics."
        ),
        "images": ["botticelli", "impression"],
    },
    ("modern", "ESP"): {
        "literature": (
            "Generation of ’98 wounds, Lorca’s lyric, Civil War poetry, and democratic boom novels — "
            "Spain writing itself out of silence."
        ),
        "art": (
            "Picasso’s Guernica as global scream, Dalí’s brand surrealism, post-Franco movida. Dress: "
            "region and runway in ongoing argument."
        ),
        "images": ["velazquez", "impression"],
    },
    ("modern", "POL"): {
        "literature": (
            "Romantic messianism, Miłosz and Szymborska’s moral clarity, reportage traditions — literature "
            "as national nervous system under partitions and party."
        ),
        "art": (
            "Poster art genius, Chopin’s export ghost, Solidarity’s graphic simple courage. Hussar wings "
            "return as heritage cosplay and meme."
        ),
        "images": ["polish_hussar", "industrial"],
    },
    ("modern", "RUS"): {
        "literature": (
            "Pushkin to Tolstoy to Soviet and post-Soviet argument — a literature that treats the soul as "
            "a public utility and a crime scene."
        ),
        "art": (
            "Icons to Malevich to film montage; monumentalism and its mockers. Dress: imperial parade "
            "vs Soviet uniformity vs oligarch gloss."
        ),
        "images": ["icon_rublev", "industrial"],
    },
}


# Fix mistaken tuple wrapping for high-medieval FRA
SPECIAL[("high-medieval", "FRA")] = {
    "literature": (
        "Chrétien’s Arthurian laboratories, fabliaux laughter, university quodlibets, crusade "
        "chronicles. French becomes Europe’s prestige vernacular of romance — soft power before the word."
    ),
    "art": (
        "Chartres and Saint-Denis invent Gothic light theology; ivory Madonnas; heraldic surcoats. "
        "Mail hauberks, great helms, and horse caparisons turn war into movable stained glass."
    ),
    "images": ["chartres", "knight", "bayeux"],
}


def apply_package(pol: dict, package: dict):
    lit = package.get("literature")
    art = package.get("art")
    image_ids = package.get("images") or []
    if lit:
        pol["literature"] = lit
    if art:
        pol["art"] = art
    if image_ids:
        pol["images"] = imgs(*image_ids)
    pol.setdefault("literature", "")
    pol.setdefault("art", "")
    pol.setdefault("images", [])


def iso_flavor(iso: str, period_id: str) -> dict:
    """Light per-country seasoning on top of period defaults."""
    flavors = {
        "GBR": " Insular voices and North Sea contact give this place a distinctive accent in the wider European chorus.",
        "IRL": " Irish monastic and later Gaelic learned traditions punch above demographic weight in Europe’s imagination.",
        "FRA": " French courts and vernaculars repeatedly set continental fashions of word and dress.",
        "DEU": " German lands often host the workshop — print, metal, and later industrial form — for Europe’s ideas.",
        "ITA": " Italian cities teach prestige: from Roman monumentality to Renaissance brand management of beauty.",
        "ESP": " Iberia’s art of contact — Christian, Jewish, Islamic — keeps Europe from pretending it was ever only Latin.",
        "PRT": " Portugal’s Atlantic gaze turns European art toward oceans and return cargoes of style.",
        "GRC": " Greek language and forms remain a reusable antiquity — quarried by every later age for prestige.",
        "RUS": " Russian and wider Rus’ cultures translate Byzantine inheritance into forest and empire scales.",
        "UKR": " Borderland creativity — Cossack, Ruthenian, and European currents braided under dangerous skies.",
        "POL": " Polish–Lithuanian and later Polish culture specializes in noble liberty myths and romantic survival art.",
        "SWE": " Swedish culture often exports northern clarity — from rock art to modern design temperaments.",
        "DNK": " Danish gatekeeping of the Baltic Sound makes culture a toll-booth as well as a stage.",
        "NOR": " Norwegian arts remember ships first — keel as national metaphor from Oseberg to oil platforms.",
        "TUR": " Ottoman and Anatolian layers make this edge of the map a second classical continuum for Europe to face.",
        "NLD": " Low Countries urbanism turns painting, print, and cloth into a civic theology of detail.",
        "BEL": " Flemish workshops paint Europe’s devotion and cloth trade in the same luminous oil.",
        "CHE": " Alpine republican myths and mercenary fame produce a spare, stubborn aesthetic of autonomy.",
        "AUT": " Habsburg capitals stage empire as opera — multilingual, ceremonial, slightly melancholic.",
        "HUN": " Hungarian culture keeps a steppe-origin memory inside a Latin-Christian and later Habsburg frame.",
        "CZE": " Bohemian lands repeatedly host Europe’s heresies and modernisms a few years early.",
        "FIN": " Finnish oral epic (later Kalevala) and modern design both treat forest silence as a material.",
        "LTU": " Lithuanian culture remembers being Europe’s last great pagan power — then a bilingual republic of letters.",
        "BGR": " Bulgarian letters pioneer Slavic Christian literacy — a soft empire of books south of the Danube.",
        "SRB": " Serbian epic song turns defeat into repertoire; the gusle outlasts many maps.",
        "HRV": " Croatian culture faces both Rome and Byzantium — a shoreline of scripts and loyalties.",
        "ROU": " Romanian lands keep Latin memory in a Slavic-Orthodox sea — language as archaeological survival.",
        "ALB": " Albanian frontier culture preserves distinct speech under successive empires’ costumes.",
        "ISL": " Iceland’s medieval republic writes Europe’s greatest vernacular prose museum — the sagas.",
    }
    extra = flavors.get(iso, " Local workshops and courts give the shared European repertoire a regional grain.")
    return {"note": extra}


def main():
    data = json.loads(PATH.read_text())
    n = 0
    for period in data["periods"]:
        pid = period["id"]
        base = PERIOD_DEFAULTS.get(pid, {
            "literature": "Cultural expression in this horizon mixes oral tradition, ritual, and material style.",
            "art": "Artifacts, dress, and monuments carry meaning where texts are thin or uneven.",
            "images": ["megalith"],
        })
        for iso, pol in (period.get("polities") or {}).items():
            package = {
                "literature": base["literature"],
                "art": base["art"],
                "images": list(base.get("images") or []),
            }
            special = SPECIAL.get((pid, iso))
            if special:
                package.update(special)
            else:
                flavor = iso_flavor(iso, pid)
                # Append a short local accent without duplicating whole paragraphs
                if package.get("literature") and flavor["note"] not in package["literature"]:
                    package["literature"] = package["literature"].rstrip() + flavor["note"]
                if package.get("art") and flavor["note"] not in package["art"]:
                    package["art"] = package["art"].rstrip() + flavor["note"]

            # Normalize image ids if special provided ids
            if package.get("images") and isinstance(package["images"][0], str):
                pass
            elif package.get("images") and isinstance(package["images"][0], dict):
                # already resolved — re-extract ids impossible; keep
                pol["literature"] = package["literature"]
                pol["art"] = package["art"]
                pol["images"] = package["images"]
                n += 1
                continue

            apply_package(pol, package)
            n += 1

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    # verify
    sample = None
    for p in data["periods"]:
        if p["id"] == "vikings" and "NOR" in p["polities"]:
            sample = p["polities"]["NOR"]
            break
    print("enriched polities:", n)
    print("sample NOR vikings images:", len(sample.get("images") or []), sample.get("literature", "")[:80])


if __name__ == "__main__":
    main()
