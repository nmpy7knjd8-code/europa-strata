#!/usr/bin/env node
/**
 * Wire precededBy / succeededBy on every polity by ISO across periods
 * (sorted by yearApprox). Also attach short aliases for auto-linking.
 *
 * Usage: node scripts/wire_polity_chains.js
 */
const fs = require("fs");
const path = require("path");

const file = path.join(__dirname, "..", "data", "timeline.json");
const data = JSON.parse(fs.readFileSync(file, "utf8"));

const byIso = new Map();
for (const period of data.periods) {
  const pols = period.polities || {};
  for (const [iso, pol] of Object.entries(pols)) {
    if (!byIso.has(iso)) byIso.set(iso, []);
    byIso.get(iso).push({ period, iso, pol });
  }
}

let chained = 0;
for (const [, entries] of byIso) {
  entries.sort(
    (a, b) => (a.period.yearApprox ?? 0) - (b.period.yearApprox ?? 0)
  );
  for (let i = 0; i < entries.length; i++) {
    const { period, iso, pol } = entries[i];
    const ref = (e) => ({
      periodId: e.period.id,
      iso: e.iso,
      name: e.pol.name,
    });
    if (i > 0) {
      pol.precededBy = ref(entries[i - 1]);
      chained++;
    } else {
      delete pol.precededBy;
    }
    if (i < entries.length - 1) {
      pol.succeededBy = ref(entries[i + 1]);
      chained++;
    } else {
      delete pol.succeededBy;
    }

    // Light aliases for prose linking (name stems + slash parts)
    const aliases = new Set();
    const name = pol.name || "";
    name.split(/\s*[/·|]\s*/).forEach((part) => {
      const p = part.trim();
      if (p.length >= 5) aliases.add(p);
    });
    // Strip trailing parentheticals / qualifiers for shorter match forms
    const bare = name
      .replace(/\s*\([^)]*\)\s*/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    if (bare.length >= 5 && bare !== name) aliases.add(bare);
    // Keep only aliases that aren't the full name
    const list = [...aliases].filter((a) => a !== name && a.length >= 5);
    if (list.length) pol.aliases = list.slice(0, 6);
    else delete pol.aliases;
  }
}

// A few high-value cross-ISO / cross-thread aliases used in blurbs
const EXTRA = [
  // name fragment → preferred target
  { alias: "Roman Empire", periodId: "classical", iso: "ITA" },
  { alias: "Roman Britain", periodId: "classical", iso: "GBR" },
  { alias: "Roman Gaul", periodId: "classical", iso: "FRA" },
  { alias: "Roman Hispania", periodId: "classical", iso: "ESP" },
  { alias: "Yamnaya", periodId: "yamnaya", iso: "UKR" },
  { alias: "Corded Ware", periodId: "beaker-corded", iso: "DEU" },
  { alias: "Bell Beaker", periodId: "beaker-corded", iso: "GBR" },
  { alias: "Ostrogothic", periodId: "migration", iso: "ITA" },
  { alias: "Visigothic", periodId: "migration", iso: "ESP" },
  { alias: "Carolingian", periodId: "frankish", iso: "FRA" },
  { alias: "Holy Roman Empire", periodId: "high-medieval", iso: "DEU" },
  { alias: "Kievan Rus", periodId: "vikings", iso: "UKR" },
  { alias: "Kievan Rus’", periodId: "vikings", iso: "UKR" },
  { alias: "Byzantine Empire", periodId: "vikings", iso: "GRC" },
  { alias: "Ottoman Empire", periodId: "early-modern", iso: "TUR" },
  { alias: "Al-Andalus", periodId: "frankish", iso: "ESP" },
  { alias: "Danelaw", periodId: "frankish", iso: "GBR" },
  { alias: "Normandy", periodId: "vikings", iso: "FRA" },
  { alias: "Plantagenet", periodId: "high-medieval", iso: "GBR" },
  { alias: "Capetian", periodId: "high-medieval", iso: "FRA" },
];

if (!data.meta) data.meta = {};
data.meta.linkAliases = EXTRA;

fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
console.log(
  `Wired ${chained} precede/succeed edges across ${byIso.size} ISOs; ${EXTRA.length} global aliases.`
);
