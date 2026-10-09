#!/usr/bin/env node
/**
 * Add HG holdout layers + within-culture ancestry clines for key periods.
 */
const fs = require("fs");
const path = require("path");

const file = path.join(__dirname, "..", "data", "timeline.json");
const data = JSON.parse(fs.readFileSync(file, "utf8"));

function period(id) {
  const p = data.periods.find((x) => x.id === id);
  if (!p) throw new Error(`missing period ${id}`);
  return p;
}

function upsertLayer(p, layer) {
  if (!p.mapLayers) p.mapLayers = [];
  const i = p.mapLayers.findIndex((l) => l.id === layer.id);
  if (i >= 0) p.mapLayers[i] = { ...p.mapLayers[i], ...layer };
  else p.mapLayers.push(layer);
}

function patchRegion(p, rid, patch) {
  const r = p.regions[rid];
  if (!r) return;
  Object.assign(r, patch);
  if (patch.ancestry) r.ancestry = { ...r.ancestry, ...patch.ancestry };
}

/* ——— Early Neolithic ——— */
{
  const p = period("early-neolithic");
  upsertLayer(p, {
    id: "ertebolle",
    label: "Ertebølle foragers (HG holdout)",
    role: "substrate",
    color: "#4a6a68",
    opacity: 0.7,
    countries: ["DNK", "DEU", "SWE"],
  });
  upsertLayer(p, {
    id: "narva-comb",
    label: "Narva / Comb Ware foragers",
    role: "substrate",
    color: "#3f5f6a",
    opacity: 0.68,
    countries: ["EST", "LVA", "LTU", "FIN", "BLR"],
  });
  upsertLayer(p, {
    id: "ehg-persist",
    label: "EHG forest-steppe persistence",
    role: "substrate",
    color: "#5a7a9a",
    opacity: 0.65,
    countries: ["RUS", "UKR", "BLR", "LTU", "LVA", "EST"],
  });
  p.narrative =
    "Farming spreads demically along Cardial/Impresso coasts and the LBK Danube corridor. Hunter-gatherer holdouts remain: Ertebølle in southern Scandinavia/south Baltic, Narva–Comb Ware in the east Baltic, and EHG forest-steppe groups east of the farmer line. Early farmer Europe is already clinal — WHG share higher toward Atlantic and northern contact zones than in LBK cores.";
  p.culturesNote =
    "Cardial, Impresso, LBK, Starčevo–Vinča + HG holdouts (Ertebølle, Narva/Comb Ware, EHG persistence).";

  patchRegion(p, "britain", {
    ancestry: { eef: 78, whg: 20, steppe: 0 },
    ancestryRange: { eef: [70, 88], whg: [10, 28] },
    ancestryNote: "Earliest farming Britain: EEF-led; WHG higher at Atlantic edges than in pioneer cores.",
    ancestryCline: {
      label: "Core pioneer → Atlantic edge",
      note: "WHG% higher where farmers meet residual foragers; EEF highest in early pioneer packages.",
      ends: [
        { id: "core", label: "Pioneer core", ancestry: { eef: 88, whg: 10, steppe: 0 } },
        { id: "edge", label: "Atlantic edge", ancestry: { eef: 70, whg: 28, steppe: 0 } },
      ],
    },
  });
  patchRegion(p, "central", {
    ancestry: { eef: 90, whg: 8, steppe: 0 },
    ancestryRange: { eef: [85, 95], whg: [3, 14] },
    ancestryNote: "Early LBK cores often >85% EEF; WHG rises later in Mid–Late Neolithic.",
    ancestryCline: {
      label: "LBK core → northern contact",
      note: "WHG higher toward northern/forest contact; EEF highest in loess LBK heartland.",
      ends: [
        { id: "core", label: "LBK loess core", ancestry: { eef: 94, whg: 5, steppe: 0 } },
        { id: "north", label: "Northern contact", ancestry: { eef: 82, whg: 16, steppe: 0 } },
      ],
    },
  });
  patchRegion(p, "scandinavia", {
    ancestry: { shg: 55, eef: 30, whg: 12, ehg: 3, steppe: 0 },
    ancestryRange: { shg: [40, 75], eef: [15, 45] },
    ancestryNote: "Ertebølle holdout still strong; earliest TRB farmers only beginning the first Holocene turnover.",
    ancestryCline: {
      label: "Forager coast → earliest TRB farms",
      note: "SHG/WHG dominate Ertebølle coasts; EEF rises where earliest Funnelbeaker farming sticks.",
      ends: [
        { id: "hg", label: "Ertebølle coasts", ancestry: { shg: 70, whg: 18, eef: 10, steppe: 0 } },
        { id: "farm", label: "Earliest TRB farms", ancestry: { eef: 55, shg: 25, whg: 18, steppe: 0 } },
      ],
    },
    description:
      "Ertebølle foragers remain the demographic majority along Danish and south Swedish coasts while earliest Funnelbeaker farming appears in the south. Genetics: SHG/WHG holdouts beside rising EEF — the first Holocene turnover is beginning, not finished.",
  });
  patchRegion(p, "eastern", {
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
}

/* ——— Middle Neolithic / TRB ——— */
{
  const p = period("middle-neolithic");
  upsertLayer(p, {
    id: "pitted-ware",
    label: "Pitted Ware foragers (HG holdout)",
    role: "substrate",
    color: "#4a6a62",
    opacity: 0.72,
    countries: ["SWE", "DNK", "NOR"],
  });
  upsertLayer(p, {
    id: "narva-comb-mn",
    label: "Narva / Comb Ware foragers",
    role: "substrate",
    color: "#3f5f6a",
    opacity: 0.7,
    countries: ["EST", "LVA", "LTU", "FIN"],
  });
  upsertLayer(p, {
    id: "trb",
    label: "Funnelbeaker (TRB)",
    role: "dominant",
    color: "#b89038",
    countries: ["DEU", "POL", "DNK", "SWE", "NLD", "CZE"],
  });
  p.narrative =
    "Farmer Europe densifies: Atlantic megaliths, Chasséen/Michelsberg, Funnelbeaker (TRB), Cucuteni–Trypillia, early Globular Amphora. Hunter-gatherer holdouts persist beside farmers — Pitted Ware on Scandinavian coasts, Narva–Comb Ware in the east Baltic. Within TRB and other farmer packages, WHG% is clinal: higher north and west, lower in southern/central agricultural cores.";
  p.culturesNote =
    "TRB, Michelsberg, Chasséen, megalithic Atlantic, GAC, Trypillia + HG holdouts (Pitted Ware, Narva/Comb Ware).";

  patchRegion(p, "iberia", {
    ancestry: { eef: 68, whg: 30, steppe: 0 },
    ancestryRange: { eef: [60, 78], whg: [20, 38] },
    ancestryNote: "EEF majority; WHG higher on Atlantic megalithic façades than in southern inland cores.",
    ancestryCline: {
      label: "Atlantic façade → inland south",
      note: "WHG% rises toward Atlantic megalithic zones; EEF higher inland/south.",
      ends: [
        { id: "atlantic", label: "Atlantic megalithic", ancestry: { eef: 60, whg: 38, steppe: 0 } },
        { id: "inland", label: "Inland / south", ancestry: { eef: 78, whg: 20, steppe: 0 } },
      ],
    },
    description:
      "Passage graves and related monuments along Atlantic and southern Iberia. Still EEF-dominated, but WHG is higher on the Atlantic façade than in inland cores — a within-culture farmer cline, not a uniform Neolithic mix. Steppe still ~0.",
  });
  patchRegion(p, "britain", {
    ancestry: { eef: 72, whg: 26, steppe: 0 },
    ancestryRange: { eef: [65, 82], whg: [16, 34] },
    ancestryNote: "Neolithic Britain without steppe; WHG higher in north/west monument zones than in denser southern farming.",
    ancestryCline: {
      label: "North/west → southern farming",
      note: "WHG% higher in northern/western Neolithic landscapes; EEF higher in denser southern farming.",
      ends: [
        { id: "nw", label: "North / west", ancestry: { eef: 64, whg: 34, steppe: 0 } },
        { id: "se", label: "Southern farming", ancestry: { eef: 82, whg: 16, steppe: 0 } },
      ],
    },
    description:
      "Orkney, Wessex, and related Neolithic monument societies. Genomically Anatolian farmer–related + WHG, with a north/west vs south cline in WHG share — not one uniform Neolithic percentage across Britain. This is the gene pool later replaced in the Beaker age.",
  });
  patchRegion(p, "france", {
    ancestry: { eef: 70, whg: 28, steppe: 0 },
    ancestryRange: { eef: [62, 80], whg: [18, 36] },
    ancestryNote: "EEF majority + WHG; WHG higher on Atlantic megalithic west than in eastern Chasséen cores.",
    ancestryCline: {
      label: "Atlantic west → eastern Chasséen",
      note: "WHG% higher on the megalithic Atlantic façade; EEF higher in eastern Chasséen farming.",
      ends: [
        { id: "west", label: "Atlantic west", ancestry: { eef: 62, whg: 36, steppe: 0 } },
        { id: "east", label: "Eastern Chasséen", ancestry: { eef: 80, whg: 18, steppe: 0 } },
      ],
    },
  });
  patchRegion(p, "central", {
    ancestry: { eef: 72, whg: 26, steppe: 0 },
    ancestryRange: { eef: [60, 85], whg: [12, 38] },
    ancestryNote: "TRB/Michelsberg farmers: WHG higher in northern TRB; EEF higher in southern/central agricultural cores. GAC forms as the farmer side later mixed into Corded Ware.",
    ancestryCline: {
      label: "Northern TRB → central/south core",
      note: "WHG% rises north (and toward forager contact); EEF highest in Michelsberg / southern TRB cores.",
      ends: [
        { id: "north", label: "Northern TRB", ancestry: { eef: 58, whg: 38, steppe: 0 } },
        { id: "core", label: "Central / south core", ancestry: { eef: 84, whg: 14, steppe: 0 } },
      ],
    },
    description:
      "Funnelbeaker and Michelsberg farming societies; Globular Amphora forms toward the Late Neolithic. TRB is not genetically uniform — WHG ancestry is higher in northern TRB and lower in southern/central cores. Still pre-steppe.",
  });
  patchRegion(p, "scandinavia", {
    ancestry: { eef: 55, shg: 22, whg: 20, steppe: 0 },
    ancestryRange: { eef: [35, 75], shg: [8, 40], whg: [10, 30] },
    ancestryNote: "TRB farmers inland/south vs Pitted Ware forager holdouts on coasts — two genetic regimes under one map period.",
    ancestryCline: {
      label: "Pitted Ware coasts → TRB farms",
      note: "Coastal Pitted Ware keeps high SHG/WHG; southern/inland TRB is EEF-led with residual HG.",
      ends: [
        {
          id: "pitted",
          label: "Pitted Ware coasts",
          ancestry: { shg: 45, whg: 30, eef: 25, steppe: 0 },
        },
        {
          id: "trb",
          label: "TRB farming south",
          ancestry: { eef: 75, whg: 14, shg: 10, steppe: 0 },
        },
      ],
    },
    description:
      "Southern Scandinavia hosts both Funnelbeaker farmers and Pitted Ware coastal foragers. Genetics split with that geography: EEF-led TRB inland/south vs SHG/WHG-rich Pitted Ware holdouts on the coasts — not a single Scandinavian Neolithic mix.",
  });
  patchRegion(p, "eastern", {
    ancestry: { eef: 42, ehg: 28, chg: 14, whg: 10, steppe: 6 },
    ancestryRange: { eef: [30, 55], ehg: [18, 40] },
    ancestryNote: "Trypillia farmer cores vs Pontic Eneolithic steppe-adjacent groups — clinal before Yamnaya.",
    ancestryCline: {
      label: "Trypillia farms → Pontic steppe edge",
      note: "EEF higher in Trypillia; EHG/CHG-related rise toward Usatove / Serednii Stih contact.",
      ends: [
        { id: "tryp", label: "Trypillia core", ancestry: { eef: 58, whg: 14, ehg: 16, chg: 8, steppe: 4 } },
        { id: "pontic", label: "Pontic edge", ancestry: { eef: 28, ehg: 38, chg: 20, whg: 6, steppe: 8 } },
      ],
    },
  });
}

/* ——— Yamnaya horizon ——— */
{
  const p = period("yamnaya");
  upsertLayer(p, {
    id: "pitted-ware2",
    label: "Pitted Ware foragers (HG holdout)",
    role: "substrate",
    color: "#4a6a62",
    opacity: 0.7,
    countries: ["SWE", "DNK"],
  });
  upsertLayer(p, {
    id: "narva-late",
    label: "Late Narva / Comb Ware foragers",
    role: "substrate",
    color: "#3f5f6a",
    opacity: 0.65,
    countries: ["EST", "LVA", "LTU", "FIN"],
  });
  p.narrative =
    "Yamnaya pastoralists expand on the Pontic–Caspian steppe while Late Neolithic farmer Europe (TRB, GAC, Iberian Copper Age, British Late Neolithic) continues west of the steppe. Scandinavian/Baltic forager holdouts (Pitted Ware, late Narva–Comb) still mark the map. Steppe ancestry is high on the core steppe and falls off west/north — a gradient, not an instant uniform coat.";

  patchRegion(p, "eastern", {
    ancestry: { steppe: 55, ehg: 15, chg: 12, eef: 12, whg: 6 },
    ancestryRange: { steppe: [35, 80], eef: [5, 25] },
    ancestryNote: "Yamnaya core high steppe; farmer/Trypillia edges keep more EEF.",
    ancestryCline: {
      label: "Yamnaya core → farmer edge",
      note: "Steppe% highest on Yamnaya core steppe; EEF rises toward late Trypillia / western contact.",
      ends: [
        { id: "core", label: "Yamnaya core", ancestry: { steppe: 78, ehg: 8, chg: 10, eef: 3, whg: 1 } },
        { id: "edge", label: "Farmer / west edge", ancestry: { steppe: 35, eef: 35, ehg: 15, chg: 10, whg: 5 } },
      ],
    },
  });
  patchRegion(p, "central", {
    ancestry: { eef: 52, whg: 18, steppe: 30 },
    ancestryRange: { steppe: [15, 45], eef: [40, 65] },
    ancestryNote: "Late TRB/GAC still farmer-led; early steppe signals uneven — higher toward the east.",
    ancestryCline: {
      label: "West GAC/TRB → eastern contact",
      note: "Steppe% rises east toward Pontic contact; western Late Neolithic stays more EEF+WHG.",
      ends: [
        { id: "west", label: "West Late Neo", ancestry: { eef: 65, whg: 22, steppe: 13 } },
        { id: "east", label: "Eastern contact", ancestry: { eef: 40, whg: 14, steppe: 46 } },
      ],
    },
  });
  patchRegion(p, "scandinavia", {
    ancestry: { eef: 50, whg: 28, shg: 14, steppe: 8 },
    ancestryRange: { eef: [30, 70], steppe: [0, 20] },
    ancestryNote: "Mostly pre–Single Grave; Pitted Ware coasts keep HG-rich profiles beside TRB farms.",
    ancestryCline: {
      label: "Pitted Ware → late TRB",
      note: "Coastal holdouts stay HG-rich; southern TRB is EEF-led with only slight early steppe.",
      ends: [
        { id: "pw", label: "Pitted Ware", ancestry: { shg: 40, whg: 30, eef: 28, steppe: 2 } },
        { id: "trb", label: "Late TRB south", ancestry: { eef: 68, whg: 20, shg: 6, steppe: 6 } },
      ],
    },
  });
  patchRegion(p, "britain", {
    ancestry: { eef: 72, whg: 26, steppe: 2 },
    ancestryRange: { eef: [65, 80], whg: [18, 32] },
    ancestryNote: "Still Neolithic Britain — steppe negligible until Beaker.",
    ancestryCline: {
      label: "North/west → south",
      note: "Residual WHG cline within Late Neolithic Britain; steppe still ~0–few %.",
      ends: [
        { id: "nw", label: "North / west", ancestry: { eef: 66, whg: 32, steppe: 2 } },
        { id: "s", label: "South", ancestry: { eef: 80, whg: 18, steppe: 2 } },
      ],
    },
  });
}

/* ——— Corded Ware / Bell Beaker ——— */
{
  const p = period("beaker-corded");
  upsertLayer(p, {
    id: "cw-germany",
    label: "Corded Ware (Germany–Bohemia)",
    role: "incoming",
    color: "#a05030",
    countries: ["DEU", "CZE", "AUT"],
  });
  p.narrative =
    "Corded Ware and Bell Beaker remake temperate Europe with Yamnaya-related steppe ancestry — but not uniformly. Steppe% is typically higher in northern/central Corded Ware and Single Grave Denmark than in Iberian Beaker; British Beaker shows near-total turnover of the prior Neolithic pool. Residual farmer/HG clines persist under the new packages.";
  p.culturesNote =
    "Corded Ware, Single Grave, Battle Axe, Bell Beaker (Britain high-turnover; Iberia more gradual) — steppe gradients, not one %.";

  patchRegion(p, "britain", {
    ancestry: { steppe: 50, eef: 35, whg: 15 },
    ancestryRange: { steppe: [40, 60], eef: [25, 45], whg: [8, 22] },
    ancestryNote: "~90% turnover of prior Neolithic ancestry; resulting ternary still varies site-to-site.",
    ancestryCline: {
      label: "Early Beaker pulse → later mix",
      note: "Steppe-rich Beaker immigrants vs slightly more EEF/WHG in some later/local mixes — Britain stays high-steppe overall.",
      ends: [
        { id: "pulse", label: "Beaker pulse", ancestry: { steppe: 60, eef: 28, whg: 12 } },
        { id: "local", label: "Later local mix", ancestry: { steppe: 42, eef: 42, whg: 16 } },
      ],
    },
    description:
      "Bell Beaker Britain: genomic turnover of the Neolithic population. The new mix is steppe + EEF + WHG, with steppe typically highest in the early Beaker pulse and a bit more farmer/HG in some later local profiles — not a single flat percentage.",
  });
  patchRegion(p, "scandinavia", {
    ancestry: { steppe: 70, eef: 18, whg: 12 },
    ancestryRange: { steppe: [55, 85], eef: [8, 30] },
    ancestryNote: "Single Grave / Battle Axe: often ~60–85% steppe-related; southern SGC higher steppe than some inland mixes.",
    ancestryCline: {
      label: "Single Grave south → inland mix",
      note: "Danish Single Grave often at the high end of steppe%; some inland/northern mixes keep more farmer/HG.",
      ends: [
        { id: "sgc", label: "SGC Denmark", ancestry: { steppe: 82, eef: 10, whg: 8 } },
        { id: "inland", label: "Inland / north mix", ancestry: { steppe: 55, eef: 28, whg: 17 } },
      ],
    },
  });
  patchRegion(p, "central", {
    ancestry: { steppe: 55, eef: 35, whg: 10 },
    ancestryRange: { steppe: [40, 75], eef: [20, 50] },
    ancestryNote: "Corded Ware steppe% higher early/east; more GAC-like farmer ancestry persists west/south.",
    ancestryCline: {
      label: "Early/east CW → west farmer mix",
      note: "Steppe highest in early Corded Ware; western/southern profiles keep more Globular Amphora–like EEF.",
      ends: [
        { id: "east", label: "Early / east CW", ancestry: { steppe: 72, eef: 20, whg: 8 } },
        { id: "west", label: "West farmer mix", ancestry: { steppe: 40, eef: 48, whg: 12 } },
      ],
    },
    description:
      "Corded Ware across Germany–Bohemia–Poland with Globular Amphora farmer admixture. Steppe ancestry is clinal: higher in early/eastern CW, lower where GAC-like farmer ancestry persists in the west — not one Corded Ware percentage.",
  });
  patchRegion(p, "iberia", {
    ancestry: { eef: 55, steppe: 25, whg: 20 },
    ancestryRange: { steppe: [10, 40], eef: [45, 70] },
    ancestryNote: "Beaker Iberia: more gradual, often male-biased steppe intake — lower steppe% than Britain/SGC.",
    ancestryCline: {
      label: "Beaker steppe intake → EEF base",
      note: "Steppe rises with Beaker-associated lineages but usually stays below British/Danish levels; EEF remains the base.",
      ends: [
        { id: "beaker", label: "Beaker-enriched", ancestry: { eef: 48, steppe: 38, whg: 14 } },
        { id: "base", label: "EEF-heavy base", ancestry: { eef: 68, steppe: 12, whg: 20 } },
      ],
    },
    description:
      "Bell Beaker Iberia keeps a strong EEF base. Steppe ancestry enters more gradually (and often male-biased) than in Britain — a west Mediterranean cline of lower steppe%, not a copy of the British turnover.",
  });
  patchRegion(p, "france", {
    ancestry: { steppe: 40, eef: 42, whg: 18 },
    ancestryRange: { steppe: [25, 55], eef: [30, 55] },
    ancestryNote: "Beaker/CW France intermediate — higher steppe northeast, more EEF southwest.",
    ancestryCline: {
      label: "Northeast → southwest",
      note: "Steppe% higher toward Rhine/CW contact; southwest keeps more Neolithic EEF+WHG.",
      ends: [
        { id: "ne", label: "Northeast", ancestry: { steppe: 55, eef: 32, whg: 13 } },
        { id: "sw", label: "Southwest", ancestry: { steppe: 25, eef: 55, whg: 20 } },
      ],
    },
  });
  patchRegion(p, "eastern", {
    ancestry: { steppe: 60, eef: 15, ehg: 10, whg: 8, chg: 7 },
    ancestryRange: { steppe: [45, 75] },
    ancestryNote: "Catacomb / steppe-contact Ukraine stays steppe-rich vs farmer-west edges.",
    ancestryCline: {
      label: "Steppe/Catacomb → western contact",
      note: "Steppe highest on Catacomb/steppe; EEF rises toward western Corded Ware contact.",
      ends: [
        { id: "steppe", label: "Catacomb / steppe", ancestry: { steppe: 75, ehg: 8, chg: 8, eef: 5, whg: 4 } },
        { id: "west", label: "Western contact", ancestry: { steppe: 48, eef: 30, whg: 12, ehg: 5, chg: 5 } },
      ],
    },
  });
}

fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
console.log("Patched early-neolithic, middle-neolithic, yamnaya, beaker-corded with holdouts + clines.");
