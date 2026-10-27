#!/usr/bin/env node
/**
 * Check the map-key region headings (CULTURE_FAMILY_RULES in js/app.js).
 *
 * Runs the live rules over every Deep-time map layer and every kingdom-tab
 * polity name (incl. nameByTick), then:
 *  - fails if any EXPECT entry below lands under the wrong heading;
 *  - fails if a Deep-time layer or kingdom polity gets no heading, unless it
 *    is listed in OTHER_OK (these show under "Other");
 *  - with --all, prints every assignment for review.
 *
 * Usage: node scripts/check_legend_families.js [--all]
 */
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");

const src = read("js/app.js");
const m = src.match(/const CULTURE_FAMILY_RULES = (\[[\s\S]*?\n\]);/);
if (!m) {
  console.error("CULTURE_FAMILY_RULES not found in js/app.js");
  process.exit(2);
}
const RULES = eval(m[1]); // eslint-disable-line no-eval
const family = (id, label) => {
  const t = `${id || ""} ${label || ""}`;
  for (const [name, re] of RULES) if (re.test(t)) return name;
  return "";
};

// Regression cases from the Oct 2026 content review.
const EXPECT = {
  "migration/brittonic": "Britain & Ireland",
  "frankish/croatia": "Balkans",
  "late-medieval/hungary-lm": "Central Europe",
  "early-modern/russia-em": "Slavic & Baltic",
  "eve-of-war/vojvodina-1914": "Central Europe",
  "eve-of-war/austria-hungary": "Western Europe",
  "modern:netherlands-united": "Western Europe",
  "early-modern:spanish-netherlands": "Western Europe",
  "early-modern:prussia": "Western Europe",
  "modern:russian-empire": "Slavic & Baltic",
  "high-medieval:florence": "Italy",
  "high-medieval:kalmar-union": "Nordic",
};
const OTHER_OK = new Set(["modern/caucasus", "high-medieval:crusader-states"]);

const rows = [];
const tl = JSON.parse(read("data/timeline.json"));
for (const p of tl.periods)
  for (const l of p.mapLayers || [])
    rows.push({ key: `${p.id}/${l.id}`, label: l.label, fam: family(l.id, l.label) });
for (const tab of ["high-medieval", "renaissance", "early-modern", "modern"]) {
  const d = JSON.parse(read(`data/kingdom-eras/${tab}.json`));
  for (const p of d.polities) {
    rows.push({ key: `${tab}:${p.id}`, label: p.name, fam: family(p.id, p.name) });
    for (const [yr, nm] of Object.entries(p.nameByTick || {}))
      rows.push({ key: `${tab}:${p.id}@${yr}`, label: nm, fam: family(p.id, nm) });
  }
}

let bad = 0;
const byKey = new Map(rows.map((r) => [r.key, r]));
for (const [k, want] of Object.entries(EXPECT)) {
  const r = byKey.get(k);
  if (!r) { console.log(`MISSING  ${k} (expected ${want})`); bad++; continue; }
  if (r.fam !== want) { console.log(`WRONG    ${k} "${r.label}" -> ${r.fam || "(none)"}, expected ${want}`); bad++; }
}
// Pre-farming Deep-time stops use archaeological culture names; those have
// their own forager/farmer rules, so unmatched there is reported, not failed.
const PREHISTORIC = /^(mesolithic|early-neolithic|middle-neolithic|yamnaya|beaker-corded|nordic-bronze|iron-age)\//;
for (const r of rows) {
  if (r.fam || OTHER_OK.has(r.key)) continue;
  const tag = PREHISTORIC.test(r.key) ? "note    " : "NOHEAD  ";
  if (tag.startsWith("NOHEAD")) bad++;
  console.log(`${tag} ${r.key} "${r.label}"`);
}
if (process.argv.includes("--all")) for (const r of rows) console.log(`${r.fam.padEnd(18)} ${r.key} "${r.label}"`);
console.log(`${rows.length} layers checked, ${bad} problem(s)`);
process.exit(bad ? 1 : 0);
