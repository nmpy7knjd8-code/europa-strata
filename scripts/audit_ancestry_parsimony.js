#!/usr/bin/env node
/**
 * Parsimony pass on regional ancestry mixes:
 * - WSH (steppe) already ≈ EHG+CHG — don't double-count
 * - Keep separate EHG/CHG only pre-Yamnaya or as labeled excess
 */
const fs = require("fs");
const path = require("path");

const file = path.join(__dirname, "..", "data", "timeline.json");
const data = JSON.parse(fs.readFileSync(file, "utf8"));

function cleanMap(a, { periodId, allowSeparateEhgChg }) {
  if (!a || typeof a !== "object") return a;
  const out = { ...a };
  const steppe = Number(out.steppe) || 0;
  const ehg = Number(out.ehg) || 0;
  const chg = Number(out.chg) || 0;

  if (steppe > 0 && (ehg > 0 || chg > 0)) {
    if (allowSeparateEhgChg && steppe < 20) {
      // Pre-/forming WSH: prefer EHG+CHG, drop tiny steppe slice
      out.ehg = ehg + Math.round(steppe * 0.55);
      out.chg = chg + Math.round(steppe * 0.45);
      delete out.steppe;
    } else {
      // Balanced WSH package: fold EHG/CHG into WSH
      out.steppe = steppe + ehg + chg;
      delete out.ehg;
      delete out.chg;
    }
  }

  // Drop dust buckets (< 3%) into nearest major component
  for (const [k, v] of Object.entries(out)) {
    if (k === "other") continue;
    if (Number(v) > 0 && Number(v) < 3) {
      if (k === "ehg" && (out.shg || out.whg || out.steppe)) {
        const target = out.shg != null ? "shg" : out.steppe != null ? "steppe" : "whg";
        out[target] = (Number(out[target]) || 0) + Number(v);
        delete out[k];
      } else if (k === "chg" && out.steppe != null) {
        out.steppe = (Number(out.steppe) || 0) + Number(v);
        delete out[k];
      }
    }
  }

  // Renormalize to ~100
  const keys = Object.keys(out).filter((k) => Number(out[k]) > 0);
  const sum = keys.reduce((s, k) => s + Number(out[k]), 0);
  if (sum > 0 && Math.abs(sum - 100) > 1) {
    const scale = 100 / sum;
    for (const k of keys) out[k] = Math.round(Number(out[k]) * scale);
    // fix rounding drift
    const sum2 = keys.reduce((s, k) => s + out[k], 0);
    const drift = 100 - sum2;
    if (drift !== 0) {
      const main = keys.sort((a, b) => out[b] - out[a])[0];
      out[main] += drift;
    }
  }

  // Remove zeros
  for (const k of Object.keys(out)) {
    if (!Number(out[k])) delete out[k];
  }
  return out;
}

function cleanRange(range, cleanedAncestry) {
  if (!range) return range;
  const out = { ...range };
  for (const k of Object.keys(out)) {
    if (!cleanedAncestry[k]) delete out[k];
  }
  return Object.keys(out).length ? out : undefined;
}

const PRE_WSH = new Set(["mesolithic", "early-neolithic", "middle-neolithic"]);
let n = 0;

for (const p of data.periods) {
  const allowSeparate = PRE_WSH.has(p.id);
  for (const r of Object.values(p.regions || {})) {
    const before = JSON.stringify(r.ancestry);
    r.ancestry = cleanMap(r.ancestry, { periodId: p.id, allowSeparateEhgChg: allowSeparate });
    if (JSON.stringify(r.ancestry) !== before) n++;

    if (r.ancestryRange) {
      r.ancestryRange = cleanRange(r.ancestryRange, r.ancestry);
      if (!r.ancestryRange) delete r.ancestryRange;
    }

    if (r.ancestryCline?.ends) {
      r.ancestryCline.ends = r.ancestryCline.ends.map((end) => ({
        ...end,
        ancestry: cleanMap(end.ancestry, {
          periodId: p.id,
          allowSeparateEhgChg: allowSeparate,
        }),
      }));
      // Notes for post-WSH contexts that had been double-counting
      if (!allowSeparate && /ehg|chg/i.test(r.ancestryNote || "")) {
        r.ancestryNote = (r.ancestryNote || "")
          .replace(/EHG\/?CHG[^.]*\./gi, "")
          .replace(/\s+/g, " ")
          .trim();
      }
    }
  }
}

// Explicit literature-shaped fixes for eastern Europe
function setRegion(periodId, rid, patch) {
  const p = data.periods.find((x) => x.id === periodId);
  const r = p?.regions?.[rid];
  if (!r) return;
  Object.assign(r, patch);
}

setRegion("early-neolithic", "eastern", {
  ancestry: { ehg: 58, eef: 20, whg: 12, chg: 10 },
  ancestryRange: { ehg: [45, 70], eef: [10, 35] },
  ancestryNote:
    "Pre-Yamnaya: EHG + CHG-related kept separate (not yet fused as WSH). Farmer fringe only on the southwest edge.",
  ancestryCline: {
    label: "Forest-steppe HG → farmer fringe",
    note: "EHG (+ some CHG-related) east of the Neolithic divide; EEF rises on Bug–Dniester contact — not WSH yet.",
    ends: [
      { id: "hg", label: "Forest-steppe EHG", ancestry: { ehg: 78, whg: 10, chg: 8, eef: 4 } },
      { id: "fringe", label: "Farmer fringe", ancestry: { eef: 42, ehg: 32, whg: 14, chg: 12 } },
    ],
  },
});

setRegion("middle-neolithic", "eastern", {
  ancestry: { eef: 44, ehg: 28, chg: 16, whg: 12 },
  ancestryRange: { eef: [30, 55], ehg: [18, 40] },
  ancestryNote:
    "Pre-Yamnaya Pontic: EHG + CHG-related as separate ingredients beside Trypillia EEF — forming steppe package, not scored as WSH yet.",
  ancestryCline: {
    label: "Trypillia farms → Pontic steppe edge",
    note: "EEF higher in Trypillia; EHG/CHG-related rise toward Usatove / Serednii Stih (pre-WSH fusion).",
    ends: [
      { id: "tryp", label: "Trypillia core", ancestry: { eef: 60, whg: 14, ehg: 16, chg: 10 } },
      { id: "pontic", label: "Pontic edge", ancestry: { ehg: 40, chg: 24, eef: 28, whg: 8 } },
    ],
  },
});

setRegion("yamnaya", "eastern", {
  ancestry: { steppe: 78, eef: 14, whg: 8 },
  ancestryRange: { steppe: [55, 90], eef: [5, 25] },
  ancestryNote:
    "Yamnaya = WSH package (EHG+CHG already fused). Shown as WSH, not re-split into EHG and CHG.",
  ancestryCline: {
    label: "Yamnaya core → farmer edge",
    note: "WSH% highest on Yamnaya core steppe; EEF rises toward late Trypillia / western contact.",
    ends: [
      { id: "core", label: "Yamnaya core", ancestry: { steppe: 90, eef: 6, whg: 4 } },
      { id: "edge", label: "Farmer / west edge", ancestry: { steppe: 48, eef: 38, whg: 14 } },
    ],
  },
});

setRegion("beaker-corded", "eastern", {
  ancestry: { steppe: 72, eef: 18, whg: 10 },
  ancestryRange: { steppe: [55, 85], eef: [10, 30] },
  ancestryNote:
    "Catacomb / steppe-contact as WSH package + farmer remainder — no separate EHG/CHG slices.",
  ancestryCline: {
    label: "Steppe/Catacomb → western contact",
    note: "WSH highest on Catacomb/steppe; EEF rises toward western Corded Ware contact.",
    ends: [
      { id: "steppe", label: "Catacomb / steppe", ancestry: { steppe: 85, eef: 8, whg: 7 } },
      { id: "west", label: "Western contact", ancestry: { steppe: 55, eef: 32, whg: 13 } },
    ],
  },
});

setRegion("early-neolithic", "scandinavia", {
  ancestry: { shg: 55, eef: 32, whg: 13 },
  ancestryRange: { shg: [40, 75], eef: [15, 45] },
  ancestryNote:
    "Ertebølle holdout still strong; earliest TRB farmers only beginning the first Holocene turnover.",
});

fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
console.log(`Parsimony cleanup touched ${n} region ancestry maps (+ explicit eastern fixes).`);
