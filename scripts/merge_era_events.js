#!/usr/bin/env node
/**
 * Merge research JSON from era-events/ into data/key-events.json.
 * Accepts one period object OR an array of period objects per file.
 * Transforms richer research fields (year/title/summary/regions) into the app model.
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
const outFile = path.resolve(
  arg("--out", path.join(__dirname, "../data/key-events.json"))
);

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

const REGION_IDS = new Set([
  "iberia",
  "britain",
  "france",
  "central",
  "scandinavia",
  "italy",
  "balkans",
  "eastern",
]);

function asList(v) {
  if (!v) return [];
  return Array.isArray(v) ? v : [v];
}

function normalizeRegions(e) {
  const out = [];
  for (const r of asList(e.regions)) {
    const id = String(r || "").trim().toLowerCase();
    if (REGION_IDS.has(id)) out.push(id);
  }
  if (e.region) {
    const id = String(e.region).trim().toLowerCase();
    if (REGION_IDS.has(id) && !out.includes(id)) out.push(id);
  }
  return out;
}

function normalizeEvent(e) {
  if (!e || typeof e !== "object") return null;
  const title = String(e.title || "").trim();
  const summary = String(e.summary || "").trim();
  const plain = String(e.text || e.event || e.note || "").trim();
  const detail = String(e.detail || "").trim();
  const teaserIn = String(e.teaser || "").trim();
  // Prefer summary body; fall back to plain text field
  const text = summary || plain || detail;
  if (!text && !title) return null;
  const date = String(e.date || e.when || e.year || "").trim() || null;
  const regions = normalizeRegions(e);
  const themes = asList(e.themes)
    .map((t) => String(t || "").trim())
    .filter(Boolean);
  // Prefer enrich_key_events_detail.py for teaser/detail; pass through if present
  const teaser =
    teaserIn ||
    title ||
    (text.length > 140 ? text.slice(0, 137).trimEnd() + "…" : text);
  const full = detail || text || title;
  return {
    date,
    title: title || null,
    teaser,
    detail: full,
    text: full,
    iso: e.iso ? String(e.iso).toUpperCase() : null,
    region: regions[0] || null,
    regions,
    themes,
  };
}

function normalizeElement(e) {
  if (typeof e === "string") {
    const s = e.trim();
    if (!s) return null;
    return { title: s, text: null, iso: null };
  }
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
  if (typeof s === "string") {
    const t = s.trim();
    if (!t) return null;
    return { title: t, detail: null, url: null };
  }
  if (!s || typeof s !== "object") return null;
  const title = String(s.title || s.name || "").trim();
  if (!title && !s.detail && !s.url) return null;
  return {
    title: title || null,
    detail: s.detail ? String(s.detail).trim() : null,
    url: s.url ? String(s.url).trim() : null,
  };
}

function normalizePeriod(raw, fallbackId) {
  const periodId = String(raw.periodId || raw.id || fallbackId || "")
    .trim();
  if (!PERIOD_IDS.has(periodId)) {
    console.warn(`skip period: unknown periodId "${periodId}"`);
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
    console.warn(`skip ${periodId}: no usable fields`);
    return null;
  }
  return {
    periodId,
    label: raw.label || raw.periodLabel || null,
    approxYears: raw.approxYears || null,
    keyEvents,
    interestingElements,
    sources,
    sourceFile: raw.__sourceFile || null,
  };
}

function loadFile(filePath) {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const base = path.basename(filePath, ".json");
  const blocks = Array.isArray(raw) ? raw : [raw];
  return blocks.map((b) =>
    normalizePeriod({ ...b, __sourceFile: path.basename(filePath) }, base)
  );
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
  const packedList = loadFile(path.join(inDir, f));
  for (const packed of packedList) {
    if (!packed) continue;
    periods[packed.periodId] = packed;
    n += 1;
    console.log(
      `+ ${packed.periodId} ← ${f}: ${packed.keyEvents.length} events, ${packed.interestingElements.length} elements, ${packed.sources.length} sources`
    );
  }
}

const out = {
  version: 1,
  updatedAt: new Date().toISOString(),
  periods,
};

fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, JSON.stringify(out, null, 2) + "\n");
console.log(`wrote ${outFile} (${n} periods)`);
