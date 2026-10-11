#!/usr/bin/env python3
"""Author and inject per-tick narrative/title/eyebrow into kingdom era packs."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "data" / "kingdom-eras"
STORE = Path("/cursor/stores/self/internal/kingdom-enrichment/tick-blurbs")

# Each tick: name (serif title), era (eyebrow), narrative (body)
TICK_BLURBS = {
    "high-medieval": {
        1000: {
            "name": "Millennium kingdoms",
            "era": "Capetians, Ottonians, and the year-1000 map",
            "narrative": (
                "Around 1000, Latin Christendom is a mosaic of consolidating crowns and duchies: "
                "Capetian France still thin around Paris, Ottonian–Salian Germany and Italy under imperial claim, "
                "England after Æthelred, Christian Iberian north against al-Andalus, and Piast, Árpád, and "
                "Scandinavian realms entering the Latin church. Byzantium and Kievan Rus’ still define the east; "
                "schematic polities here mark that millennial patchwork, not modern borders."
            ),
        },
        1100: {
            "name": "After the First Crusade",
            "era": "Investiture, Normans, and Outremer",
            "narrative": (
                "By 1100 the Investiture Contest reshapes empire and papacy, Norman power binds England to "
                "the Continent, and crusader states cling to the Levantine coast. Iberian reconquest advances "
                "unevenly; Poland and Hungary deepen Latin kingship; the Commune movement stirs in Italy. "
                "This snapshot is post-crusade politics—holy war, reform popes, and feudal crowns in motion."
            ),
        },
        1200: {
            "name": "High Medieval climax",
            "era": "Philip Augustus, Innocent III, and Latins in Constantinople",
            "narrative": (
                "c. 1200 is Capetian ascent after Bouvines’ generation, papal monarchy under Innocent III, "
                "and the shock of the Fourth Crusade’s Latin Empire in Constantinople. Plantagenet cross-Channel "
                "lordship strains; Iberian crowns push south; Hohenstaufen Italy and the Reich remain contested. "
                "Read this tick as the classic ‘high’ Middle Ages of law, crusade, and royal consolidation."
            ),
        },
        1300: {
            "name": "Crisis and consolidation",
            "era": "Philip IV, Avignon’s eve, and eastern unions",
            "narrative": (
                "Around 1300, Philip IV’s France tests Boniface VIII; the Empire fragments after the "
                "Hohenstaufen; England and Scotland lock into wars of sovereignty. Aragon and Castile mature "
                "as Mediterranean and Meseta powers; Lithuania and Muscovy rise on the Orthodox–Latin frontier. "
                "The tick catches late Capetian/early Avignon pressures before the Black Death remakes demography."
            ),
        },
        1400: {
            "name": "Schism, plague aftershocks, and rivals",
            "era": "Hundred Years’ War, Timur, and Kalmar’s shadow",
            "narrative": (
                "c. 1400 Europe lives with papal schism, unfinished Hundred Years’ War, and Ottoman advance "
                "after Nicopolis. Timur’s blow to Bayezid resets Anatolia; Poland–Lithuania and Muscovy "
                "reorganize the east; Scandinavian union politics hover over Denmark–Norway–Sweden. "
                "This late medieval snapshot is war, schism, and recovering kingdoms—not a single Christendom."
            ),
        },
    },
    "renaissance": {
        1400: {
            "name": "Quattrocento threshold",
            "era": "Italian powers, Valois–Lancaster, and Ottoman rise",
            "narrative": (
                "At 1400 Italian republics and signorie already export humanism and mercenary war while "
                "Valois and Lancastrians bleed in France. The Ottomans press the Balkans; Iberian crowns "
                "prepare the final Nasrid reduction; Burgundy is a princely third force. This tick is "
                "late medieval politics with Renaissance culture beginning in Italian courts and communes."
            ),
        },
        1450: {
            "name": "Print, guns, and the fall of the City",
            "era": "1453 Constantinople and mid-century recovery",
            "narrative": (
                "Mid-century turns on Constantinople’s fall (1453), French recovery under Charles VII, "
                "and Burgundy’s glittering composite state. Italian powers balance before the French wars; "
                "print and artillery begin to alter information and sieges. The snapshot is post-plague "
                "recovery meeting Ottoman and Valois ambition."
            ),
        },
        1500: {
            "name": "Age of discoveries & Italian Wars",
            "era": "Charles VIII’s trail, Habsburg marriages, Atlantic turn",
            "narrative": (
                "Around 1500 French armies open the Italian Wars, Spain unites under the Catholic Monarchs’ "
                "heirs, and Portuguese routes already pull Asia into European politics. Maximilian’s Habsburg "
                "web and Tudor consolidation frame the north. Culture is High Renaissance in Italy while "
                "dynastic war makes the peninsula Europe’s battlefield."
            ),
        },
        1550: {
            "name": "Confessions harden",
            "era": "Augsburg, Trent, and Habsburg–Valois deadlock",
            "narrative": (
                "By 1550 Lutheran settlement (Augsburg 1555 approaches), the Council of Trent has begun, "
                "and Charles V’s stretched empire faces Valois France and Ottoman pressure. England under "
                "Edward/Mary oscillates confessionally; Scandinavia is Lutheran; Muscovy under Ivan IV "
                "pushes east. This tick is Reformation politics—faith as border—before the Dutch Revolt ignites."
            ),
        },
        1600: {
            "name": "Century’s turn",
            "era": "Dutch Revolt, Philip III, and northern wars",
            "narrative": (
                "c. 1600 the Dutch Republic fights for recognition, Spain under Philip III manages a global "
                "but strained monarchy, and France exits Wars of Religion toward Henri IV’s settlement. "
                "Sweden and Poland contest the Baltic; England is late Elizabethan/early Stuart. "
                "Renaissance culture shades into confessional Baroque politics."
            ),
        },
    },
    "early-modern": {
        1600: {
            "name": "Confessional Europe",
            "era": "Dutch Revolt, Henri IV, and the road to 1618",
            "narrative": (
                "In 1600 the Eighty Years’ War still defines the Low Countries, France consolidates after "
                "the Wars of Religion, and the Holy Roman Empire’s confessional truce grows brittle. "
                "Spain’s global monarchy, English and Dutch maritime challenge, and Polish–Swedish Baltic "
                "rivalry set the board. This snapshot is late Renaissance politics tipping into the "
                "Thirty Years’ War generation—not a generic ‘early modern’ blur."
            ),
        },
        1648: {
            "name": "Westphalia",
            "era": "Peace of Westphalia and the mid-century settlement",
            "narrative": (
                "1648 ends the Thirty Years’ War and (with Münster) the Dutch–Spanish conflict: sovereignty "
                "language, French and Swedish gains, and a shattered German landscape. England is in civil war "
                "and republic; Portugal has broken from Spain; Ukraine’s Khmelnytsky uprising remakes the east. "
                "Read this tick as the Westphalian settlement moment—war’s diplomatic aftershock."
            ),
        },
        1700: {
            "name": "Succession crises",
            "era": "Spain’s vacant throne and northern catastrophe",
            "narrative": (
                "Around 1700 the Spanish succession crisis draws Bourbon and Habsburg coalitions into "
                "continent-wide war, while Sweden’s Charles XII and Russia’s Peter collide in the Great "
                "Northern War. Louis XIV’s France is still the measuring stick of power; the Dutch and "
                "English are fiscal-military innovators. This is dynastic endgame politics, not 1600’s "
                "confessional map."
            ),
        },
        1750: {
            "name": "Enlightenment states",
            "era": "Diplomatic Revolution’s eve and colonial rivalry",
            "narrative": (
                "By 1750 Prussia under Frederick II and Austria under Maria Theresa redefine German power; "
                "Britain and France duel in Atlantic and Indian theatres; Russia is a European great power. "
                "Partition talk already shadows Poland; Enlightenment courts patronize science and reform "
                "rhetoric. The snapshot is mid-century cabinet war and colonial rivalry before 1756 realigns alliances."
            ),
        },
        1789: {
            "name": "Revolutionary threshold",
            "era": "French Revolution opens; old regimes wobble",
            "narrative": (
                "1789 cracks the French monarchy and forces every court to answer revolution, debt, and "
                "national claim. Poland’s reform moment races partition; Britain consolidates imperial gains "
                "after 1763; the Ottoman and Russian frontiers keep shifting. This tick is the hinge out of "
                "cabinet-era early modernity into revolutionary and Napoleonic remaking."
            ),
        },
    },
    "modern": {
        1815: {
            "name": "Vienna settlement",
            "era": "Congress of Vienna and post-Napoleonic order",
            "narrative": (
                "1815 restores and redesigns Europe after Napoleon: legitimacy, buffer states, and great-power "
                "concert under Metternich’s generation. Prussia and Austria share German leadership; Britain "
                "underwrites balance; Russia polices the east. Liberal and national movements are contained, "
                "not erased—this snapshot is restoration geopolitics."
            ),
        },
        1871: {
            "name": "Nation-states ascend",
            "era": "German and Italian unification; new empires",
            "narrative": (
                "1871 proclaims the German Empire at Versailles and seals Italian unification’s core. "
                "France is a humbled republic; Austria-Hungary is Dualist; the Balkans destabilize Ottoman "
                "retreat. Industrial and colonial competition accelerate. The tick is the unified-nation map "
                "that will march toward 1914."
            ),
        },
        1914: {
            "name": "July Crisis",
            "era": "Great War begins; imperial Europe armed",
            "narrative": (
                "1914 opens with alliance war among German, Austro-Hungarian, Russian, French, and British "
                "empires; Ottoman and later American entry globalize the conflict. Railway mobilization and "
                "industrial killing define the year. This snapshot is Europe’s imperial order at the moment "
                "it chooses general war."
            ),
        },
        1945: {
            "name": "Zero hour",
            "era": "Third Reich defeated; bipolar occupation",
            "narrative": (
                "1945 ends Nazi Germany and fragments the continent into occupation zones, displaced persons, "
                "and Soviet advance in the east. Colonial empires begin to unwind; nuclear weapons and UN "
                "institutions appear. The tick is ruin and partition—Cold War borders not yet fully frozen."
            ),
        },
        1990: {
            "name": "After the Wall",
            "era": "German reunification and Soviet collapse’s eve",
            "narrative": (
                "1990 reunifies Germany and signals Warsaw Pact dissolution; free elections remake Central "
                "Europe while Yugoslavia frays. The Soviet Union still exists but sovereignty cascades in "
                "the Baltics and republics. This snapshot is post-1989 transition—markets, NATO/EU aspiration, "
                "and unfinished borders."
            ),
        },
        2000: {
            "name": "Millennial Europe",
            "era": "EU enlargement eve; post-Cold War normal?",
            "narrative": (
                "Around 2000 the EU prepares eastern enlargement, the euro launches, and NATO’s post-Cold War "
                "map looks settled—until later shocks. Russia under Putin consolidates; Balkans remain after "
                "the Yugoslav wars; digital and migration politics rise. The tick is millennial European "
                "integration confidence before the twenty-first century’s reversals."
            ),
        },
    },
}


def apply_era(era: str) -> dict:
    path = SITE / f"{era}.json"
    pack = json.loads(path.read_text(encoding="utf-8"))
    blurbs = TICK_BLURBS[era]
    ticks = pack.get("ticks") or []
    updated = 0
    for tick in ticks:
        year = tick.get("year")
        b = blurbs.get(year)
        if not b:
            continue
        tick["name"] = b["name"]
        tick["era"] = b["era"]
        tick["narrative"] = b["narrative"]
        updated += 1
    path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"era": era, "ticks": len(ticks), "updated": updated}


def main():
    STORE.mkdir(parents=True, exist_ok=True)
    report = {"eras": []}
    for era in TICK_BLURBS:
        stats = apply_era(era)
        report["eras"].append(stats)
        print(json.dumps(stats))
    # Export authored blurbs for the store
    export = {
        "version": 1,
        "note": "Per-tick kingdom era panel titles/eyebrows/narratives",
        "eras": TICK_BLURBS,
    }
    (STORE / "kingdom-tick-blurbs.json").write_text(
        json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (STORE / "README.md").write_text(
        "# Kingdom tick blurbs\n\n"
        "Per-slider-tick `name` / `era` / `narrative` for High Medieval → Modern.\n"
        "Applied into `data/kingdom-eras/*.json` ticks; consumed by `normalizeKingdomPack`.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
