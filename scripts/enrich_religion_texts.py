#!/usr/bin/env python3
"""Add / expand polity religion notes: beliefs + rituals where archaeology or texts allow.

Skips inventing pantheons for poorly attested Mesolithic cases beyond burial/ritual evidence.
Idempotent: only fills missing fields or expands texts shorter than MIN_KEEP.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "timeline.json"

# Do not shrink already-rich notes
MIN_KEEP = 95

# periodId -> iso -> religion text (beliefs + rituals, concise)
NEW = {
    "mesolithic": {
        # Cautious: ritual archaeology only — no invented deities
        "ESP": "Belief systems unrecoverable in detail. Ritual archaeology: ochre-stained and curated burials, rare structured deposits, and landscape reuse of Paleolithic art places.",
        "GBR": "No recoverable pantheon. Shell-midden and cave burials, ochre, and curated human bone suggest ancestor/body rites; cosmology itself stays opaque.",
        "FRA": "Forager ritual poorly named. Archaeology shows careful burials, ochre, and occasional animal deposits — practice without readable myths.",
        "DEU": "Mesolithic belief content is lost. Scattered burials and structured faunal deposits hint at rites around death and animals, not temples or texts.",
        "DNK": "Maglemosian–Kongemose ritual known mainly from graves and bog finds. No named gods; body treatment and wetland deposition are the evidence.",
        "SWE": "Coastal forager ritual inferred from burials and later northern sacred landscapes. Deities and myths are not recoverable for this horizon.",
        "NOR": "Fosna–Hensbacka / Komsa ritual is thinly attested: coastal camps, rare burials, and later rock-art traditions still far in the future.",
        "ITA": "Epigravettian-descended foragers leave burial and ornament evidence; Mediterranean rock shelters hold ritual deposits without readable theology.",
        "SRB": "Iron Gates cemeteries show elaborate body treatment, sculptures, and house–burial links — unusually rich ritual archaeology for Mesolithic Europe.",
        "UKR": "Forest-steppe forager ritual: burials with ochre and grave goods. Named gods and afterlife doctrines are not recoverable.",
        "RUS": "Eastern forest HG ritual mainly visible in burials and later forest sacred-place traditions; avoid projecting historic Finno-Ugric pantheons backward wholesale.",
    },
    "early-neolithic": {
        "DEU": "LBK farmers practiced domestic and enclosure ritual: foundation deposits, cattle offerings, and cemetery rows. Ancestor care and fertility rites are inferred; named gods are not.",
        "HUN": "Starčevo–Körös villages show figurines, house rituals, and formal burials. Beliefs center on household and fertility cult practice more than temples.",
        "ESP": "Cardial communities combine cave/open-air ritual with early megalithic experiments. Burial and ceramic deposits mark ancestor and place cults.",
        "ITA": "Impresso/Cardial Italy: household figurines, cave rites, and emerging formal cemeteries — agrarian ritual without written pantheons.",
        "GRC": "Early Greek Neolithic villages use figurines, hearth/house deposits, and cemetery rites. Later Olympian names must not be read back into this phase.",
        "DNK": "Ertebølle holdouts keep forager burial/wetland rites beside earliest TRB farmer ceremonies — two ritual regimes in contact, not one creed.",
        "GBR": "Earliest Neolithic Britain imports chambered-tomb and causewayed-enclosure rites: collective burial, feasting debris, and seasonal gathering places.",
        "UKR": "Bug–Dniester / farmer-fringe ritual mixes forager burial habits with incoming agrarian figurines and domestic deposits along the contact zone.",
    },
    "middle-neolithic": {
        "GBR": "Atlantic megalithic religion: collective tombs, ancestor bone circulation, and solar-aligned monuments (e.g. Stonehenge landscape). Ritual feasting at causewayed enclosures.",
        "FRA": "Chasséen / Breton–Atlantic megaliths: passage graves, menhirs, and enclosure ceremonies. Ancestor veneration and landscape sacralization dominate the evidence.",
        "DEU": "TRB / Michelsberg: enclosure rituals, cattle offerings, and early megalithic tombs. Community ancestor cult more visible than individual named deities.",
        "UKR": "Cucuteni–Trypillia: house figurines, intentional house burning, and cemetery rites — domestic and settlement-scale cult practice at huge agrarian sites.",
        "DNK": "TRB Scandinavia: megalithic tombs, amber offerings, and wetland deposits. Ancestor burial architecture is the clearest ritual signature.",
        "SWE": "TRB farmers build megalithic tombs while Pitted Ware coasts keep forager ritual. Two sacral geographies — chambered ancestors vs marine/forager deposits.",
        "POL": "TRB / early GAC: megalithic and flat cemeteries, animal offerings, and enclosure rites. GAC cattle-and-amber ritual intensifies toward the steppe contact zone.",
    },
    "yamnaya": {
        "UKR": "Yamnaya steppe religion is read from kurgans: ochre-covered flexed burials, wagons/animal offerings, and stelae. Sky/ancestor pastoral cult inferred; no native texts.",
        "RUS": "Pontic–Caspian kurgan rite: single elite graves under mounds, ochre, weapons, and sacrificed animals — status afterlife and pastoral cosmology in earth and herd.",
        "HUN": "Yamnaya-related Carpathian Basin graves import kurgan burial grammar (ochre, mounds, pastoral goods) into farmer Europe’s ritual map.",
        "ESP": "Los Millares / Copper Age Iberia: fortified ritual centers, collective and emerging individual tombs, idol plaques — not Yamnaya kurgans, but parallel sacral intensification.",
        "GBR": "Late Neolithic Britain: continuing megalithic and henge rites (Stonehenge landscape) before Beaker individual graves rewrite burial fashion.",
        "ITA": "Remedello / Gaudo: Copper Age cemeteries with weapon graves and formal rite — Italian paths to status burial without steppe kurgans.",
        "DEU": "GAC → Corded Ware dawn: cattle-centered offerings and changing grave rites as steppe-related practices approach temperate Europe.",
    },
    "beaker-corded": {
        "DEU": "Corded Ware: gendered single graves (battle-axe male package), amphora/beaker offerings, and ancestral mound reuse. Steppe-linked burial ideology over older megalithic collectivity.",
        "POL": "Corded Ware Poland: flexed single inhumations with axes and ceramics; ritual individuality and martial male symbolism dominate cemetery evidence.",
        "DNK": "Single Grave: barrow burials with corded beaker and battle-axe kits. New funerary grammar replacing TRB megalithic collective rites.",
        "SWE": "Battle Axe Culture: boat-axe graves and beaker offerings — northern Corded Ware ritual package with strong male martial display.",
        "GBR": "Bell Beaker Britain: individual graves with beaker, copper/bronze, and archer kits; henge landscapes still used. Beaker rite overlays older monumental religion.",
        "ESP": "Bell Beaker Iberia: beaker graves and prestige metal beside older Copper Age idol/tomb traditions — mixed ritual landscape, not pure steppe copy.",
        "FRA": "Beaker / late CW France: beaker inhumations and residual megalithic reuse. Atlantic and continental ritual packages meet in cemeteries.",
        "NLD": "Dutch/Rhine Beakers: single graves with beaker sets along river corridors — classic western Beaker funerary package.",
        "UKR": "Catacomb steppe: niche graves under kurgans, ochre, and weapon offerings — evolved Yamnaya-related funerary religion on the Pontic plain.",
        "ITA": "Italian Beaker / EBA: beaker graves and local Copper Age cemetery continuity; Mediterranean ritual vocabularies absorb the beaker fashion selectively.",
    },
    "nordic-bronze": {
        "DNK": "Nordic Bronze Age: sun-cult imagery (Trundholm chariot), rock-art processions, weapon/ornament hoards in bogs, and rich barrow burials — cosmology performed with metal and water.",
        "SWE": "Bohuslän-type rock art, ship and sun motifs, and wetland hoards. Elite barrows and offering lakes structure a solar/maritime ritual world.",
        "NOR": "Coastal rock art, cairns, and metal hoards. Ritual emphasizes seascape, boats, and deposited wealth more than temples.",
        "GBR": "Wessex / British BA: rich barrow burials, ceremonial landscapes around older henges, and prestige metal deposition — ancestor and status cult in chalk country.",
        "ESP": "El Argar: intramural and cemetery burials with sharp status grading; Argaric ritual is household/tomb-focused rather than Nordic sun-chariot religion.",
        "DEU": "Tumulus Culture: barrow cemeteries, weapon graves, and bronze hoards. Central European BA religion visible mainly as funerary and deposition rites.",
        "ITA": "Terramare: settlement rituals, structured deposits, and cemetery practice in embanked villages — Po-plain civic-sacral order without Nordic rock-art cosmology.",
        "GRC": "Mycenaean palaces: named gods appear in Linear B (e.g. Poseidon, Potnia); palace sacrifice, libation, and tholos/chamber tombs. First European written pantheon fragments.",
        "UKR": "Srubnaya: timber-grave steppe rite under kurgans with weapons and animal offerings — continuing Pontic funerary religion into the Late Bronze Age.",
    },
    "iron-age": {
        "FRA": "La Tène Gallic religion: polytheism later named by Romans (e.g. syncretized Mercury/Teutates types); rituals include sanctuary deposits, weapon offerings, and funerary feasting. Druids as learned ritual specialists in classical reports.",
        "GBR": "British Iron Age: shrine deposits, bog/river offerings, chariot burials in the east, and hillfort ceremonial spaces. Local gods later equated with Roman deities after conquest.",
        "IRL": "Irish Iron Age ritual: royal sites (Tara, Emain), bog deposits, and later mythic cycles that must be used cautiously as Iron Age evidence. Sovereignty and otherworld themes dominate later texts.",
        "DEU": "Jastorf / La Tène frontier: weapon and bog offerings, cremation cemeteries, and sacred enclosures. Germanic and Celtic ritual zones meet without a single pantheon list.",
        "ESP": "Iberian & Celtiberian cults: sanctuaries, inscribed deity names in places, warrior/funerary stelae, and cave or high-place rites — local pantheons, not a uniform Celtic church.",
        "ITA": "Rome vs Etruscans/Samnites: Roman state cult (Jupiter, Mars, Vesta) with augury and sacrifice; Etruscan haruspicy and tomb ritual; Italian peoples keep distinct sanctuary traditions.",
        "GRC": "Greek poleis: Olympian pantheon, civic temples, blood sacrifice, festivals (Panathenaia, Dionysia), oracles, and mystery cults (Eleusis). Religion is public liturgy as much as private piety.",
        "BGR": "Thracian kingdoms: royal burials with rich grave goods, rock sanctuaries, and later Greek reports of Zalmoxis/immortality ideas — elite funerary religion at the core.",
        "UKR": "Scythian nomads: kurgan elites, horse sacrifice, cannabis/vapor rites in Herodotus, and golden ritual gear. Ancestor and sky/animal cult inferred from graves and art.",
        "AUT": "Hallstatt / early La Tène elites: princely graves, banqueting ritual, and sanctuary deposits in the Alpine foreland — status afterlife and feasting ideology.",
    },
    "classical": {
        "ITA": "Roman civic polytheism: Jupiter–Juno–Minerva and household Lares/Penates; blood sacrifice, augury, and calendrical festivals. Rising imperial cult, plus mystery religions (Isis, Mithras) in the army and cities.",
        "FRA": "Roman Gaul: interpretatio Romana of Celtic gods, imperial cult centers (Lugdunum), and Gallo-Roman temples. Native deposition rites continue beside Roman sacrifice and priesthoods.",
        "ESP": "Roman Hispania: imperial and civic cults, Iberian/Celtiberian survivals in rural sanctuaries, and mystery cults in towns. Sacrifice, vows (ex-votos), and emperor worship structure public religion.",
        "GBR": "Roman Britannia: classical temples and imperial cult in towns; Mithraea on the frontier; local deities syncretized (e.g. Sulis Minerva). Rural shrines and votive deposits persist.",
        "DEU": "Limes religion: Roman camps host Jupiter, standards-cult, and Mithras; Magna Germania beyond the Rhine keeps Germanic votive and funerary rites outside imperial liturgy.",
        "GRC": "Roman Greece: classical temples and festivals continue under Roman rule; imperial cult joins civic polytheism. Philosophical schools debate gods while sacrifice still defines public piety.",
        "TUR": "Roman Asia Minor: dense temple cities, imperial cult, Greek civic gods, and mystery/healing sanctuaries (e.g. Asclepius). Processions and benefactor religion animate urban life.",
        "ROU": "Dacia contested: Geto-Dacian sacral kingship and sanctuary traditions meet Roman military cult after conquest — imperial religion imposed on a resistant ritual landscape.",
        "IRL": "Hibernia outside the Empire: Iron Age–style royal sites, bog deposits, and local gods. No Roman civic cult; later Christian conversion still centuries away.",
        "UKR": "Sarmatian steppe: kurgan burial, horse gear, and nomadic cult practice. Greek cities of the coast keep Hellenic temples at the edge of the pastoral world.",
    },
}

# Expansions for short historical one-liners: period -> iso -> fuller text
EXPAND = {
    "migration": {
        "POL": "Wielbark communities practice cremation and inhumation with Scandinavian links; gods unnamed in texts. Christianity is still a distant Roman/Byzantine horizon, not a local church yet.",
        "UKR": "Chernyakhov / Gothic steppe edge mixes Germanic, Sarmatian, and local rites — kurgans, weapon graves, and limited Christian contact. Steppe cults and household offerings outrank organized churches.",
        "HUN": "Sarmatian and early steppe groups keep horse-and-kurgan funerary religion; Roman Christian missions are peripheral. Local cult practice, not dioceses, structures the sacred.",
        "TUR": "Imperial Christianity of the Eastern Roman world: episcopal cities, liturgy, relics, and Christological debate. Monasteries and pilgrimage already shape Anatolian sacred geography.",
    },
    "frankish": {
        "DEU": "Latin Christianity with royal and episcopal sponsorship; baptism, Mass, and saints’ cults structure public life. Missionary pushes east plant churches among Saxons and neighbors, often with political force.",
        "ITA": "Rome’s Latin papacy, Greek Orthodoxy in the south, and rising Islam in Sicily create a three-way ritual map — Mass, Byzantine liturgy, and congregational prayer on one peninsula.",
        "ESP": "Al-Andalus: Islamic prayer, Qur’anic law, and mosque life; northern Christian kingdoms keep Mass and saints; Jewish communities maintain synagogue and law. Three ritual civilizations in one peninsula.",
        "IRL": "Christian monastic Ireland (Mass, reliquaries, high crosses) meets pagan Norse newcomers whose gods and ship-burial rites convert unevenly in the towns.",
        "DNK": "Norse pagan sacrifice and hall cult dominate; Ansgar-style missions plant fragile churches. Baptism is still a royal/port phenomenon, not a finished conversion.",
        "NOR": "Norse paganism — blót, burial mounds, and sacred groves — remains dominant. Christian contact arrives via trade and raid; forced conversion is still ahead.",
        "SWE": "Uppsala-centered pagan cult memory, local blót, and mound burial persist while Varangian routes bring Byzantine and Latin Christian contact religions east and west.",
        "TUR": "Greek Orthodoxy: Divine Liturgy, icons, and monasticism under iconoclast/iconophile controversy. Imperial church and holy images are political as well as sacred.",
        "BGR": "Bulgar elite paganism gives way to Slavic Orthodoxy after conversion: baptism, liturgy in Slavic, and a new patriarchal church tying rule to rite.",
        "UKR": "Rus’ river road remains largely pagan (Perun and related cults in later memory) while Byzantine and missionary Christianity arrive along trade — baptism still episodic.",
    },
    "vikings": {
        "DNK": "Royal conversion to Latin Christianity: baptism, church-building, and Jelling-style monuments. Pagan blót and mound rites survive in places as the kingdom’s public religion flips.",
        "NOR": "Aggressive royal Christianization suppresses local blót and temple cults; baptism and parish foundations remake the ritual map, not without resistance.",
        "PRT": "Latin Christian frontier: Mass, saints, and military-religious pressure against Islam to the south. Parish and monastery structure a crusading society in formation.",
        "ITA": "Latin Mass in the north/center, Greek liturgy in Byzantine zones, and Islamic prayer in the south — three ritual systems sharing markets and frontiers.",
        "POL": "Newly Latin Christian Piast realm: baptism of elites, church tithes, and saints’ cults. Pagan uprisings show conversion is still unfinished social work.",
        "RUS": "Orthodox Christianization spreads north from Kiev unevenly: liturgy, baptism, and icons in towns; rural pagan practice persists in forest zones.",
        "GRC": "Byzantine Orthodoxy as imperial ideology — liturgy, icons, and missionary baptism among Slavs. The emperor and patriarch frame sacred politics.",
        "BGR": "Slavic Orthodoxy with Bulgarian patriarchal memory: liturgy, monasticism, and autocephalous pride after conversion from Bulgar paganism.",
    },
    "high-medieval": {
        "SWE": "Latin Christian kingdom with Uppsala archbishopric: parish Mass, saints, and pilgrimage. Older pagan cult sites are remembered as the church plants a full diocesan map.",
        "DNK": "Latin Christian monarchy partnered with bishops: Mass, confession, crusading vows, and monastic houses structure belief and politics together.",
        "NOR": "Latin Christianity after civil wars of church and crown: parish system, pilgrimage to Nidaros, and royal sacral ideology.",
        "ISL": "Latin Christianity after the 1000 conversion: farmstead churches, quiet pagan residues in saga memory, and law tied to Christian public order.",
        "IRL": "Latin Christian Ireland under reforming bishops and English pressure: Mass, saints, and monastic learning; Gaelic church customs slowly standardized.",
        "DEU": "Catholic Holy Roman Empire: Mass, relics, and crusading emperors after Investiture conflicts. Monasteries and cathedral chapters are ritual and political engines.",
        "CZE": "Latin Christianity with dense monasteries: Mass, saints, and Premyslid sacral kingship. Bohemia becomes a rich liturgical landscape inside the Empire’s orbit.",
        "HUN": "Latin Christian realm with Orthodox and steppe minorities: coronation liturgy, dioceses, and border confessions sharing one kingdom.",
        "PRT": "Crusading Catholicism: Mass, military orders, and Reconquista ideology. Knighthood and monastic vow blur in frontier war.",
        "ITA": "Papal monarchy at full claim; Franciscan and Dominican preaching remakes urban piety. Communion, confession, and confraternities intensify lay ritual life.",
        "GRC": "Greek Orthodoxy under/against Latin occupation after 1204: Byzantine liturgy vs Frankish Latin rites — schism lived parish by parish.",
        "BGR": "Bulgarian Orthodoxy with episodic union politics toward Rome: Slavic liturgy, monasteries, and contested ecclesiastical loyalty.",
        "SRB": "Autocephalous Serbian Orthodoxy (Sava): national church, liturgy, and monastic centers binding dynasty to rite.",
        "TUR": "Greek Orthodoxy retreats as Turkish Islam advances in Anatolia — mosque and medrese replace many churches; conversion and coexistence both occur.",
        "RUS": "Orthodoxy under Mongol census: liturgy and monasteries continue while princes collect tribute. Sacred authority shifts with political centers.",
        "UKR": "Galicia–Volhynia Orthodoxy under Mongol pressure: episcopal continuity, monasticism, and princely patronage amid political fragmentation.",
        "CHE": "Latin Christian alpine communities: parish Mass, local saints, and communal vows. Mountain autonomy includes control of local church life.",
        "NLD": "Dense parish Latin Christianity: Mass, guild piety, and early urban mysticism. The Low Countries become a laboratory of lay devotion.",
    },
    "late-medieval": {
        "DNK": "Kalmar Catholic monarchies under Rome: Mass, saints, and royal church patronage across the union. Vernacular piety grows beside Latin liturgy.",
        "SWE": "Catholic Sweden with strong vernacular devotion: parish Mass, guilds, and saint cults under/against Kalmar politics.",
        "NOR": "Catholic Nidaros archbishopric remains prestigious: pilgrimage, Mass, and saintly kingship memory even as Kalmar politics weaken the realm.",
        "PRT": "Aviz crusading Catholicism pivots toward Africa: military orders, Mass, and missionary conquest ideology.",
        "ITA": "Catholic Italy in conciliar crisis: Mass, confraternities, preaching, and civic saint cults while popes and councils fight for authority.",
        "SRB": "Serbian Orthodoxy as identity under Ottoman pressure: liturgy, memory of empire, and monastic refuges.",
        "BGR": "Bulgarian Orthodoxy entering millet structures: liturgy under Islamic sovereignty; Islamization limited at first, church life constrained but continuous.",
        "HUN": "Catholic kingdom with Orthodox minorities: Latin liturgy at court, mixed border rites, and crusading ideology against Ottomans.",
        "NLD": "Burgundian Netherlands: intense parish Catholicism, processions, and guild chapels; underground reform currents before Luther.",
        "CHE": "Catholic Swiss communes: local saints, parish autonomy, and armed piety — religion as communal identity.",
        "AUT": "Habsburg Catholic dynastic piety: court liturgy, relics, and emerging dynastic sainthood politics.",
        "TUR": "Ottoman Sunni Islam as state religion: Friday prayer, sharia courts, and Sufi orders; Christian and Jewish dhimmi communities keep their own rites under restriction.",
    },
    "reformation": {
        "IRL": "Catholic majority under a newly claimed Protestant state church: Mass goes underground or contested; conformity laws reshape public ritual.",
        "ESP": "Tridentine Catholicism: reformed Mass, Inquisition discipline, and global missionary orders. Baroque piety and orthodoxy as imperial project.",
        "PRT": "Catholic empire with Jesuit and other orders as soft power: confession, missions, and Inquisition courts tying belief to overseas rule.",
        "CHE": "Reformed vs Catholic cantons: Zwinglian/Calvinist preaching, psalms, and disciplined consistories beside continuing Mass in Catholic valleys.",
        "DNK": "Lutheran Reformation after civil war: vernacular liturgy, married clergy, and crown control of the church; Catholic rite suppressed.",
        "NOR": "Lutheran reform from above via Denmark: new church order, vernacular services, and closure of Catholic monastic ritual life.",
        "LTU": "Commonwealth borderland of Catholicizing elites, Orthodox majorities in places, Protestant nobles, and Jewish towns — plural ritual under one republic.",
        "RUS": "Orthodox autocracy with rising Third Rome ideology: liturgy, tsar as sacred protector, and tight control of heresy and ritual dissent.",
        "BGR": "Orthodoxy under Ottoman rule with gradual Islamization in some regions: church tax, restricted building, and village feast continuity.",
        "SRB": "Southern Slavic Orthodoxy in millet structures: patriarchate politics, liturgy, and identity under Islamic sovereignty (Habsburg fringe differs).",
        "BEL": "Tridentine Catholic restoration under Spain: Baroque churches, Jesuit schooling, and suppressed Calvinism after revolt violence.",
    },
    "early-modern": {
        "ESP": "Baroque Catholicism: ornate Mass, confraternities, and an Inquisition still policing belief. Saints, processions, and imperial mission theology saturate public life.",
        "PRT": "Catholic empire with Inquisition and missionary orders: sacramental conformity at home, conversion projects abroad.",
        "NLD": "Public Calvinism (preaching, psalms, consistory discipline) with pragmatic urban tolerance — synagogues and Catholic house-churches in a carefully managed pluralism.",
        "AUT": "Catholic Reform and Jesuit baroque: renewed Mass, confession, pilgrimage, and education as Habsburg confessional statecraft.",
        "SWE": "Lutheran great-power church: state liturgy, catechism, and clerical loyalty to the crown; Catholic and Calvinist minorities tightly limited.",
        "DNK": "Lutheran monarchy: folk-church baptism, catechism, and parish discipline under royal supremacy.",
        "RUS": "Orthodox tsardom with patriarchate: liturgy and ritual uniformity, plus Uniate conflict on the western edge over rite and loyalty.",
        "TUR": "Sunni imperial Islam with millet continuities: mosque, sharia, Sufi brotherhoods; Christian and Jewish communities keep bounded ritual autonomy.",
        "ITA": "Baroque Catholicism and scientific trials (Galileo): ornate liturgy and confraternities beside tighter doctrinal policing after Trent.",
        "IRL": "Catholic population under Protestant state church claims: clandestine Mass, pilgrimage, and penal constraints shape ritual life.",
        "NOR": "Lutheran reform from above continues: vernacular liturgy and parish schooling under Danish church law.",
        "BEL": "Tridentine Catholic restoration: Baroque churches, processions, and confessional schooling after the revolt’s religious split.",
        "CHE": "Standing Reformed/Catholic cantonal split: sermon-centered worship vs Mass — a miniature confessional Europe in the Alps.",
    },
    "modern": {
        "FIN": "Lutheran majority church with strong secularization: baptism and church tax persist while belief privatizes; new minorities grow.",
        "SWE": "Lutheran heritage under deep secularization; church rites as culture more than compulsion, plus rising religious diversity.",
        "DNK": "Lutheran folk church under secularization: life-cycle rituals (baptism, confirmation, funeral) outlast weekly practice for many.",
        "NOR": "Lutheran heritage with rapid secularization; state–church untying and plural immigration reshape the ritual field.",
        "ESP": "Catholic culture under rapid secularization after Franco-era confessionalism; regional identities and new pluralism reframe practice.",
        "PRT": "Catholic culture under secularization: feast days and parish memory endure beside declining weekly Mass.",
        "ITA": "Catholic society beside the Vatican: parish and papal ritual still public, while secularization and immigration diversify belief.",
        "RUS": "Orthodox revival after Soviet atheism: rebuilt churches, public liturgy, and state-adjacent piety alongside Muslim, Buddhist, and secular populations.",
        "UKR": "Orthodox jurisdictions in flux plus Greek Catholic west: liturgy as identity under war and politics; pluralism and secular strata coexist.",
        "TUR": "Secular republic over a Muslim-majority society: contested laicism, mosque life, and political Islam debates redefine public ritual.",
        "GRC": "Greek Orthodoxy as cultural establishment: liturgy and feast calendar still mark public time while youth secularization rises.",
    },
}


def main() -> None:
    data = json.loads(PATH.read_text())
    added = 0
    expanded = 0
    kept = 0

    for period in data["periods"]:
        pid = period["id"]
        pols = period.get("polities") or {}
        for iso, polity in pols.items():
            if not isinstance(polity, dict):
                continue
            current = (polity.get("religion") or "").strip()
            replacement = None
            if pid in NEW and iso in NEW[pid]:
                replacement = NEW[pid][iso]
                source = "new"
            elif pid in EXPAND and iso in EXPAND[pid]:
                replacement = EXPAND[pid][iso]
                source = "expand"

            if not replacement:
                continue

            if not current:
                polity["religion"] = replacement
                added += 1
            elif len(current) < MIN_KEEP:
                polity["religion"] = replacement
                expanded += 1
            else:
                kept += 1

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Religion texts: added {added}, expanded {expanded}, kept rich {kept}.")


if __name__ == "__main__":
    main()
