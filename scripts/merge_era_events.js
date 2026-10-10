#!/usr/bin/env node
/**
 * Merge research JSON from era-events/ into data/key-events.json.
 * Does not invent events — only copies what research files provide.
 *
 * Usage:
 *   node scripts/merge_era_events.js \
 *     --in /cursor/stores/self/internal/era-events \
 *     --out data/key-events.json
 */
const fs = require("fs");
const path = require("path");

function arg(name, fallback) {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const inDir = path.resolve(
  arg("--in", "/cursor/stores/self/internal/era-events")
);
const outFile = path.resolve(arg("--out", path.join(__dirname, "../data/key-events.json")));

const PERIOD_IDS = new Set([
  "mesolithic",
  "early-neolithic",
  "middle-neolithic",
  "yamnaya",
  "beaker-corded",
  "nordic-bronze",
  "iron-age",
  "classical",
  "migration",
  "frankish",
  "vikings",
  "high-medieval",
  "late-medieval",
  "reformation",
  "early-modern",
  "modern",
]);

function normalizeEvent(e) {
  if (!e || typeof e !== "object") return null;
  const text = String(e.text || e.summary || e.event || "").trim();
  if (!text) return null;
  return {
    date: String(e.date || e.when || e.year || "").trim() || null,
    text,
    iso: e.iso ? String(e.iso).toUpperCase() : null,
    region: e.region || null,
  };
}

function normalizeElement(e) {
  if (!e || typeof e !== "object") return null;
  const text = String(e.text || e.note || e.detail || "").trim();
  const title = String(e.title || e.label || "").trim();
  if (!text && !title) return null;
  return {
    title: title || null,
    text: text || null,
    iso: e.iso ? String(e.iso).toUpperCase() : null,
  };
}

function normalizeSource(s) {
  if (!s || typeof s !== "object") return null;
  const title = String(s.title || s.name || "").trim();
  if (!title && !s.detail && !s.url) return null;
  return {
    title: title || null,
    detail: s.detail ? String(s.detail).trim() : null,
    url: s.url ? String(s.url).trim() : null,
  };
}

function loadOne(filePath) {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const base = path.basename(filePath, ".json");
  const periodId = String(raw.periodId || raw.id || base).trim();
  if (!PERIOD_IDS.has(periodId)) {
    console.warn(`skip ${filePath}: unknown periodId "${periodId}"`);
    return null;
  }
  const keyEvents = (raw.keyEvents || raw.events || [])
    .map(normalizeEvent)
    .filter(Boolean);
  const interestingElements = (raw.interestingElements || raw.elements || [])
    .map(normalizeElement)
    .filter(Boolean);
  const sources = (raw.sources || []).map(normalizeSource).filter(Boolean);
  if (!keyEvents.length && !interestingElements.length && !sources.length) {
    console.warn(`skip ${filePath}: no usable fields`);
    return null;
  }
  return {
    periodId,
    label: raw.label || null,
    keyEvents,
    interestingElements,
    sources,
  };
}

if (!fs.existsSync(inDir)) {
  console.error(`input dir missing: ${inDir}`);
  process.exit(1);
}

const files = fs
  .readdirSync(inDir)
  .filter((f) => f.endsWith(".json") && !f.startsWith("_"))
  .sort();

const periods = {};
let n = 0;
for (const f of files) {
  const packed = loadOne(path.join(inDir, f));
  if (!packed) continue;
  periods[packed.periodId] = packed;
  n += 1;
  console.log(
    `+ ${packed.periodId}: ${packed.keyEvents.length} events, ${packed.interestingElements.length} elements, ${packed.sources.length} sources`
  );
}

const out = {
  version: 1,
  updatedAt: new Date().toISOString(),
  periods,
};

fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, JSON.stringify(out, null, 2) + "\n");
console.log(`wrote ${outFile} (${n} periods)`);
