/* Europa Strata — real Europe map + culture extents */

const REGION_IDS = [
  "iberia",
  "britain",
  "france",
  "central",
  "scandinavia",
  "italy",
  "balkans",
  "eastern",
];


const SLIDER_MAX = 1000;

/**
 * Top-center era tabs — Deep-time stays center / default.
 * Older eras left; newer (Early Modern, Modern) right.
 */
const ATLAS_TAB_ORDER = [
  "high-medieval",
  "renaissance",
  "deep-time",
  "early-modern",
  "modern",
];

/** Single build/version string (also in <meta name="build">; bump with scripts/bump_version.py). */
const BUILD =
  document.querySelector('meta[name="build"]')?.getAttribute("content") || "dev";
const withV = (url) => `${url}${url.includes("?") ? "&" : "?"}v=${encodeURIComponent(BUILD)}`;

function storageGet(key) {
  try {
    return localStorage.getItem(key);
  } catch (_) {
    return null;
  }
}
function storageSet(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (_) {}
}

/** Visible, dismissible data-load notice (replaces silent console-only failures). */
function showLoadNotice(message, { retry = null } = {}) {
  let box = document.getElementById("load-notice");
  if (!box) {
    box = document.createElement("div");
    box.id = "load-notice";
    box.className = "load-notice";
    box.setAttribute("role", "alert");
    document.body.appendChild(box);
  }
  box.replaceChildren();
  const msg = document.createElement("span");
  msg.textContent = message;
  box.appendChild(msg);
  if (retry) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = "Retry";
    b.addEventListener("click", () => {
      box.hidden = true;
      retry();
    });
    box.appendChild(b);
  }
  const x = document.createElement("button");
  x.type = "button";
  x.setAttribute("aria-label", "Dismiss");
  x.textContent = "×";
  x.addEventListener("click", () => (box.hidden = true));
  box.appendChild(x);
  box.hidden = false;
}

const KINGDOM_PACK_IDS = [
  "high-medieval",
  "renaissance",
  "early-modern",
  "modern",
];

const KINGDOM_TAB_LABELS = {
  "high-medieval": "High Medieval",
  renaissance: "Renaissance",
  "early-modern": "Early Modern",
  modern: "Modern",
};

function motionMs(ms) {
  try {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return 0;
  } catch (_) {}
  return ms;
}

const state = {
  data: null,
  geo: null,
  keyEvents: { version: 1, periods: {} },
  atlasMode: "deep-time",
  kingdomPacks: {},
  periodIndex: 0,
  sliderPos: 0, // 0..1 continuous
  selectedIso: null,
  selectedPolityId: null,
  selectedCultureLayer: null,
  selectedRegion: "britain",
  path: null,
  svg: null,
  tip: null,
  zoom: null,
  zoomLayer: null,
  mapSize: { w: 900, h: 700 },
  legendHoverId: null,
  legendPinId: null,
};

function isKingdomMode(mode = state.atlasMode) {
  return mode !== "deep-time" && KINGDOM_PACK_IDS.includes(mode);
}

function activePack() {
  if (!isKingdomMode()) return null;
  return state.kingdomPacks[state.atlasMode] || null;
}

function activePeriods() {
  if (isKingdomMode()) {
    const pack = activePack();
    return pack?.periods || [];
  }
  return state.data?.periods || [];
}

/** Crude lon/lat ring for schematic city-republic “approx” circles. */
function approxCircleRing(center, radiusKm, steps = 20) {
  const [lon0, lat0] = center;
  const dLat = radiusKm / 111.32;
  const cosLat = Math.cos((lat0 * Math.PI) / 180) || 0.2;
  const dLon = radiusKm / (111.32 * cosLat);
  const ring = [];
  for (let i = 0; i <= steps; i++) {
    const a = (i / steps) * Math.PI * 2;
    ring.push([lon0 + Math.cos(a) * dLon, lat0 + Math.sin(a) * dLat]);
  }
  return ring;
}

function extentToGeometry(ext) {
  if (!ext) return null;
  const kind = ext.kind || "polygon";
  if (kind === "approx" && ext.approx?.center) {
    const ring = approxCircleRing(
      ext.approx.center,
      ext.approx.radiusKm || 80
    );
    return { type: "Polygon", coordinates: [ring] };
  }
  const rings = ext.rings;
  if (!rings?.length) return null;
  if (kind === "multi" || (Array.isArray(rings[0]?.[0]) && Array.isArray(rings[0][0]?.[0]))) {
    // rings is array of polygons, each polygon = array of rings (outer only here)
    const polys = rings.map((poly) => {
      // poly may be a single ring [[lon,lat],...] or [ring]
      if (typeof poly[0]?.[0] === "number") return [poly];
      return poly;
    });
    return { type: "MultiPolygon", coordinates: polys };
  }
  // polygon: rings = [outer, ...holes] OR a single outer ring listed directly
  if (typeof rings[0]?.[0] === "number") {
    return { type: "Polygon", coordinates: [rings] };
  }
  return { type: "Polygon", coordinates: rings };
}

/**
 * Normalize kingdom packs:
 * - App/scaffold: { periods, geo }
 * - Research: { ticks, polities[].extentsByTick }
 */
/* Deep-time-inspired earth palette shared by all kingdom-era tabs */
const ERA_PALETTE = [
  "#a8705a", "#c49a6c", "#7d8a6a", "#8a6a4f", "#b4a07a", "#6f7f8c",
  "#9b7b6f", "#c3aa8a", "#8f5a4a", "#a3936b", "#5f6f5f", "#b98f74",
];
const ERA_NEUTRAL = "#e4ded3";
const V2_ATTRIBUTION =
  "Borders: historical-basemaps © A. Ourednik (GPL-3.0) · coasts: Natural Earth.";

/** Greedy colouring so neighbouring polities never share a colour (stable per era). */
function eraPolityColors(topo, polityIds) {
  const adj = new Map(polityIds.map((id) => [id, new Set()]));
  for (const obj of Object.values(topo.objects || {})) {
    const geoms = obj.geometries || [];
    let nb = [];
    try {
      nb = topojson.neighbors(geoms);
    } catch (_) {
      nb = [];
    }
    geoms.forEach((g, i) => {
      const a = g.properties?.polityId;
      if (!a || !adj.has(a)) return;
      for (const j of nb[i] || []) {
        const b = geoms[j].properties?.polityId;
        if (b && b !== a && adj.has(b)) {
          adj.get(a).add(b);
          adj.get(b).add(a);
        }
      }
    });
  }
  const order = [...polityIds].sort((a, b) => adj.get(b).size - adj.get(a).size);
  const colors = {};
  for (const id of order) {
    const used = new Set([...adj.get(id)].map((n) => colors[n]).filter(Boolean));
    let h = 0;
    for (const ch of id) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
    let pick = null;
    for (let k = 0; k < ERA_PALETTE.length; k++) {
      const c = ERA_PALETTE[(h + k) % ERA_PALETTE.length];
      if (!used.has(c)) {
        pick = c;
        break;
      }
    }
    colors[id] = pick || ERA_PALETTE[h % ERA_PALETTE.length];
  }
  return colors;
}

function polityPanel(p) {
  return {
    name: p.name,
    type: p.type,
    yearsActive: p.yearsActive,
    summary: p.description || "",
    description: p.description || "",
    conflicts: p.conflicts || "",
    leaders: p.leaders || "",
    religion: p.religion || "",
    culture: p.culture || "",
    story: p.stories || p.story || "",
    stories: p.stories || p.story || null,
    literature: p.literature || "",
    art: p.art || "",
    ideas: p.ideas || "",
    artIdeas: p.artIdeas || p.artAndIdeas || "",
    philosophy: p.philosophy || "",
    science: p.science || "",
    images: p.images || null,
  };
}

/** Build one tick's layers/panels/geo from the era TopoJSON. */
function v2TickFromTopo(topo, obj, raw, colors) {
  const byId = new Map(raw.polities.map((p) => [p.id, p]));
  const fc = topojson.feature(topo, obj);
  const mapLayers = [];
  const polities = {};
  const features = [];
  let approxCount = 0;
  fc.features.forEach((f, i) => {
    const props = f.properties || {};
    const p = props.polityId ? byId.get(props.polityId) : null;
    if (props.approx) approxCount++;
    if (p) {
      if (!polities[p.id]) {
        polities[p.id] = polityPanel(p);
        mapLayers.push({
          polityId: p.id,
          id: p.id,
          label: p.name,
          color: colors[p.id] || p.color || "#8a7a6a",
          role: "dominant",
        });
      }
      features.push({
        type: "Feature",
        properties: { polityId: p.id, name: p.name, type: p.type || "", approx: !!props.approx },
        geometry: f.geometry,
      });
    } else {
      const name = String(props.name || "").trim() || "Unnamed territory";
      const xid = `x-${i}-${name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
      polities[xid] = {
        name,
        type: "Other polity",
        summary: `${name}, shown from the historical-basemaps dataset. No Europa Strata profile yet.`,
        description: "",
      };
      mapLayers.push({ polityId: xid, id: xid, label: name, color: ERA_NEUTRAL, role: "dominant", extra: true });
      features.push({
        type: "Feature",
        properties: { polityId: xid, name, type: "", extra: true },
        geometry: f.geometry,
      });
    }
  });
  return {
    mapLayers,
    polities,
    geo: { type: "FeatureCollection", features },
    // all arcs: shared borders + coastlines, one line like Deep-time
    borders: topojson.mesh(topo, obj),
    approxBorders: topojson.mesh(
      topo,
      obj,
      (a, b) => Boolean(a.properties?.approx || b.properties?.approx)
    ),
    approxTick: approxCount > 0 && approxCount === fc.features.length,
  };
}

function normalizeKingdomPack(raw, topo = null) {
  if (!raw) return null;
  if (Array.isArray(raw.periods) && (raw.geo || raw.periods.some((p) => p.geo))) {
    return {
      id: raw.id || raw.tabId || "kingdom",
      label: raw.label || raw.tabLabel || "Kingdom era",
      yearRange: raw.yearRange || null,
      defaultYear: raw.defaultYear ?? null,
      mapAttribution:
        raw.mapAttribution ||
        raw.notes ||
        "Schematic kingdom extents, not modern borders.",
      status: raw.status || "ready",
      ticks: raw.ticks || [],
      periods: raw.periods,
      geo: raw.geo || null,
    };
  }

  if (!Array.isArray(raw.polities) || !Array.isArray(raw.ticks)) return raw;

  const id = raw.tabId || raw.id || "kingdom";
  const v2 = Boolean(topo && window.topojson);
  const v2Colors = v2 ? eraPolityColors(topo, raw.polities.map((p) => p.id)) : null;
  const label = raw.tabLabel || raw.label || "Kingdom era";
  const periods = raw.ticks.map((tick) => {
    const year = tick.year ?? tick.yearApprox;
    const yearKey = String(year);
    const tickLabel = tick.label || `${year} AD`;
    // Avoid stacking identical "1200 AD" in slider year + period label
    const yearOnly = String(year);
    const labelBare = String(tickLabel)
      .replace(/\s*(AD|BC|CE|BCE)\s*/gi, "")
      .trim();
    const periodName =
      tick.name ||
      tick.periodLabel ||
      (labelBare === yearOnly ? label : tickLabel);
    const tickEyebrow = (tick.era || tick.eyebrow || tick.theme || "").trim();
    const tickNarrative = (
      tick.narrative ||
      tick.summary ||
      tick.description ||
      ""
    ).trim();
    const v2Obj = v2 ? topo.objects?.[`y${year}`] : null;
    if (v2Obj) {
      const t = v2TickFromTopo(topo, v2Obj, raw, v2Colors);
      return {
        id: `${id}-${year}`,
        yearApprox: year,
        yearLabel: `${year} AD`,
        label: periodName,
        tickYear: `${year} AD`,
        era: tickEyebrow || label,
        narrative: tickNarrative || raw.narrative || raw.notes || "",
        culturesNote: tickEyebrow || "",
        mapLayers: t.mapLayers,
        polities: t.polities,
        geo: t.geo,
        v2: true,
        borders: t.borders,
        approxBorders: t.approxBorders,
        approxTick: t.approxTick,
      };
    }
    const mapLayers = [];
    const polities = {};
    const features = [];

    for (const p of raw.polities) {
      const ext = p.extentsByTick?.[yearKey];
      if (!ext) continue;
      const geom = extentToGeometry(ext);
      if (!geom) continue;
      const polityId = p.id;
      mapLayers.push({
        polityId,
        id: polityId,
        label: p.name,
        color: p.color || "#6b7c8a",
        role: "dominant",
      });
      polities[polityId] = {
        name: p.name,
        type: p.type,
        yearsActive: p.yearsActive,
        summary: p.description || "",
        description: p.description || "",
        conflicts: p.conflicts || "",
        leaders: p.leaders || "",
        religion: p.religion || "",
        culture: p.culture || "",
        story: p.stories || p.story || "",
        stories: p.stories || p.story || null,
        literature: p.literature || "",
        art: p.art || "",
        ideas: p.ideas || "",
        artIdeas: p.artIdeas || p.artAndIdeas || "",
        philosophy: p.philosophy || "",
        science: p.science || "",
        images: p.images || null,
      };
      features.push({
        type: "Feature",
        properties: {
          polityId,
          name: p.name,
          type: p.type || "",
        },
        geometry: geom,
      });
    }

    return {
      id: `${id}-${year}`,
      yearApprox: year,
      yearLabel: `${year} AD`,
      label: periodName,
      tickYear: `${year} AD`,
      // Prefer tick-specific eyebrow; fall back to tab label only if none authored
      era: tickEyebrow || label,
      narrative:
        tickNarrative ||
        raw.narrative ||
        raw.notes ||
        `Schematic ${label} polities around ${year} AD: kingdoms, empires, duchies, and confederations (not modern borders).`,
      culturesNote: tickEyebrow || "",
      mapLayers,
      polities,
      geo: { type: "FeatureCollection", features },
    };
  });

  return {
    id,
    label,
    yearRange: raw.yearRange || [
      raw.ticks[0]?.year,
      raw.ticks[raw.ticks.length - 1]?.year,
    ],
    defaultYear: raw.defaultYear ?? null,
    mapAttribution: v2
      ? V2_ATTRIBUTION
      : raw.mapAttribution ||
        raw.notes ||
        "Schematic kingdom extents, not modern state borders.",
    v2,
    status: raw.status || "ready",
    ticks: raw.ticks,
    periods,
    geo: periods[0]?.geo || { type: "FeatureCollection", features: [] },
  };
}

function kingdomGeoForPeriod(period) {
  return period?.geo || activePack()?.geo || null;
}

/** Chaikin corner-cutting — softer polity outlines without angular rings. */
function chaikinRing(ring, iterations = 2) {
  if (!ring?.length || ring.length < 4) return ring;
  let pts = ring.slice();
  const closed =
    pts.length > 1 &&
    pts[0][0] === pts[pts.length - 1][0] &&
    pts[0][1] === pts[pts.length - 1][1];
  if (closed) pts = pts.slice(0, -1);
  for (let iter = 0; iter < iterations; iter++) {
    const next = [];
    const n = pts.length;
    for (let i = 0; i < n; i++) {
      const a = pts[i];
      const b = pts[(i + 1) % n];
      next.push([0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]]);
      next.push([0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]]);
    }
    pts = next;
  }
  if (closed || pts.length) pts = pts.concat([pts[0]]);
  return pts;
}

function smoothGeometry(geom) {
  if (!geom) return geom;
  if (geom.type === "Polygon") {
    return {
      type: "Polygon",
      coordinates: geom.coordinates.map((r) => chaikinRing(r, 2)),
    };
  }
  if (geom.type === "MultiPolygon") {
    return {
      type: "MultiPolygon",
      coordinates: geom.coordinates.map((poly) =>
        poly.map((r) => chaikinRing(r, 2))
      ),
    };
  }
  return geom;
}

function smoothFeatureCollection(fc) {
  if (!fc?.features) return fc;
  return {
    type: "FeatureCollection",
    features: fc.features.map((f) => ({
      ...f,
      geometry: smoothGeometry(f.geometry),
    })),
  };
}

function kingdomGeoSmoothed(period) {
  const key = period?.id || "";
  if (!key) return null;
  if (!state._smoothGeoCache) state._smoothGeoCache = new Map();
  if (state._smoothGeoCache.has(key)) return state._smoothGeoCache.get(key);
  const raw = kingdomGeoForPeriod(period);
  // v2 TopoJSON borders are shared arcs — smoothing would split neighbours apart
  const smoothed = period?.v2 ? raw : smoothFeatureCollection(raw);
  state._smoothGeoCache.set(key, smoothed);
  return smoothed;
}

function $(sel) {
  return document.querySelector(sel);
}

function $$(sel) {
  return [...document.querySelectorAll(sel)];
}

/** Only allow plain CSS colors from data into style attributes. */
function safeColor(c) {
  const v = String(c || "").trim();
  return /^(#[0-9a-f]{3,8}|rgba?\([\d\s.,%]+\)|hsla?\([\d\s.,%deg]+\)|[a-z]+)$/i.test(v) ? v : "transparent";
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function resolveChainRef(ref) {
  if (!ref) return null;
  if (typeof ref === "string") {
    const [periodId, iso] = ref.split(":");
    if (!periodId || !iso) return null;
    const period = state.data.periods.find((p) => p.id === periodId);
    return {
      periodId,
      iso,
      name: period?.polities?.[iso]?.name || `${iso} · ${periodId}`,
    };
  }
  if (ref.periodId && ref.iso) {
    return {
      periodId: ref.periodId,
      iso: ref.iso,
      name:
        ref.name ||
        state.data.periods.find((p) => p.id === ref.periodId)?.polities?.[
          ref.iso
        ]?.name ||
        ref.iso,
    };
  }
  return null;
}

function goToAtlasTarget(ref) {
  const target = resolveChainRef(ref);
  if (!target) return;
  // Chain links target Deep-time polity ISOs
  if (isKingdomMode()) setAtlasMode("deep-time");
  const idx = state.data.periods.findIndex((p) => p.id === target.periodId);
  if (idx < 0) return;
  state.selectedIso = target.iso;
  state.selectedPolityId = null;
  const rid = isoToRegion(target.iso);
  if (rid) state.selectedRegion = rid;
  snapToPeriod(idx);
  state.svg
    ?.selectAll("path.country")
    .classed("is-active", (d) => d.properties.iso === target.iso);
  // Bring the detail panel into view on stacked mobile layout
  requestAnimationFrame(() => {
    $("#detail")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function atlasLinkHtml(ref, label) {
  const t = resolveChainRef(ref);
  if (!t) return escapeHtml(label || "");
  const text = label || t.name;
  // Use <a> (not <button>) so iOS/WebKit inherits parent body metrics reliably
  return `<a href="#${escapeHtml(t.periodId)}/${escapeHtml(t.iso)}" class="atlas-link" data-period="${escapeHtml(t.periodId)}" data-iso="${escapeHtml(t.iso)}" title="Go to ${escapeHtml(t.name)}">${escapeHtml(text)}</a>`;
}

/** Body/description copy — plain text only (no <a>/buttons/pills). */
function setPlainText(el, text) {
  if (!el) return;
  // Wipe any prior markup nodes, then set text (never innerHTML).
  while (el.firstChild) el.removeChild(el.firstChild);
  el.textContent = String(text ?? "");
}

/** Multi-paragraph plain prose (splits on blank lines) for long deep-time / kingdom copy. */
function setProseText(el, text) {
  if (!el) return;
  while (el.firstChild) el.removeChild(el.firstChild);
  const raw = String(text ?? "").trim();
  if (!raw) return;
  const paras = raw.split(/\n\n+/).map((s) => s.trim()).filter(Boolean);
  if (paras.length <= 1) {
    el.textContent = raw;
    return;
  }
  paras.forEach((para, i) => {
    if (i) el.appendChild(document.createElement("br"));
    el.appendChild(document.createElement("br"));
    el.appendChild(document.createTextNode(para));
  });
}

/** Strip accidental interactive markup if anything else wrote HTML into body fields. */
function scrubBodyCopyMarkup(root = document) {
  const fields = root.querySelectorAll(
    [
      "#culture-desc",
      "#ancestry-note",
      "#polity-summary",
      "#polity-conflicts",
      "#polity-leaders",
      "#polity-religion",
      "#polity-culture",
      "#polity-story",
      "#polity-literature",
      "#polity-art",
      "#polity-philosophy",
      "#polity-science",
      "#period-copy",
      "#period-ling",
      "#ling-note",
      "#absorb-substrate",
      "#absorb-incoming",
      "#absorb-fused",
    ].join(",")
  );
  fields.forEach((el) => {
    if (!el) return;
    // Flatten any nested <a>/<button>/<span class=atlas-link> to plain text
    const junk = el.querySelectorAll("a, button, .atlas-link");
    if (!junk.length) return;
    el.textContent = el.textContent;
  });
}

function renderPolityChain(polity) {
  const row = $("#polity-chain");
  if (!row) return;
  const prev = resolveChainRef(polity?.precededBy);
  const next = resolveChainRef(polity?.succeededBy);
  if (!prev && !next) {
    row.hidden = true;
    row.innerHTML = "";
    return;
  }
  row.hidden = false;
  const parts = [];
  if (prev) {
    parts.push(
      `<span class="polity-chain-item"><span class="polity-chain-label">Preceded by</span> ${atlasLinkHtml(prev)}</span>`
    );
  }
  if (next) {
    parts.push(
      `<span class="polity-chain-item"><span class="polity-chain-label">Succeeded by</span> ${atlasLinkHtml(next)}</span>`
    );
  }
  row.innerHTML = parts.join('<span class="polity-chain-sep" aria-hidden="true">·</span>');
}

function currentPeriod() {
  const periods = activePeriods();
  return periods[state.periodIndex] || periods[0] || null;
}

function regionData(period, id) {
  return period?.regions?.[id] || null;
}

function layerPolityId(layer) {
  return layer?.polityId || layer?.id || null;
}

function isoToRegion(iso) {
  const map = state.data.meta.regionCountries || {};
  for (const [rid, list] of Object.entries(map)) {
    if (list.includes(iso)) return rid;
  }
  return null;
}

function periodIndexFromSlider(pos) {
  const n = activePeriods().length;
  if (n <= 1) return 0;
  return Math.min(n - 1, Math.round(pos * (n - 1)));
}

/** Color for a kingdom polity at a discrete period (from mapLayers). */
function polityStyleForPeriod(period, polityId) {
  const layers = period?.mapLayers || [];
  const layer = layers.find((l) => layerPolityId(l) === polityId);
  if (!layer) return { fill: null, opacity: 0, label: null };
  const role = layer.role || "dominant";
  const opacity =
    role === "fringe" || role === "substrate" ? 0.42 : role === "incoming" ? 0.7 : 0.78;
  return { fill: layer.color, opacity, label: layer.label || polityId };
}

function interpolatedPolityStyle(polityId, pos) {
  const periods = activePeriods();
  if (!periods.length) return { fill: null, opacity: 0, label: null };
  if (periods.length === 1) return polityStyleForPeriod(periods[0], polityId);
  const max = periods.length - 1;
  const f = Math.max(0, Math.min(1, pos)) * max;
  const i0 = Math.floor(f);
  const i1 = Math.min(max, i0 + 1);
  const t = f - i0;
  const a = polityStyleForPeriod(periods[i0], polityId);
  const b = polityStyleForPeriod(periods[i1], polityId);
  if (!a.fill && !b.fill) return { fill: null, opacity: 0, label: null };
  if (!a.fill) return b;
  if (!b.fill) return a;
  return {
    fill: lerpColor(a.fill, b.fill, t),
    opacity: a.opacity + (b.opacity - a.opacity) * t,
    label: t < 0.5 ? a.label : b.label,
  };
}

function lerpColor(a, b, t) {
  const pa = d3.color(a);
  const pb = d3.color(b);
  if (!pa || !pb) return a;
  return d3.interpolateRgb(pa, pb)(t);
}

/** Dominant culture color for an ISO in a period (incoming > dominant > fringe > substrate) */
function countryStyleForPeriod(period, iso) {
  const layers = period.mapLayers || [];
  const roleRank = { incoming: 4, dominant: 3, fringe: 2, substrate: 1 };
  let best = null;
  for (const layer of layers) {
    if (!layer.countries?.includes(iso)) continue;
    const rank = roleRank[layer.role] || 0;
    if (!best || rank > best.rank) {
      best = { layer, rank };
    }
  }
  if (!best) {
    return { fill: null, opacity: 1, labels: [] };
  }
  // Collect all labels covering this country for tooltip
  const labels = layers
    .filter((l) => l.countries?.includes(iso))
    .sort((a, b) => (roleRank[b.role] || 0) - (roleRank[a.role] || 0));
  return {
    fill: best.layer.color,
    opacity: best.layer.opacity ?? 0.75,
    labels,
    role: best.layer.role,
  };
}

function interpolatedCountryStyle(iso, pos) {
  const periods = state.data.periods;
  const n = periods.length;
  if (n === 0) return { fill: null, opacity: 1, labels: [] };
  if (n === 1) return countryStyleForPeriod(periods[0], iso);

  const x = pos * (n - 1);
  const i0 = Math.floor(x);
  const i1 = Math.min(n - 1, i0 + 1);
  const t = x - i0;
  const s0 = countryStyleForPeriod(periods[i0], iso);
  const s1 = countryStyleForPeriod(periods[i1], iso);

  // Prefer nearer period's labels
  const labels = (t < 0.5 ? s0.labels : s1.labels) || [];

  if (!s0.fill && !s1.fill) return { fill: null, opacity: 1, labels };
  if (!s0.fill) return { fill: s1.fill, opacity: (s1.opacity || 0.75) * t, labels };
  if (!s1.fill) return { fill: s0.fill, opacity: (s0.opacity || 0.75) * (1 - t), labels };

  return {
    fill: lerpColor(s0.fill, s1.fill, t),
    opacity: (s0.opacity || 0.75) * (1 - t) + (s1.opacity || 0.75) * t,
    labels,
    role: t < 0.5 ? s0.role : s1.role,
  };
}

/** Normalize ancestry map; support midpoints and [min,max] ranges. */
function ancestryMap(source) {
  const a = source || {};
  const out = {};
  for (const [id, v] of Object.entries(a)) {
    if (Array.isArray(v) && v.length >= 2) {
      out[id] = (Number(v[0]) + Number(v[1])) / 2;
    } else {
      out[id] = Number(v) || 0;
    }
  }
  return out;
}

/**
 * Contextual label/definition for the catch-all "other" ancestry slice.
 * Uses explicit region fields when present; otherwise derives honest residual
 * hints from ancestryNote without inventing percentages.
 */
function resolveOtherMeta(region, baseKey = {}) {
  const explicitLabel = String(
    region?.otherLabel || region?.otherName || ""
  ).trim();
  const explicitDetail = String(
    region?.otherDetail || region?.otherNote || ""
  ).trim();
  const note = String(region?.ancestryNote || "").trim();
  const n = note.toLowerCase();

  const hints = [];
  if (/east eurasian|siber|nganasan/.test(n)) {
    hints.push("East Eurasian / Siberian-related");
  }
  if (/eastern med|east med|imperial|levant/.test(n)) {
    hints.push("eastern Mediterranean / imperial");
  }
  if (/north african|maghreb/.test(n)) hints.push("North African-related");
  if (/\bchg\b|iran-related|iranian/.test(n)) hints.push("CHG / Iran-related");
  if (/slavic/.test(n)) hints.push("Slavic-related residual");
  if (/finnic|saami|\buralic\b/.test(n)) hints.push("Finnic / northern residual");
  if (/turkic/.test(n)) hints.push("Turkic-related residual");
  if (/local structure|poorly resolved|uncertain|model-dependent/.test(n)) {
    hints.push("local / model-dependent residual");
  }

  const hintText = hints.length ? hints.join("; ") : "";
  const full =
    explicitLabel ||
    hintText ||
    baseKey.full ||
    "Residual / unmodeled components";
  let detail = explicitDetail;
  if (!detail) {
    const baseDetail =
      baseKey.detail ||
      "Residual ancestry outside the main WHG–EEF–WSH (and named) components. Not a single deep Paleolithic cluster.";
    if (hintText && note) {
      detail = `Residual / unmodeled slice: ${hintText}. ${note}`;
    } else if (note) {
      detail = `Residual / unmodeled ancestry outside the main modeled components. ${note}`;
    } else {
      detail = baseDetail;
    }
  }

  const shortHint = hints[0] || "residual / unmodeled";
  return {
    ...baseKey,
    id: "other",
    label: "Other",
    displayLabel: explicitLabel
      ? `Other · ${explicitLabel}`
      : `Other · ${shortHint}`,
    full,
    detail,
  };
}

function ancestryEntries(region, keys, source) {
  const a = ancestryMap(source || region.ancestry);
  const ranges = region.ancestryRange || {};
  return keys
    .map((k) => {
      const value = Number(a[k.id]) || 0;
      const range = ranges[k.id];
      let rangeLabel = null;
      if (Array.isArray(range) && range.length >= 2) {
        rangeLabel = `${Math.round(range[0])}–${Math.round(range[1])}%`;
      }
      const meta =
        k.id === "other" && (value > 0 || rangeLabel)
          ? resolveOtherMeta(region, k)
          : k;
      return {
        ...meta,
        value,
        rangeLabel,
        detail: meta.detail || meta.full,
      };
    })
    .filter((k) => k.value > 0 || k.rangeLabel);
}

function renderAncestryCline(region, keys) {
  const box = $("#ancestry-cline");
  const endsEl = $("#cline-ends");
  const noteEl = $("#cline-note");
  const labelEl = $("#cline-label");
  const midLabel = $("#ancestry-mid-label");
  const cline = region.ancestryCline;
  if (!box || !endsEl) return;
  if (!cline?.ends?.length) {
    box.hidden = true;
    endsEl.innerHTML = "";
    if (noteEl) noteEl.textContent = "";
    if (midLabel) midLabel.hidden = true;
    return;
  }
  box.hidden = false;
  if (midLabel) midLabel.hidden = false;
  if (labelEl) labelEl.textContent = cline.label || "Geographic cline";
  if (noteEl) noteEl.textContent = cline.note || "";
  endsEl.innerHTML = cline.ends
    .map((end) => {
      const entries = ancestryEntries(region, keys, end.ancestry);
      const total = entries.reduce((s, e) => s + e.value, 0) || 1;
      const segs = entries
        .map((e) => {
          const w = (e.value / total) * 100;
          return `<div class="stack-seg" style="width:${w}%;background:${safeColor(e.color)}" title="${escapeHtml(e.label)}: ~${Math.round(e.value)}%"></div>`;
        })
        .join("");
      const legend = entries
        .map((e) => `${escapeHtml(e.label)} ~${Math.round(e.value)}%`)
        .join(" · ");
      return `<div class="cline-end">
        <p class="cline-end-label">${escapeHtml(end.label || end.id)}</p>
        <div class="stack-bar cline-bar">${segs}</div>
        <p class="cline-end-legend">${legend}</p>
      </div>`;
    })
    .join("");
}

/** Flat pie wedges. Remainder (when parts sum under 100) is a solid land fill. */
function pieMarkup(entries) {
  const usable = (entries || []).filter((e) => (Number(e.value) || 0) > 0);
  const sum = usable.reduce((s, e) => s + (Number(e.value) || 0), 0);
  if (!usable.length || sum <= 0) {
    return `<svg class="pie-svg" viewBox="0 0 100 100" aria-hidden="true"><circle class="pie-rest" cx="50" cy="50" r="50" /></svg>`;
  }
  const total = Math.max(sum, 100);
  let angle = -Math.PI / 2;
  const cx = 50;
  const cy = 50;
  const r = 50;
  const parts = [];
  const wedge = (sweep, fill, rest) => {
    if (sweep >= Math.PI * 2 - 0.0001) {
      return rest
        ? `<circle class="pie-rest" cx="50" cy="50" r="50" />`
        : `<circle cx="50" cy="50" r="50" fill="${fill}" />`;
    }
    const a0 = angle;
    const a1 = angle + sweep;
    angle = a1;
    const x0 = cx + r * Math.cos(a0);
    const y0 = cy + r * Math.sin(a0);
    const x1 = cx + r * Math.cos(a1);
    const y1 = cy + r * Math.sin(a1);
    const large = sweep > Math.PI ? 1 : 0;
    const d = `M ${cx} ${cy} L ${x0.toFixed(3)} ${y0.toFixed(3)} A ${r} ${r} 0 ${large} 1 ${x1.toFixed(3)} ${y1.toFixed(3)} Z`;
    return rest
      ? `<path class="pie-rest" d="${d}" />`
      : `<path d="${d}" fill="${fill}" />`;
  };
  for (const e of usable) {
    parts.push(wedge(((Number(e.value) || 0) / total) * Math.PI * 2, safeColor(e.color), false));
  }
  if (sum < 99.5) parts.push(wedge(((total - sum) / total) * Math.PI * 2, "", true));
  return `<svg class="pie-svg" viewBox="0 0 100 100" aria-hidden="true">${parts.join("")}</svg>`;
}

function shortPeriodName(p) {
  // Compact but full words for the secondary tick line (not snapshot titles)
  const map = {
    mesolithic: "Mesolithic",
    "early-neolithic": "Early Neolithic",
    "middle-neolithic": "Middle Neolithic",
    yamnaya: "Yamnaya",
    "beaker-corded": "Corded Ware / Beaker",
    "nordic-bronze": "Bronze Age",
    "iron-age": "Iron Age",
    classical: "Classical / Roman",
    migration: "Migration Period",
    frankish: "Frankish / Carolingian",
    vikings: "Viking Age",
    "high-medieval": "High Medieval",
    "late-medieval": "Late Medieval",
    reformation: "Reformation",
    "early-modern": "Early Modern",
    modern: "Modern",
  };
  return map[p.id] || p.periodName || p.label;
}

/* ——— Map ——— */

/** Drop overseas rings (Canaries, Caribbean, Reunion, Svalbard, …) so fitExtent
 *  frames continental Europe + Iceland, not the full colonial footprint. */
function clipFeatureToEurope(feature) {
  const g = feature.geometry;
  if (!g) return null;
  const ringInEurope = (ring) => {
    let lon = 0;
    let lat = 0;
    const n = ring.length;
    for (let i = 0; i < n; i++) {
      lon += ring[i][0];
      lat += ring[i][1];
    }
    lon /= n;
    lat /= n;
    return lon >= -25 && lon <= 45 && lat >= 34.2 && lat <= 72.2;
  };
  if (g.type === "Polygon") {
    return ringInEurope(g.coordinates[0]) ? feature : null;
  }
  if (g.type === "MultiPolygon") {
    const parts = g.coordinates.filter((poly) => ringInEurope(poly[0]));
    if (!parts.length) return null;
    if (parts.length === 1) {
      return {
        type: "Feature",
        properties: feature.properties,
        geometry: { type: "Polygon", coordinates: parts[0] },
      };
    }
    return {
      type: "Feature",
      properties: feature.properties,
      geometry: { type: "MultiPolygon", coordinates: parts },
    };
  }
  return feature;
}

function initMap({ preserveZoom = true } = {}) {
  const el = $("#map");
  const w = Math.max(el.clientWidth || 900, 320);
  const h = Math.max(el.clientHeight || 700, 280);

  // Keep user zoom across remaps (mobile URL-bar resize must not yank zoom out)
  let savedZoom = null;
  if (preserveZoom && state.svg?.node) {
    try {
      const t = d3.zoomTransform(state.svg.node());
      if (t && (Math.abs(t.k - 1) > 0.001 || Math.abs(t.x) > 0.5 || Math.abs(t.y) > 0.5)) {
        savedZoom = { k: t.k, x: t.x, y: t.y };
      }
    } catch (_) {
      /* ignore */
    }
  }
  if (!savedZoom && preserveZoom && state.savedZoom) {
    savedZoom = state.savedZoom;
  }

  el.innerHTML = "";
  state.tip = d3
    .select(el)
    .append("div")
    .attr("class", "map-tip")
    .style("opacity", 0);

  const svg = d3
    .select(el)
    .append("svg")
    .attr("viewBox", `0 0 ${w} ${h}`)
    .attr("preserveAspectRatio", "xMidYMid meet");

  state.svg = svg;
  // Tap/click on open sea (not a polity) clears the kingdom selection
  svg.on("click.clearsel", (event) => {
    if (event.defaultPrevented) return;
    if (event.target?.closest?.("path.polity")) return;
    clearPolitySelection();
  });
  state.mapPixelSize = { w, h };

  const projection = d3.geoAzimuthalEqualArea();

  // Open/Reset: Spain–Moscow continental framing (same for Deep-time + kingdom).
  // Iceland stays drawn but out of the fit so it doesn’t pull the view west.
  const LAND_ROTATE = [-10.5, -52];
  const LAND_PAD = [8, 14, 8, 10]; // L,T,R,B
  const LAND_BOOST = 1.14;
  const LAND_DRAW_ISOS = [
    "ISL", "IRL", "GBR", "PRT", "ESP", "FRA", "AND", "BEL", "NLD", "LUX",
    "DEU", "CHE", "AUT", "ITA", "DNK", "NOR", "SWE", "FIN", "POL", "CZE",
    "SVK", "HUN", "SVN", "HRV", "BIH", "SRB", "MNE", "ALB", "MKD", "KOS",
    "ROU", "BGR", "GRC", "MDA", "UKR", "BLR", "LTU", "LVA", "EST", "TUR",
  ];
  // Fit on Iberia→Baltic→Balkans (+ Moscow / Black Sea anchors). Skip ISL.
  const LAND_FIT_ISOS = LAND_DRAW_ISOS.filter((iso) => iso !== "ISL");
  const mainland = state.geo.features
    .filter((f) => LAND_DRAW_ISOS.includes(f.properties.iso))
    .map(clipFeatureToEurope)
    .filter(Boolean);
  state.landFeatures = mainland;
  const fitFeatures = mainland.filter((f) =>
    LAND_FIT_ISOS.includes(f.properties.iso)
  );
  const land = {
    type: "FeatureCollection",
    features: [
      ...fitFeatures,
      // East-of-Moscow / Black Sea anchors (RUS polygon is too huge)
      {
        type: "Feature",
        properties: { iso: "_anchor_moscow_e" },
        geometry: { type: "Point", coordinates: [37.6, 55.8] },
      },
      {
        type: "Feature",
        properties: { iso: "_anchor_black_sea_e" },
        geometry: { type: "Point", coordinates: [39.5, 43.5] },
      },
    ],
  };
  projection.rotate(LAND_ROTATE).fitExtent(
    [
      [LAND_PAD[0], LAND_PAD[1]],
      [w - LAND_PAD[2], h - LAND_PAD[3]],
    ],
    land
  );
  const baseScale = projection.scale();
  projection.scale(baseScale * LAND_BOOST);
  const t0 = projection.translate();
  projection.translate([t0[0], t0[1] + 4]);
  state.mapFit = {
    mode: "land-fit",
    rotate: LAND_ROTATE,
    pad: LAND_PAD,
    boost: LAND_BOOST,
    baseScale,
    scale: projection.scale(),
    translate: projection.translate(),
    stage: [w, h],
  };

  state.path = d3.geoPath(projection);
  state.mapSize = { w, h };

  // Zoom/pan layer — transforms the map only; page chrome stays put
  const zoomLayer = svg.append("g").attr("class", "map-zoom");
  state.zoomLayer = zoomLayer;

  // Clip polity fills to Natural Earth land so oceans stay clear
  const defs = zoomLayer.append("defs");
  const landClip = defs
    .append("clipPath")
    .attr("id", "land-clip")
    .attr("clipPathUnits", "userSpaceOnUse");
  landClip
    .selectAll("path")
    .data(mainland)
    .join("path")
    .attr("d", state.path);

  // Kingdom-era polities clip to ALL Natural Earth land (incl. Russia) so
  // eastern empires aren't cut off; Deep-time keeps its own rendering.
  defs
    .append("clipPath")
    .attr("id", "polity-clip")
    .attr("clipPathUnits", "userSpaceOnUse")
    .selectAll("path")
    .data(state.geo.features)
    .join("path")
    .attr("d", state.path);

  const g = zoomLayer.append("g").attr("class", "countries");

  g.selectAll("path")
    .data(state.geo.features)
    .join("path")
    .attr("class", "country")
    .attr("d", state.path)
    .attr("data-iso", (d) => d.properties.iso)
    .attr("data-name", (d) => d.properties.name)
    .on("mouseenter", onCountryEnter)
    .on("mousemove", onCountryMove)
    .on("mouseleave", onCountryLeave)
    .on("click", onCountryClick);

  // Partial-country culture fills (data/timeline.json meta.fillExtents): an overlay
  // per listed country, clipped to that period's lon/lat outline. The country path
  // underneath keeps hover/click and shows plain land outside the outline.
  const extentIsos = new Set(Object.keys(state.data?.meta?.fillExtents?.countries || {}));
  const extentFeatures = state.geo.features.filter((f) => extentIsos.has(f.properties.iso));
  defs
    .selectAll("clipPath.extent-clip")
    .data(extentFeatures)
    .join("clipPath")
    .attr("class", "extent-clip")
    .attr("id", (d) => `extent-clip-${d.properties.iso}`)
    .attr("clipPathUnits", "userSpaceOnUse")
    .append("path");
  zoomLayer
    .append("g")
    .attr("class", "country-extents")
    .attr("aria-hidden", "true")
    .selectAll("path")
    .data(extentFeatures)
    .join("path")
    .attr("class", "country-extent")
    .attr("data-iso", (d) => d.properties.iso)
    .attr("d", state.path)
    .attr("clip-path", (d) => `url(#extent-clip-${d.properties.iso})`)
    .style("fill-opacity", 0);

  // Coastlines under polities so fills stay clickable
  const coasts = zoomLayer.append("g").attr("class", "coasts");
  coasts
    .selectAll("path")
    .data(mainland)
    .join("path")
    .attr("class", "coastline")
    .attr("d", state.path);

  // Kingdom / empire extents — clipped to land; above coasts for hit-testing
  zoomLayer
    .append("g")
    .attr("class", "polities")
    .attr("clip-path", "url(#polity-clip)");
  // v2: shared polity borders drawn once (no double strokes), above fills
  zoomLayer
    .append("g")
    .attr("class", "polity-borders")
    .attr("clip-path", "url(#polity-clip)")
    .style("pointer-events", "none");

  state._kingdomGeoPeriodId = null;
  if (isKingdomMode()) syncKingdomPolityLayer({ force: true });

  const zoom = d3
    .zoom()
    // Allow a little zoom-out from the baked-in default; Reset = identity
    .scaleExtent([0.7, 8])
    .extent([
      [0, 0],
      [w, h],
    ])
    .translateExtent([
      [-w * 0.45, -h * 0.45],
      [w * 1.45, h * 1.45],
    ])
    .filter((event) => {
      // Never steal taps from zoom chrome
      const t = event.target;
      if (t && t.closest && t.closest(".map-tools, .map-chrome")) {
        return false;
      }
      // Never steal wheel — page scroll must not zoom the map in or out.
      // Zoom only via pinch, ± buttons, or Reset.
      if (event.type === "wheel") return false;
      // Pinch (2+ touches) zooms the map, even from default framing
      const touches = event.touches || event.targetTouches;
      if (touches && touches.length >= 2) return true;
      // Single-finger / mouse drag: only pan once already zoomed/panned in
      if (!mapGestureEngaged()) return false;
      return !event.button;
    })
    .on("zoom", (event) => {
      zoomLayer.attr("transform", event.transform);
      const t = event.transform;
      state.savedZoom =
        Math.abs(t.k - 1) > 0.001 || Math.abs(t.x) > 0.5 || Math.abs(t.y) > 0.5
          ? { k: t.k, x: t.x, y: t.y }
          : null;
      syncZoomReset(t);
      if (state.selectedIso || state.selectedPolityId) updateSelectionTip();
    });

  state.zoom = zoom;
  svg.call(zoom);
  // Double-click zoom fights accidental country taps on phones
  svg.on("dblclick.zoom", null);

  const restore =
    savedZoom != null
      ? d3.zoomIdentity.translate(savedZoom.x, savedZoom.y).scale(savedZoom.k)
      : d3.zoomIdentity;
  svg.call(zoom.transform, restore);
  state.savedZoom =
    restore.k !== 1 || restore.x || restore.y
      ? { k: restore.k, x: restore.x, y: restore.y }
      : null;
  syncZoomReset(restore);

  paintMap(false);
}

/** True when the map is zoomed/panned away from the default framing. */
function mapGestureEngaged(transform) {
  const t = transform || (state.svg ? d3.zoomTransform(state.svg.node()) : null);
  if (!t) return false;
  return (
    Math.abs(t.k - 1) > 0.03 || Math.abs(t.x) > 4 || Math.abs(t.y) > 4
  );
}

function syncZoomReset(transform) {
  const btn = $("#btn-zoom-reset");
  if (!btn || !transform) return;
  const zoomed = mapGestureEngaged(transform);
  btn.hidden = !zoomed;
  // At default framing, allow page scroll through the map; once engaged,
  // capture pan/pinch/wheel so the map moves instead of the page.
  const mapEl = $("#map");
  if (mapEl) mapEl.classList.toggle("is-map-engaged", zoomed);
}

function resetMapZoom() {
  if (!state.svg || !state.zoom) return;
  state.savedZoom = null;
  state.svg
    .transition()
    .duration(motionMs(320))
    .ease(d3.easeCubicOut)
    .call(state.zoom.transform, d3.zoomIdentity);
}

function bumpMapZoom(factor) {
  if (!state.svg || !state.zoom) return;
  state.svg
    .transition()
    .duration(motionMs(220))
    .ease(d3.easeCubicOut)
    .call(state.zoom.scaleBy, factor);
}

/** Approximate spherical area — used to stack small polities above empires. */
function featureArea(f) {
  try {
    return Math.abs(d3.geoArea(f));
  } catch (_) {
    return 0;
  }
}

/** Large first in DOM (behind); small last (on top / clickable). */
function sortFeaturesSmallOnTop(features) {
  return [...features].sort((a, b) => featureArea(b) - featureArea(a));
}

/**
 * Pick polity under a pointer: smallest containing geometry wins.
 * Repeat-click cycles through overlapping stack (small → larger → …).
 */
function pickPolityAtEvent(event, fallbackId = null) {
  if (!state.path || !state.zoomLayer) return fallbackId;
  const layer = state.zoomLayer.node();
  if (!layer) return fallbackId;
  const proj = state.path.projection?.();
  if (!proj?.invert) return fallbackId;

  const [x, y] = d3.pointer(event, layer);
  const lonlat = proj.invert([x, y]);
  if (!lonlat || !Number.isFinite(lonlat[0]) || !Number.isFinite(lonlat[1])) {
    return fallbackId;
  }

  const period = currentPeriod();
  const features = kingdomGeoSmoothed(period)?.features || [];
  const hits = features.filter((f) => {
    try {
      return d3.geoContains(f, lonlat);
    } catch (_) {
      return false;
    }
  });
  if (!hits.length) return fallbackId;

  hits.sort((a, b) => featureArea(a) - featureArea(b)); // smallest first

  if (hits.length > 1 && state.selectedPolityId) {
    const idx = hits.findIndex(
      (h) => h.properties.polityId === state.selectedPolityId
    );
    if (idx >= 0) {
      return hits[(idx + 1) % hits.length].properties.polityId;
    }
  }
  return hits[0].properties.polityId;
}

/** Bind / update polity paths only when the kingdom tick changes. */
function syncKingdomPolityLayer({ force = false } = {}) {
  if (!state.svg || !state.path || !isKingdomMode()) return;
  const period = currentPeriod();
  const periodId = period?.id || "";
  if (!force && state._kingdomGeoPeriodId === periodId) {
    applyPolitySelectionClass();
    return;
  }
  state._kingdomGeoPeriodId = periodId;

  const polityGeo = kingdomGeoSmoothed(period);
  const features = sortFeaturesSmallOnTop(polityGeo?.features || []);
  const pg = state.svg.select("g.polities");
  if (pg.empty()) return;

  pg.selectAll("path.polity")
    .data(features, (d) => d.properties.polityId)
    .join(
      (enter) =>
        enter
          .append("path")
          .attr("class", "polity")
          .attr("d", state.path)
          .attr("data-polity", (d) => d.properties.polityId)
          .attr("data-name", (d) => d.properties.name)
          .style("pointer-events", "all")
          .on("pointerenter", onPolityEnter)
          .on("pointermove", onPolityMove)
          .on("pointerleave", onPolityLeave)
          .on("pointerdown", onPolityPointerDown)
          .on("pointerup", onPolityPointerUp)
          .on("click", onPolityClick),
      (update) =>
        update
          .attr("d", state.path)
          .attr("data-polity", (d) => d.properties.polityId)
          .attr("data-name", (d) => d.properties.name)
          .style("pointer-events", "all"),
      (exit) => exit.remove()
    );

  // Re-assert paint order: empires under duchies (selection must not steal z-order)
  pg.selectAll("path.polity")
    .datum((d) => d)
    .sort((a, b) => featureArea(b) - featureArea(a));

  const bg = state.svg.select("g.polity-borders");
  if (!bg.empty()) {
    const lines = period?.v2
      ? [
          { k: "border", g: period.borders },
        ].filter((d) => d.g && d.g.coordinates?.length)
      : [];
    bg.selectAll("path")
      .data(lines, (d) => d.k)
      .join("path")
      .attr("class", (d) => `polity-${d.k}`)
      .attr("d", (d) => state.path(d.g));
  }
  state.svg.select("g.polities").classed("is-v2", Boolean(period?.v2));
  // v2 geometry is pre-clipped to land in the build; the per-country clipPath
  // would re-open hairline seams between Natural Earth countries, so drop it.
  state.svg.selectAll("g.polities, g.polity-borders")
    .attr("clip-path", period?.v2 ? null : "url(#polity-clip)");
  state.svg.select("g.polities")
    .selectAll("path.polity")
    .classed("is-extra", (d) => Boolean(d.properties.extra));

  // Drop selection only when the polity is gone from this tick entirely
  if (state.selectedPolityId) {
    const hasGeom = features.some(
      (f) => f.properties.polityId === state.selectedPolityId
    );
    const hasPanel = Boolean(period?.polities?.[state.selectedPolityId]);
    if (!hasGeom && !hasPanel) state.selectedPolityId = null;
  }
  applyPolitySelectionClass();
}

function applyPolitySelectionClass() {
  if (!state.svg) return;
  const pg = state.svg.select("g.polities");
  if (pg.empty()) return;
  pg.selectAll("path.polity").classed(
    "is-active",
    (d) => d.properties.polityId === state.selectedPolityId
  );
  // Do NOT raise selected — that buried smaller kingdoms under HRE/etc.
}

function selectPolity(polityId, { scrollDetail = false } = {}) {
  if (!polityId) return;
  state.selectedPolityId = polityId;
  state.selectedIso = null;
  state.svg?.selectAll("path.country").classed("is-active", false);
  // Interrupt fill transitions so selection isn't eaten mid-tween
  state.svg?.selectAll("path.polity").interrupt();
  applyPolitySelectionClass();
  renderDetail();
  highlightCultureChips();
  updateSelectionTip();
  renderKeyEvents();
  if (scrollDetail) {
    requestAnimationFrame(() => {
      $("#detail")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
}

/** Clear the kingdom-mode place selection (hides Key events again). */
function clearPolitySelection() {
  if (!isKingdomMode() || !state.selectedPolityId) return;
  state.selectedPolityId = null;
  applyPolitySelectionClass();
  renderDetail();
  highlightCultureChips();
  updateSelectionTip();
  renderKeyEvents();
}

/** Deep-time period nearest the slider (same switch point as the culture labels). */
function nearestDeepPeriod(pos = state.sliderPos) {
  const periods = state.data?.periods || [];
  if (!periods.length) return null;
  return periods[Math.min(periods.length - 1, Math.max(0, Math.round(pos * (periods.length - 1))))];
}

/** Projected SVG path for the partial-fill outline of iso in period, or null if filled whole. */
function fillExtentPath(iso, period) {
  const ring = state.data?.meta?.fillExtents?.countries?.[iso]?.[period?.id];
  if (!Array.isArray(ring) || ring.length < 4 || !state.path) return null;
  let poly = { type: "Polygon", coordinates: [ring] };
  // d3-geo treats rings by winding; flip if this one came out as "the rest of the globe"
  if (d3.geoArea(poly) > 2 * Math.PI) poly = { type: "Polygon", coordinates: [ring.slice().reverse()] };
  return state.path(poly);
}

function paintMap(animate = true) {
  if (!state.svg) return;

  if (isKingdomMode()) {
    // Modern country basemap stays land-colored; polities carry fills.
    state.svg
      .selectAll("path.country")
      .style("fill", null)
      .style("fill-opacity", 1);
    state.svg.selectAll("path.country-extent").interrupt().classed("is-extent-on", false).style("fill-opacity", 0);

    // Geometry only when tick changes — avoids selection flicker on slider drag
    syncKingdomPolityLayer({ force: false });

    state.svg.selectAll("path.polity").each(function (d) {
      const polityId = d.properties.polityId;
      const style = interpolatedPolityStyle(polityId, state.sliderPos);
      const node = d3.select(this);
      const fill = style.fill || "transparent";
      // Keep fills translucent so Natural Earth coasts read through
      const v2 = Boolean(currentPeriod()?.v2);
      const opacity = style.fill
        ? v2
          ? 1
          : Math.min(0.62, Math.max(0.32, style.opacity * 0.78))
        : 0;
      const visible = Boolean(style.fill);
      // Keep hit targets even while fill tweens between ticks
      node.style("pointer-events", "all");
      if (animate) {
        node
          .transition()
          .duration(motionMs(280))
          .ease(d3.easeCubicOut)
          .style("fill", fill)
          .style("fill-opacity", opacity)
          .style("stroke-opacity", visible ? null : 0);
      } else {
        node
          .style("fill", fill)
          .style("fill-opacity", opacity)
          .style("stroke-opacity", visible ? null : 0);
      }
    });
    applyPolitySelectionClass();
    applyLegendFocus();
    return;
  }

  const paths = state.svg.selectAll("path.country");
  const period = nearestDeepPeriod();
  const setFill = (node, fill, opacity) => {
    if (animate) {
      node
        .transition()
        .duration(motionMs(420))
        .ease(d3.easeCubicOut)
        .style("fill", fill)
        .style("fill-opacity", opacity);
    } else {
      node.interrupt().style("fill", fill).style("fill-opacity", opacity);
    }
  };
  paths.each(function (d) {
    const iso = d.properties.iso;
    const style = interpolatedCountryStyle(iso, state.sliderPos);
    const node = d3.select(this);
    const fill = style.fill || "var(--land-base)";
    const opacity = style.fill ? Math.max(0.35, style.opacity) : 1;
    const overlay = state.svg.select(`path.country-extent[data-iso="${iso}"]`);
    const clipD = style.fill ? fillExtentPath(iso, period) : null;
    if (clipD && !overlay.empty()) {
      // Culture covers only part of this modern country: plain land underneath,
      // culture colour on the clipped overlay.
      state.svg.select(`#extent-clip-${iso} path`).attr("d", clipD);
      setFill(node, "var(--land-base)", 1);
      overlay.classed("is-extent-on", true);
      setFill(overlay, fill, opacity);
    } else {
      if (!overlay.empty()) overlay.classed("is-extent-on", false);
      if (!overlay.empty()) setFill(overlay, fill, 0);
      setFill(node, fill, opacity);
    }
  });
  applyLegendFocus();
}

function culturesForIso(iso) {
  const style = interpolatedCountryStyle(iso, state.sliderPos);
  const labels = (style.labels || []).map((l) => l.label).filter(Boolean);
  return labels;
}

function culturesForPolity(polityId) {
  const style = interpolatedPolityStyle(polityId, state.sliderPos);
  return style.label ? [style.label] : [];
}

function tipHtml(name, cultures) {
  const filtered = (cultures || []).filter(
    (c) => c && c.toLowerCase() !== String(name || "").toLowerCase()
  );
  const line = filtered.length ? filtered.join(" · ") : "";
  if (!line) {
    return `<strong>${escapeHtml(name)}</strong>`;
  }
  return `<strong>${escapeHtml(name)}</strong><span class="map-tip-cultures">${escapeHtml(line)}</span>`;
}

/** Pin tip on selected country/polity; culture line follows the slider. */
function updateSelectionTip() {
  if (!state.tip || !state.svg) return;

  if (isKingdomMode()) {
    if (!state.selectedPolityId) {
      state.tip.style("opacity", 0);
      return;
    }
    const feat = kingdomGeoSmoothed(currentPeriod())?.features?.find(
      (f) => f.properties.polityId === state.selectedPolityId
    );
    if (!feat) {
      state.tip.style("opacity", 0);
      return;
    }
    const cultures = culturesForPolity(state.selectedPolityId);
    state.tip
      .style("opacity", 1)
      .classed("is-pinned", true)
      .html(tipHtml(feat.properties.name, cultures));
    if (state.path) {
      try {
        const c = state.path.centroid(feat);
        if (Number.isFinite(c[0]) && Number.isFinite(c[1])) {
          const t = d3.zoomTransform(state.svg.node());
          const [x, y] = t.apply(c);
          state.tip.style("left", `${x}px`).style("top", `${y}px`);
        }
      } catch (_) {
        /* centroid can fail on empty clips */
      }
    }
    return;
  }

  if (!state.selectedIso || !state.geo) return;
  const feat = state.geo.features.find(
    (f) => f.properties.iso === state.selectedIso
  );
  if (!feat) {
    state.tip.style("opacity", 0);
    return;
  }
  const cultures = culturesForIso(state.selectedIso);
  state.tip
    .style("opacity", 1)
    .classed("is-pinned", true)
    .html(tipHtml(feat.properties.name, cultures));

  if (state.path) {
    try {
      const c = state.path.centroid(feat);
      if (Number.isFinite(c[0]) && Number.isFinite(c[1])) {
        const t = d3.zoomTransform(state.svg.node());
        const [x, y] = t.apply(c);
        state.tip.style("left", `${x}px`).style("top", `${y}px`);
      }
    } catch (_) {
      /* centroid can fail on empty clips */
    }
  }
}

/** Keep detail horizon in sync while the slider moves (selected country). */
function updateSelectedHorizonLive() {
  if (isKingdomMode()) {
    if (!state.selectedPolityId) return;
    const cultures = culturesForPolity(state.selectedPolityId);
    const title = $("#culture-title");
    if (title && cultures.length) title.textContent = cultures.join(" · ");
    const horizonEl = $("#culture-horizon");
    if (horizonEl) horizonEl.textContent = "Kingdom / empire";
    return;
  }

  if (!state.selectedIso) return;
  const cultures = culturesForIso(state.selectedIso);
  const title = $("#culture-title");
  if (title && cultures.length) {
    title.textContent = cultures.join(" · ");
  }
  const horizonEl = $("#culture-horizon");
  if (horizonEl) {
    const period = currentPeriod();
    const region = state.selectedRegion
      ? regionData(period, state.selectedRegion)
      : null;
    const base = region?.culture || "";
    horizonEl.textContent =
      cultures.length && base && cultures[0] !== base
        ? `Regional horizon · ${base}`
        : cultures.length
          ? "Map layers here"
          : "Cultural horizon";
  }
}

function onPolityEnter(event, d) {
  d3.select(this).classed("is-hover", true);
  const polityId = d.properties.polityId;
  const cultures = culturesForPolity(polityId);
  state.tip
    .style("opacity", 1)
    .classed("is-pinned", polityId === state.selectedPolityId)
    .html(tipHtml(d.properties.name, cultures));
}

function onPolityMove(event) {
  if (
    state.selectedPolityId &&
    d3.select(this).datum()?.properties?.polityId === state.selectedPolityId
  ) {
    updateSelectionTip();
    return;
  }
  const mapEl = $("#map");
  if (!mapEl) return;
  const stage = mapEl.getBoundingClientRect();
  state.tip
    .style("left", `${event.clientX - stage.left}px`)
    .style("top", `${event.clientY - stage.top}px`);
}

function onPolityLeave() {
  d3.select(this).classed("is-hover", false);
  if (state.selectedPolityId) updateSelectionTip();
  else state.tip.style("opacity", 0).classed("is-pinned", false);
}

function onPolityPointerDown(event, d) {
  if (event.button != null && event.button !== 0) return;
  d3.select(this).interrupt();
  state._polityPointerDown = {
    id: d.properties.polityId,
    x: event.clientX,
    y: event.clientY,
  };
}

function onPolityPointerUp(event, d) {
  const down = state._polityPointerDown;
  state._polityPointerDown = null;
  if (!down) return;
  if (event.button != null && event.button !== 0) return;
  const dx = Math.abs((event.clientX || 0) - down.x);
  const dy = Math.abs((event.clientY || 0) - down.y);
  if (dx > 10 || dy > 10) return; // treat as pan/drag
  event.preventDefault();
  event.stopPropagation();
  const id = pickPolityAtEvent(event, d.properties.polityId);
  selectPolity(id);
}

function onPolityClick(event, d) {
  // Fallback when pointerup didn't fire (some desktop paths)
  event.preventDefault();
  event.stopPropagation();
  const id = pickPolityAtEvent(event, d.properties.polityId);
  selectPolity(id);
}

function onCountryEnter(event, d) {
  if (isKingdomMode()) return;
  d3.select(this).classed("is-hover", true);
  const iso = d.properties.iso;
  // Hovering another country: temporary tip; selected tip resumes on leave
  const cultures = culturesForIso(iso);
  state.tip
    .style("opacity", 1)
    .classed("is-pinned", iso === state.selectedIso)
    .html(tipHtml(d.properties.name, cultures));
}

function onCountryMove(event) {
  if (state.selectedIso && d3.select(this).datum()?.properties?.iso === state.selectedIso) {
    // Keep pinned tip on the selected country's centroid while sliding/zooming
    updateSelectionTip();
    return;
  }
  const mapEl = $("#map");
  if (!mapEl) return;
  const stage = mapEl.getBoundingClientRect();
  state.tip
    .style("left", `${event.clientX - stage.left}px`)
    .style("top", `${event.clientY - stage.top}px`);
}

function onCountryLeave() {
  d3.select(this).classed("is-hover", false);
  if (state.selectedIso) updateSelectionTip();
  else state.tip.style("opacity", 0).classed("is-pinned", false);
}

function onCountryClick(event, d) {
  if (isKingdomMode()) return;
  const iso = d.properties.iso;
  state.selectedIso = iso;
  state.selectedPolityId = null;
  state.selectedCultureLayer = null;
  const rid = isoToRegion(iso);
  if (rid) state.selectedRegion = rid;

  state.svg.selectAll("path.country").classed("is-active", false);
  d3.select(this).classed("is-active", true);

  renderDetail();
  highlightCultureChips();
  updateSelectionTip();
}

/* ——— UI ——— */

function setSliderPos(pos, { fromSlider = false } = {}) {
  state.sliderPos = Math.max(0, Math.min(1, pos));
  const idx = periodIndexFromSlider(state.sliderPos);
  const periodChanged = idx !== state.periodIndex;
  state.periodIndex = idx;

  const slider = $("#time-slider");
  if (!fromSlider) slider.value = String(Math.round(state.sliderPos * SLIDER_MAX));
  const pct = `${state.sliderPos * 100}%`;
  slider.style.setProperty("--slider-pct", pct);
  slider.parentElement?.style.setProperty("--slider-pct", pct);

  paintMap(true);
  if (periodChanged) {
    renderPeriodText();
    updateLegend();
    updateCulturesRail();
    renderDetail();
    highlightCultureChips();
  } else {
    // soft update year blend feel — still show nearest period text
    renderPeriodText();
  }

  // Selected country / polity groups follow the slider continuously
  if (state.selectedIso || state.selectedPolityId) {
    updateSelectionTip();
    updateSelectedHorizonLive();
  }

  $$(".ticks .tick-mark-btn").forEach((el) => {
    el.classList.toggle("is-active", Number(el.dataset.i) === state.periodIndex);
  });
  $$(".ticks .tick-label").forEach((el) => {
    el.classList.toggle("is-active", Number(el.dataset.i) === state.periodIndex);
  });
  updateTickCaption();
}

function updateTickCaption() {
  const el = $("#tick-caption");
  if (!el) return;
  const period = currentPeriod();
  el.textContent = period ? shortPeriodName(period) : "";
}

function snapToPeriod(index) {
  const n = activePeriods().length;
  const pos = n <= 1 ? 0 : index / (n - 1);
  setSliderPos(pos);
}

function formatYearUi(s) {
  // Prefer BC / AD in the UI (data may still say BCE / CE)
  return String(s || "")
    .replace(/\bBCE\b/g, "BC")
    .replace(/\bCE\b/g, "AD");
}

/** Year window [lo, hi] represented by the current slider stop. */
function currentTimeWindow() {
  const periods = activePeriods();
  const i = state.periodIndex;
  const p = periods[i];
  if (!p) return null;
  const y = Number(p.yearApprox);
  const prev = periods[i - 1] ? Number(periods[i - 1].yearApprox) : null;
  const next = periods[i + 1] ? Number(periods[i + 1].yearApprox) : null;
  const lo = prev != null ? (prev + y) / 2 : y - 50;
  const hi = next != null ? (y + next) / 2 : Math.max(y + 50, new Date().getFullYear());
  return { lo, hi };
}

/** Atlas region for the current place selection (null = whole map). */
function currentPlaceRegion() {
  if (!isKingdomMode()) {
    if (state.selectedIso) return isoToRegion(state.selectedIso);
    return state.selectedRegion || null;
  }
  if (!state.selectedPolityId) return null;
  try {
    const feat = kingdomGeoSmoothed(currentPeriod())?.features?.find(
      (f) => f.properties.polityId === state.selectedPolityId
    );
    if (!feat || !state.geo) return null;
    const c = d3.geoCentroid(feat);
    const hit = state.geo.features.find((f) => d3.geoContains(f, c));
    return hit ? isoToRegion(hit.properties.iso) : null;
  } catch (_) {
    return null;
  }
}

/** Key events for the selected time (slider stop) and place (region). */
function currentKeyEvents() {
  const periods = state.keyEvents?.periods || {};
  let pool;
  if (!isKingdomMode()) {
    pool = periods[currentPeriod()?.id]?.keyEvents || [];
  } else {
    const w = currentTimeWindow();
    pool = w
      ? Object.values(periods)
          .flatMap((p) => p.keyEvents || [])
          .filter((e) => e.start != null && e.end >= w.lo && e.start < w.hi)
      : [];
  }
  const region = currentPlaceRegion();
  // Place-only: no Europe-wide fallback; nothing without a selected place
  const list = region ? pool.filter((e) => (e.regions || []).includes(region)) : [];
  const seen = new Set();
  return list
    .filter((e) => {
      const k = `${e.date}|${e.title}`;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    })
    .sort((a, b) => (a.start ?? 0) - (b.start ?? 0) || (a.end ?? 0) - (b.end ?? 0));
}

const REGION_LABELS = {
  iberia: "Iberia",
  britain: "Britain & Ireland",
  france: "France",
  central: "Central Europe",
  scandinavia: "Scandinavia",
  italy: "Italy",
  balkans: "Balkans",
  eastern: "Eastern Europe",
};

function renderKeyEventsList(listEl, events) {
  if (!listEl) return;
  listEl.replaceChildren();
  for (const ev of events) {
    const li = document.createElement("li");
    li.className = "key-events-item";
    const details = document.createElement("details");
    details.className = "key-events-disclosure";
    const summary = document.createElement("summary");
    summary.className = "key-events-summary";
    if (ev.date) {
      const when = document.createElement("time");
      when.className = "key-events-date";
      when.textContent = formatYearUi(ev.date);
      summary.appendChild(when);
      summary.appendChild(document.createTextNode(": "));
    }
    const title = document.createElement("span");
    title.className = "key-events-teaser";
    title.textContent = ev.title || "";
    summary.appendChild(title);
    details.appendChild(summary);
    if (ev.detail) {
      const body = document.createElement("div");
      body.className = "key-events-body";
      const para = document.createElement("p");
      para.textContent = ev.detail;
      body.appendChild(para);
      details.appendChild(body);
    }
    li.appendChild(details);
    listEl.appendChild(li);
  }
}

function renderKeyEvents() {
  const section = $("#key-events");
  const listEl = $("#key-events-list");
  if (!section || !listEl || !state.data) return;
  const period = currentPeriod();
  const region = currentPlaceRegion();
  const placeSelected = isKingdomMode()
    ? Boolean(state.selectedPolityId)
    : Boolean(state.selectedIso || state.selectedRegion);
  if (!placeSelected) {
    section.hidden = true;
    listEl.innerHTML = "";
    return;
  }
  const events = currentKeyEvents();
  const ctx = $("#key-events-context");
  if (ctx) {
    const when = period ? shortPeriodName(period) : "";
    const where = region ? REGION_LABELS[region] || region : "";
    ctx.textContent = [when, where].filter(Boolean).join(" · ");
  }
  const empty = $("#key-events-empty");
  renderKeyEventsList(listEl, events);
  listEl.hidden = !events.length;
  if (empty) empty.hidden = events.length > 0;
  section.hidden = false;
}

/** Display title for the era block (tick-specific when authored). */
function periodDisplayTitle(period) {
  if (!period) return "—";
  // Kingdom + deep-time: prefer the period/tick label (e.g. "Westphalia", "Migration Period")
  const titled = String(period.label || "").trim();
  if (titled) return titled;
  if (isKingdomMode()) {
    const pack = activePack();
    return pack?.label || KINGDOM_TAB_LABELS[state.atlasMode] || period.era || "—";
  }
  return period.era || "—";
}

/** Short thematic eyebrow under the era title; hide if it only repeats the title. */
function periodEyebrowText(period) {
  if (!period) return "";
  const title = periodDisplayTitle(period).trim();
  const era = String(period.era || "").trim();
  if (era && era.toLowerCase() !== title.toLowerCase()) return era;
  const note = String(period.culturesNote || "").trim();
  if (note && note.toLowerCase() !== title.toLowerCase()) {
    return note.split(/[.—]/)[0].trim() || note;
  }
  if (isKingdomMode()) {
    const y = formatYearUi(period.tickYear || period.yearLabel);
    const pack = activePack();
    const tab = pack?.label || KINGDOM_TAB_LABELS[state.atlasMode] || "";
    if (tab && y) return `${tab} · ${y}`;
    return y ? `Schematic polities · ${y}` : "";
  }
  return "";
}

function renderPeriodText() {
  const period = currentPeriod();
  const yearEl = $("#period-year");
  const labelEl = $("#period-label");
  const titleEl = $("#period-title");
  const eraEl = $("#period-era");
  if (!period) {
    if (yearEl) yearEl.textContent = "—";
    if (labelEl) labelEl.textContent = "—";
    if (titleEl) titleEl.textContent = "—";
    if (eraEl) {
      eraEl.textContent = "";
      eraEl.hidden = true;
    }
    return;
  }
  if (yearEl) yearEl.textContent = formatYearUi(period.tickYear || period.yearLabel);
  if (labelEl) labelEl.textContent = period.label;
  const title = periodDisplayTitle(period);
  if (titleEl) titleEl.textContent = title;
  const eyebrow = periodEyebrowText(period);
  if (eraEl) {
    eraEl.textContent = eyebrow;
    eraEl.hidden = !eyebrow;
  }
  $("#period-copy").textContent = period.narrative;
  const ling = $("#period-ling");
  if (period.linguistics) {
    ling.hidden = false;
    ling.textContent = period.linguistics;
  } else {
    ling.hidden = true;
  }
  renderKeyEvents();
}

/** Culture-family headings for the map key. First match wins. */
const CULTURE_FAMILY_RULES = [
  ["Bell Beaker", /\bbell beaker\b|\bbeaker\b/i],
  ["Corded Ware", /corded ware|single grave|battle axe/i],
  ["Steppe", /yamnaya|catacomb|srubnaya|andronovo|usatove|serednii|scythian|sauromatian|sarmatian|khazar|golden horde|hunnic/i],
  ["Northern foragers", /maglemos|kongemose|erteb|fosna|hensbacka|komsa|pitted ware/i],
  ["Western foragers", /azilian|tardenois|sauveter|british mesolithic/i],
  ["Mediterranean foragers", /epigravett|iron gates|balkan mesolithic/i],
  ["Eastern foragers", /kunda|\bnarva\b|veretye|ukrainian meso|comb ware|\behg\b|forest-steppe/i],
  ["Foragers", /mesolithic|forager|hunter-gather/i],
  ["Balkans", /balkan|vu[cč]edol|vin[cč]a|star[cč]evo|k[oö]r[oö]s|cri[sș]|karanovo|trypillia|cucuteni|thracian|illyrian|otomani|f[uü]zesabony|mycenaean|serbia|bulgaria|romania/i],
  ["Neolithic farmers", /cardial|impresso|impressed|\blbk\b|linear pottery|funnelbeaker|\btrb\b|michelsberg|chass[eé]en|megalith|globular amphora|neolithic|bug[–-]dniester|tiszapolg/i],
  ["Bronze Age", /bronze|\bnba\b|tumulus|el argar|terramare|apennine|wessex \/ british/i],
  ["Celtic", /hallstatt|la t[eè]ne|\bceltic\b|celtiberian/i],
  ["Iberia", /iberian|lusitanian|hispania|castile|aragon|\bportugal\b|portuguese|nasrid|andalus|asturias|granada|\bspain\b|spanish|los millares/i],
  ["Italy", /etruscan|\bitalia\b|\bitaly\b|latin \/|early rome|venice|papal|savoy|sicil|lombard|remedello|gaudo|communal italy/i],
  ["Aegean", /greek|greece|achaea|byzantine|ottoman|asia minor|turkey/i],
  ["Germanic", /frank|alamann|anglo-saxon|wielbark|chernyakhov|ostrogoth|visigoth|vandal|germanic|jastorf|danelaw|wessex|norman|carolingian|francia|burgund/i],
  ["Slavic & Baltic", /slavic|kievan|\brus\b|moravia|piast|poland|muscov|novgorod|vladimir|galicia|volhynia|lithuania|bohemia|teutonic|baltic|ukraine|belarus/i],
  ["Nordic", /nordic|scandinav|denmark|norway|sweden|danish|norwegian|swedish|kalmar|iceland|finland/i],
  ["Britain & Ireland", /british|britain|britannia|england|scotland|wales|welsh|ireland|irish|gaelic|hibernia|plantagenet|tudor|lancastrian|united kingdom/i],
  ["Western Europe", /\bfrance\b|\bgaul\b|gallia|benelux|dutch|low countries|swiss|\bgerman\b|germany|\bhabsburg\b|austria|holy roman|\bhre\b/i],
];

function cultureFamily(layer) {
  const text = `${layer?.id || ""} ${layer?.label || ""}`;
  for (const [name, re] of CULTURE_FAMILY_RULES) {
    if (re.test(text)) return name;
  }
  return "";
}

function groupLegendLayers(layers) {
  const buckets = new Map();
  const order = [];
  for (const layer of layers) {
    const family = cultureFamily(layer);
    const key = family || "__other";
    if (!buckets.has(key)) {
      buckets.set(key, []);
      order.push(key);
    }
    buckets.get(key).push(layer);
  }
  const named = order.filter((key) => key !== "__other");
  if (!named.length) return [{ family: "", layers }];
  const groups = named.map((key) => ({ family: key, layers: buckets.get(key) }));
  const loose = buckets.get("__other") || [];
  if (loose.length) groups.push({ family: loose.length > 1 ? "Other" : "", layers: loose });
  return groups;
}

function legendLayerId(layer) {
  return layerPolityId(layer) || layer?.id || "";
}

function legendLayers() {
  return (currentPeriod()?.mapLayers || []).filter((l) => !l.extra);
}

function legendRowHtml(layer) {
  const id = legendLayerId(layer);
  return `<button type="button" class="legend-row" data-layer="${escapeHtml(id)}" aria-pressed="false"><span class="legend-swatch" style="background:${safeColor(layer.color)}"></span><span class="legend-label">${escapeHtml(layer.label)}</span></button>`;
}

function updateLegend() {
  const layers = legendLayers();
  const box = $("#map-legend");
  if (!box) return;
  // Always visible under the slider — never overlays the map
  box.hidden = false;
  const ids = new Set(layers.map((l) => legendLayerId(l)));
  if (state.legendPinId && !ids.has(state.legendPinId)) state.legendPinId = null;
  state.legendHoverId = null;
  box.innerHTML = groupLegendLayers(layers)
    .map((group) => {
      const rows = group.layers.map(legendRowHtml).join("");
      if (!group.family) return `<div class="legend-group">${rows}</div>`;
      return `<div class="legend-group" role="group" aria-label="${escapeHtml(group.family)}"><p class="legend-family">${escapeHtml(group.family)}</p>${rows}</div>`;
    })
    .join("");
  applyLegendFocus();
  const pack = activePack();
  const attr = $("#map-attr");
  if (attr) {
    const base = isKingdomMode()
      ? pack?.mapAttribution || state.data?.meta?.mapAttribution || ""
      : state.data?.meta?.mapAttribution || "";
    attr.textContent = base;
    if (isKingdomMode() && currentPeriod()?.approxTick) {
      const note = document.createElement("span");
      note.className = "approx-note";
      note.textContent = " · approx. borders";
      attr.appendChild(note);
    }
  }
}

function glossaryIdForAncestryKey(id) {
  return id === "steppe" ? "wsh" : id;
}

/** Genetic Terms — include contextual Other when the active mix has other > 0. */
function renderGlossary(activeEntries) {
  const grid = $("#glossary-grid");
  if (!grid) return;
  const base = state.data.meta.glossary || [];
  const keys = state.data.meta.ancestryKeys || [];
  const otherKey = keys.find((k) => k.id === "other");
  const byId = new Map(base.map((g) => [g.id, { ...g }]));

  const otherEntry = (activeEntries || []).find(
    (e) => e.id === "other" && (e.value > 0 || e.rangeLabel)
  );
  if (otherEntry || otherKey) {
    byId.set("other", {
      id: "other",
      term: "Other",
      name:
        otherEntry?.full ||
        otherKey?.full ||
        "Residual / unmodeled components",
      text:
        otherEntry?.detail ||
        otherKey?.detail ||
        "Residual ancestry outside the main WHG–EEF–WSH components: eastern Mediterranean, East Eurasian, North African, CHG/Iran-related, or poorly resolved inputs depending on period and place.",
    });
  }

  let items = base.map((g) => byId.get(g.id) || g);
  if (byId.has("other") && !items.some((g) => g.id === "other")) {
    items = items.concat([byId.get("other")]);
  } else if (otherEntry) {
    items = items.map((g) => (g.id === "other" ? byId.get("other") : g));
  }

  // When a place mix is active, surface present components first (Other included).
  if (activeEntries?.length) {
    const present = [];
    const seen = new Set();
    for (const e of activeEntries) {
      const gid = glossaryIdForAncestryKey(e.id);
      const g = byId.get(gid) || byId.get(e.id);
      if (!g || seen.has(g.id)) continue;
      seen.add(g.id);
      present.push(g);
    }
    for (const g of items) {
      if (!seen.has(g.id)) present.push(g);
    }
    items = present;
  }

  grid.innerHTML = items
    .map(
      (g) =>
        `<dl class="glossary-item${
          otherEntry && g.id === "other" ? " glossary-item--active" : ""
        }"><dt><a class="glossary-link" href="ancestry.html#${escapeHtml(
          g.id
        )}">${escapeHtml(g.term)}</a> <span>· ${escapeHtml(
          g.name
        )}</span></dt><dd>${escapeHtml(g.text)}</dd></dl>`
    )
    .join("");
}

function updateCulturesRail() {
  const period = currentPeriod();
  const layers = (period?.mapLayers || []).filter((l) => !l.extra);
  const rail = $("#cultures-rail");
  if (!rail) return;
  rail.innerHTML = layers
    .map((l) => {
      const id = layerPolityId(l) || l.id || "";
      return `<button type="button" class="culture-chip" data-layer="${escapeHtml(id)}">${escapeHtml(l.label)}</button>`;
    })
    .join("");
  rail.querySelectorAll(".culture-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      const layer = layers.find((l) => (layerPolityId(l) || l.id) === btn.dataset.layer);
      if (!layer) return;

      if (isKingdomMode()) {
        const polityId = layerPolityId(layer);
        if (!polityId) return;
        selectPolity(polityId, { scrollDetail: true });
        return;
      }

      if (!layer?.countries?.length) return;
      // Select first country of layer in a known region
      const iso = layer.countries.find((c) => isoToRegion(c));
      if (!iso) return;
      state.selectedIso = iso;
      state.selectedPolityId = null;
      state.selectedCultureLayer = layer.id || null;
      state.selectedRegion = isoToRegion(iso);
      state.svg
        ?.selectAll("path.country")
        .classed("is-active", (d) => d.properties.iso === iso);
      renderDetail();
      highlightCultureChips();
      updateSelectionTip();
    });
  });
}

function highlightCultureChips() {
  const period = currentPeriod();
  let ids = new Set();
  if (isKingdomMode()) {
    if (state.selectedPolityId) ids.add(state.selectedPolityId);
  } else {
    const iso = state.selectedIso;
    const style = iso ? countryStyleForPeriod(period, iso) : { labels: [] };
    ids = new Set((style.labels || []).map((l) => l.id));
  }
  $$(".culture-chip").forEach((chip) => {
    chip.classList.toggle("is-focus", ids.has(chip.dataset.layer));
  });
}

function setPolityField(key, value) {
  const block = $(`#polity-${key}-block`);
  const el = $(`#polity-${key}`);
  if (!block || !el) return;
  if (key === "story") {
    renderPolityStories(el, value);
    const has = !!(el.textContent || "").trim();
    block.hidden = !has;
    return;
  }
  const text = (value || "").trim();
  block.hidden = !text;
  setPlainText(el, text);
}

/** Parse story cards from arrays, plain prose, or stringified JSON/Python lists. */
function normalizeStoryItems(value) {
  if (value == null || value === "") return [];
  if (Array.isArray(value)) {
    const out = [];
    const seen = new Set();
    for (const item of value) {
      for (const piece of normalizeStoryItems(item)) {
        const key = `${piece.title}\0${piece.text}`;
        if (seen.has(key)) continue;
        seen.add(key);
        out.push(piece);
      }
    }
    return out;
  }
  if (typeof value === "object") {
    const title = String(value.title || value.name || "").trim();
    const text = String(
      value.text || value.body || value.narrative || value.description || ""
    ).trim();
    return title || text ? [{ title, text }] : [];
  }
  if (typeof value !== "string") return [];
  const raw = value.trim();
  if (!raw) return [];
  if (raw.startsWith("[")) {
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return normalizeStoryItems(parsed);
    } catch (_) {
      /* try Python-ish literal below */
    }
    const pyItems = parsePythonishStoryList(raw);
    if (pyItems.length) return pyItems;
  }
  return [{ title: "", text: raw }];
}

/** Best-effort parse of Python repr lists like [{'title': '...', 'text': '...'}]. */
function parsePythonishStoryList(raw) {
  const items = [];
  const re =
    /\{\s*['"]title['"]\s*:\s*(['"])([\s\S]*?)\1\s*,\s*['"]text['"]\s*:\s*(['"])([\s\S]*?)\3\s*\}/g;
  let m;
  while ((m = re.exec(raw))) {
    const title = m[2].replace(/\\'/g, "'").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
    const text = m[4].replace(/\\'/g, "'").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
    if (title || text) items.push({ title: title.trim(), text: text.trim() });
  }
  if (items.length) return items;
  // title/text key order swapped
  const re2 =
    /\{\s*['"]text['"]\s*:\s*(['"])([\s\S]*?)\1\s*,\s*['"]title['"]\s*:\s*(['"])([\s\S]*?)\3\s*\}/g;
  while ((m = re2.exec(raw))) {
    const text = m[2].replace(/\\'/g, "'").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
    const title = m[4].replace(/\\'/g, "'").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
    if (title || text) items.push({ title: title.trim(), text: text.trim() });
  }
  return items;
}

/** Render Stories & turning points as title + body cards — never String(array). */
function renderPolityStories(el, value) {
  if (!el) return;
  while (el.firstChild) el.removeChild(el.firstChild);
  const items = normalizeStoryItems(value);
  if (!items.length) return;

  // Single untitled prose blob → plain paragraphs (matches literature)
  if (items.length === 1 && !items[0].title) {
    items[0].text.split(/\n\n+/).forEach((para) => {
      const p = document.createElement("p");
      p.className = "story-item-text";
      p.textContent = para.trim();
      if (p.textContent) el.appendChild(p);
    });
    return;
  }

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "story-item";
    if (item.title) {
      const h = document.createElement("h4");
      h.className = "story-item-title";
      h.textContent = item.title;
      card.appendChild(h);
    }
    if (item.text) {
      item.text.split(/\n\n+/).forEach((para) => {
        const p = document.createElement("p");
        p.className = "story-item-text";
        p.textContent = para.trim();
        if (p.textContent) card.appendChild(p);
      });
    }
    el.appendChild(card);
  }
}

/** Join distinct prose blobs without dumping under a fake heading. */
function joinPolityProse(...parts) {
  const seen = new Set();
  const out = [];
  for (const p of parts) {
    const t = String(p || "").trim();
    if (!t || seen.has(t)) continue;
    seen.add(t);
    out.push(t);
  }
  return out.join("\n\n");
}

/** Prefer a dedicated field; optionally fall back to a bundled artIdeas blob split. */
function polityCultureField(polity, key) {
  if (!polity) return "";
  const direct = (polity[key] || "").trim();
  if (direct) return direct;
  if (key === "art" || key === "ideas") {
    const bundled = (polity.artIdeas || polity.artAndIdeas || "").trim();
    if (!bundled) return "";
    const parts = bundled.split(/\n\n+/).map((s) => s.trim()).filter(Boolean);
    if (key === "art") return parts[0] || "";
    if (parts.length > 1) return parts.slice(1).join("\n\n");
  }
  return "";
}

function applyCultureFields(polity) {
  setPolityField("art", polityCultureField(polity, "art"));
  setPolityField("ideas", polityCultureField(polity, "ideas"));
  setPolityField("philosophy", polityCultureField(polity, "philosophy"));
  setPolityField("science", polityCultureField(polity, "science"));
}

const DEEP_TIME_TEXT_KEYS = [
  "description",
  "summary",
  "narrative",
  "culture",
  "art",
  "ideas",
  "philosophy",
  "science",
  "leaders",
  "religion",
  "literature",
  "conflicts",
  "story",
];

/** Region-level culture / full packs keyed by atlas region. */
function regionCultureSlice(period, regionId) {
  const reg = regionData(period, regionId);
  if (!reg) return null;
  const slice = {};
  for (const key of DEEP_TIME_TEXT_KEYS) {
    const v = reg[key];
    if (typeof v === "string" && v.trim()) slice[key] = v.trim();
  }
  if (typeof reg.cultureLabel === "string" && reg.cultureLabel.trim()) {
    slice.cultureLabel = reg.cultureLabel.trim();
  }
  if (reg.stories != null) slice.stories = reg.stories;
  else if (reg.story != null) slice.stories = reg.story;
  if (Array.isArray(reg.images) && reg.images.length) slice.images = reg.images;
  if (Array.isArray(reg.vignettes) && reg.vignettes.length) {
    slice.stories = slice.stories || reg.vignettes;
  }
  return Object.keys(slice).length ? slice : null;
}

function pickLongestProse(...parts) {
  let best = "";
  for (const p of parts) {
    const t = String(p || "").trim();
    if (t.length > best.length) best = t;
  }
  return best;
}

/** Overlay region pack + optional focused layer onto a panel source object. */
function mergeDeepTimeCulture(polity, period) {
  const out = { ...(polity || {}) };
  const rid =
    state.selectedRegion || (state.selectedIso ? isoToRegion(state.selectedIso) : null);
  const regionSlice = rid ? regionCultureSlice(period, rid) : null;
  if (regionSlice) {
    for (const key of DEEP_TIME_TEXT_KEYS) {
      if (regionSlice[key]) {
        // Prefer longer authored pack prose over shorthand timeline stubs
        const cur = String(out[key] || "").trim();
        if (!cur || regionSlice[key].length >= cur.length) out[key] = regionSlice[key];
      }
    }
    if (regionSlice.stories != null) out.stories = regionSlice.stories;
    if (regionSlice.images) {
      out.images = mergeImageLists(out.images, regionSlice.images);
    }
  }
  const layerId = state.selectedCultureLayer;
  if (!layerId || !period) return out;
  const layer = (period.mapLayers || []).find((l) => l.id === layerId);
  if (!layer) return out;
  for (const key of ["art", "ideas", "philosophy", "science", "culture", "description"]) {
    const t = String(layer[key] || "").trim();
    if (t) out[key] = t;
  }
  if (layer.stories != null) out.stories = layer.stories;
  if (layer.story != null && out.stories == null) out.stories = layer.story;
  if (Array.isArray(layer.images) && layer.images.length) {
    out.images = mergeImageLists(out.images, layer.images);
  }
  return out;
}

function mergeImageLists(...lists) {
  const out = [];
  const seen = new Set();
  for (const list of lists) {
    if (!Array.isArray(list)) continue;
    for (const img of list) {
      if (!img || !img.src || seen.has(img.src)) continue;
      seen.add(img.src);
      out.push(img);
    }
  }
  return out.length ? out : null;
}

function deepTimePanelHasContent(source) {
  if (!source) return false;
  if (normalizeStoryItems(source.stories || source.story).length) return true;
  if (Array.isArray(source.images) && source.images.some((i) => i && i.src)) return true;
  return DEEP_TIME_TEXT_KEYS.some((k) => String(source[k] || "").trim());
}

/* Drop a gallery figure whose image fails to load (renamed/deleted on Commons).
   Image error events don't bubble, so listen in the capture phase. Replaces the
   old inline onerror attribute (CSP-friendly). scripts/check_images.py catches
   missing files before release. */
document.addEventListener(
  "error",
  (event) => {
    const img = event.target;
    if (!(img instanceof HTMLImageElement)) return;
    const fig = img.closest(".polity-figure");
    if (fig) fig.remove();
  },
  true
);

function figureHtml(img) {
  const alt = escapeHtml(img.alt || img.caption || "Historical image");
  const caption = escapeHtml(img.caption || "");
  const src = escapeHtml(img.src);
  return `<figure class="polity-figure">
    <button type="button" class="polity-figure-open" data-full-src="${src}" data-caption="${caption}" data-alt="${alt}" aria-label="View larger: ${alt}">
      <img src="${src}" alt="${alt}" loading="lazy" decoding="async" referrerpolicy="no-referrer" />
    </button>
    <figcaption>${caption}</figcaption>
  </figure>`;
}

/** Tag portrait vs landscape so CSS can shrink-wrap without wide grey slabs */
function bindFigureOrientation(root) {
  if (!root) return;
  root.querySelectorAll("figure.polity-figure img").forEach((img) => {
    const apply = () => {
      const fig = img.closest("figure.polity-figure");
      if (!fig || !img.naturalWidth) return;
      fig.dataset.orient =
        img.naturalWidth >= img.naturalHeight * 1.05 ? "landscape" : "portrait";
    };
    if (img.complete && img.naturalWidth) apply();
    else img.addEventListener("load", apply, { once: true });
  });
}

function ensureLightbox() {
  let root = $("#image-lightbox");
  if (root) return root;
  root = document.createElement("div");
  root.id = "image-lightbox";
  root.className = "image-lightbox";
  root.hidden = true;
  root.setAttribute("role", "dialog");
  root.setAttribute("aria-modal", "true");
  root.setAttribute("aria-label", "Image viewer");
  root.innerHTML = `
    <button type="button" class="image-lightbox-backdrop" aria-label="Close image"></button>
    <div class="image-lightbox-panel">
      <button type="button" class="image-lightbox-close" aria-label="Close">×</button>
      <img class="image-lightbox-img" alt="" />
      <p class="image-lightbox-caption"></p>
    </div>`;
  document.body.appendChild(root);

  const close = () => closeLightbox();
  root.querySelector(".image-lightbox-backdrop")?.addEventListener("click", close);
  root.querySelector(".image-lightbox-close")?.addEventListener("click", close);
  root.addEventListener("click", (e) => {
    if (e.target === root) close();
  });
  return root;
}

function openLightbox({ src, caption, alt }) {
  if (!src) return;
  const root = ensureLightbox();
  const img = root.querySelector(".image-lightbox-img");
  const cap = root.querySelector(".image-lightbox-caption");
  if (img) {
    img.src = src;
    img.alt = alt || caption || "Historical image";
  }
  if (cap) {
    cap.textContent = caption || alt || "";
    cap.hidden = !cap.textContent;
  }
  state._lightboxOpener = document.activeElement;
  root.hidden = false;
  document.body.classList.add("lightbox-open");
  root.querySelector(".image-lightbox-close")?.focus?.();
}

function closeLightbox() {
  const root = $("#image-lightbox");
  if (!root || root.hidden) return;
  root.hidden = true;
  document.body.classList.remove("lightbox-open");
  const img = root.querySelector(".image-lightbox-img");
  if (img) img.removeAttribute("src");
  const opener = state._lightboxOpener;
  state._lightboxOpener = null;
  if (opener && document.contains(opener)) opener.focus?.();
}

function bindLightboxUi() {
  document.addEventListener("click", (e) => {
    const btn = e.target?.closest?.(".polity-figure-open");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    openLightbox({
      src: btn.getAttribute("data-full-src"),
      caption: btn.getAttribute("data-caption") || "",
      alt: btn.getAttribute("data-alt") || "",
    });
  });
  document.addEventListener("keydown", (e) => {
    const lb = $("#image-lightbox");
    if (e.key === "Escape" && (!lb || lb.hidden)) clearPolitySelection();
  });
  document.addEventListener("keydown", (e) => {
    const root = $("#image-lightbox");
    if (!root || root.hidden) return;
    if (e.key === "Escape") {
      closeLightbox();
      return;
    }
    if (e.key === "Tab") {
      // Trap focus inside the dialog
      const items = [...root.querySelectorAll("button")].filter((b) => !b.hidden);
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
}

function inferImageRole(img) {
  const explicit = (img?.role || "").toLowerCase().trim();
  if (
    explicit &&
    [
      "leader",
      "religion",
      "literature",
      "art",
      "ideas",
      "story",
      "culture",
      "philosophy",
      "science",
      "overview",
      "conflict",
      "summary",
    ].includes(explicit)
  ) {
    return explicit === "summary" ? "overview" : explicit;
  }
  const t = `${img?.caption || ""} ${img?.alt || ""} ${img?.src || ""}`.toLowerCase();
  if (
    /augustus|charlemagne|theodoric|sutton hoo|helmet|portrait|statue|bust|emperor|king|queen|caesar|napoleon|elizabeth|luther|cnut|alfred|justinian|constantine|pericles|alexander|vladimir|suleiman|philip ii|charles v|gustav|vasa|prima porta/.test(
      t
    )
  ) {
    return "leader";
  }
  if (
    /altar|icon|temple|pantocrator|cathedral|mosque|church|gospel|kells|bible|psalter|ritual|grave good|kurgan|sun chariot|megalith|stonehenge|reliquar|cross|mosque|hagia|chartres|alhambra|sacrifice|idol|votive|chalice|censer|torc.*ritual|solar/.test(
      t
    )
  ) {
    return "religion";
  }
  if (
    /book|manuscript|folio|thes|print|illuminat|chronicle|poem|poetry|saga|text|letter|codex|quill|dante|shakespeare|cervantes|miniature/.test(
      t
    )
  ) {
    return "literature";
  }
  if (/battle|siege|treaty|turning point|revolt|uprising|war of|armada/.test(t)) {
    return "story";
  }
  if (/costume|dress|market|festival|peasant|court life|society|folk/.test(t)) {
    return "culture";
  }
  if (/philosoph|stoic|scholastic|enlightenment think|plato|aristotle|aquinas|descartes|kant/.test(t)) {
    return "philosophy";
  }
  if (
    /scient|astronom|mathematic|physic|chemic|medic|anatom|telescope|observatory|galileo|newton|copernicus|vesalius/.test(
      t
    )
  ) {
    return "science";
  }
  return "art";
}

function fillInlineGallery(el, images) {
  if (!el) return;
  const list = (images || []).filter((img) => img && img.src);
  el.innerHTML = list.map(figureHtml).join("");
  el.hidden = !list.length;
  el.classList.toggle("is-single", list.length === 1);
  bindFigureOrientation(el);
}

/** Route images into leaders / religion / culture / story / literature / art / philosophy / science */
function renderPolityGalleries(images) {
  const buckets = {
    overview: [],
    leader: [],
    religion: [],
    culture: [],
    story: [],
    literature: [],
    art: [],
    ideas: [],
    philosophy: [],
    science: [],
    conflict: [],
  };
  const list = Array.isArray(images) ? images.filter((img) => img && img.src) : [];
  list.forEach((img) => {
    const role = inferImageRole(img);
    (buckets[role] || buckets.art).push(img);
  });

  fillInlineGallery($("#polity-summary-gallery"), buckets.overview);
  fillInlineGallery($("#polity-leaders-gallery"), buckets.leader);
  fillInlineGallery($("#polity-religion-gallery"), buckets.religion);
  fillInlineGallery($("#polity-culture-gallery"), buckets.culture);
  fillInlineGallery($("#polity-story-gallery"), buckets.story);
  fillInlineGallery($("#polity-literature-gallery"), buckets.literature);
  fillInlineGallery($("#polity-art-gallery"), buckets.art);
  fillInlineGallery($("#polity-ideas-gallery"), buckets.ideas);
  fillInlineGallery($("#polity-philosophy-gallery"), buckets.philosophy);
  fillInlineGallery($("#polity-science-gallery"), buckets.science);
  fillInlineGallery($("#polity-conflicts-gallery"), buckets.conflict);

  const show = (id, has) => {
    const block = $(id);
    if (!block) return;
    const textEl =
      block.querySelector(".polity-story") ||
      block.querySelector("p:not(.kicker)");
    const hasText = !!(textEl?.textContent || "").trim();
    block.hidden = !(has || hasText);
  };
  show("#polity-leaders-block", buckets.leader.length > 0);
  show("#polity-religion-block", buckets.religion.length > 0);
  show("#polity-culture-block", buckets.culture.length > 0);
  show("#polity-story-block", buckets.story.length > 0);
  show("#polity-literature-block", buckets.literature.length > 0);
  show("#polity-art-block", buckets.art.length > 0);
  show("#polity-ideas-block", buckets.ideas.length > 0);
  show("#polity-philosophy-block", buckets.philosophy.length > 0);
  show("#polity-science-block", buckets.science.length > 0);
  show("#polity-conflicts-block", buckets.conflict.length > 0);
}

function renderKingdomDetail() {
  const period = currentPeriod();
  if (!period) return;

  const polityId = state.selectedPolityId;
  const polity = polityId && period.polities ? period.polities[polityId] : null;
  const layer = (period.mapLayers || []).find((l) => layerPolityId(l) === polityId);
  const packFeat = kingdomGeoSmoothed(period)?.features?.find(
    (f) => f.properties.polityId === polityId
  );
  const place =
    polity?.name || layer?.label || packFeat?.properties?.name || "Polity";

  $("#detail-kicker").textContent = polityId
    ? `${place} · ${formatYearUi(period.yearLabel)}`
    : `${period.era || "Kingdom era"} · ${formatYearUi(period.yearLabel)}`;

  setPlainText($("#culture-title"), polityId ? place : "Select a polity");
  const horizonEl = $("#culture-horizon");
  if (horizonEl) {
    if (!polityId) horizonEl.textContent = "Map polities";
    else {
      const bits = [polity?.type, polity?.yearsActive].filter(Boolean);
      horizonEl.textContent = bits.length
        ? bits.join(" · ")
        : "Kingdom / empire";
      if (packFeat?.properties?.approx) {
        const note = document.createElement("span");
        note.className = "approx-note";
        note.textContent = " · approx. borders";
        horizonEl.appendChild(note);
      }
    }
  }
  updateSelectionTip();

  const modeEl = $("#mode-pill");
  if (modeEl) {
    modeEl.textContent = "";
    modeEl.dataset.mode = "";
    modeEl.title = "";
  }

  const cultureDescEl = $("#culture-desc");
  if (cultureDescEl) cultureDescEl.hidden = false;
  setPlainText(
    cultureDescEl,
    polity ? polity.summary || "" : "Select a polity on the map or in the list below."
  );

  const polityPanel = $("#polity-panel");
  if (polityPanel) {
    if (polity) {
      polityPanel.hidden = false;
      const kicker = $("#polity-panel-kicker");
      if (kicker) kicker.textContent = "Polity";
      polityPanel.dataset.scope = "polity";
      setPlainText($("#polity-name"), polity.name || place);
      setProseText($("#polity-summary"), polity.summary || "");
      setPolityField("conflicts", polity.conflicts);
      setPolityField("leaders", polity.leaders);
      setPolityField("religion", polity.religion);
      setPolityField("culture", polity.culture);
      setPolityField("story", polity.stories || polity.story);
      setPolityField("literature", polity.literature);
      applyCultureFields(polity);
      renderPolityChain(polity);
      renderPolityGalleries(polity.images);
    } else {
      polityPanel.hidden = true;
      renderPolityChain(null);
      renderPolityGalleries(null);
    }
  }

  // Deep-time–only panels must not linger under kingdom polity copy
  clearDeepTimeOnlyDetail();
  scrubBodyCopyMarkup();
  highlightCultureChips();
}

/** Hide ancestry / language / absorb UI that belongs only to Deep-time. */
function clearDeepTimeOnlyDetail() {
  const note = $("#ancestry-note");
  if (note) {
    note.hidden = true;
    setPlainText(note, "");
  }
  const mid = $("#ancestry-mid-label");
  if (mid) mid.hidden = true;
  const cline = $("#ancestry-cline");
  if (cline) cline.hidden = true;
  setPlainText($("#absorb-substrate"), "");
  setPlainText($("#absorb-incoming"), "");
  setPlainText($("#absorb-fused"), "");
  setPlainText($("#ling-note"), "");
  const lingFamily = $("#ling-family");
  if (lingFamily) lingFamily.textContent = "";
  const lingLangs = $("#ling-languages");
  if (lingLangs) lingLangs.textContent = "";
}

const PERIOD_TEXT_LOADS = new Map();
/** Long region/polity prose lives in data/timeline-text/<period>.json; merge on demand. */
function ensurePeriodText(period) {
  if (!period?.id || period._textLoaded || PERIOD_TEXT_LOADS.has(period.id)) return;
  const job = fetch(withV(`data/timeline-text/${period.id}.json`))
    .then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    })
    .then((txt) => {
      for (const [rid, extra] of Object.entries(txt.regions || {})) {
        if (period.regions?.[rid]) Object.assign(period.regions[rid], extra);
      }
      for (const [pid, extra] of Object.entries(txt.polities || {})) {
        if (period.polities?.[pid]) Object.assign(period.polities[pid], extra);
      }
      period._textLoaded = true;
      if (!isKingdomMode() && currentPeriod() === period) renderDetail();
    })
    .catch(() => {
      PERIOD_TEXT_LOADS.delete(period.id);
      showLoadNotice("Some descriptions for this period could not load.", {
        retry: () => ensurePeriodText(period) || renderDetail(),
      });
    });
  PERIOD_TEXT_LOADS.set(period.id, job);
}

function renderDetail() {
  const period = currentPeriod();
  if (!period) return;

  if (isKingdomMode()) {
    renderKingdomDetail();
    renderKeyEvents();
    return;
  }
  ensurePeriodText(period);

  const rid = state.selectedRegion;
  const region = regionData(period, rid);
  if (!region) return;

  const keys = state.data.meta.ancestryKeys;
  const modeLegend = state.data.meta.modeLegend || {};
  const entries = ancestryEntries(region, keys);
  const isoName = state.selectedIso
    ? state.geo.features.find((f) => f.properties.iso === state.selectedIso)?.properties
        .name
    : null;

  const place = isoName || REGION_LABELS[rid];
  $("#detail-kicker").textContent = `${place} · ${formatYearUi(period.yearLabel)}`;

  // Overall culture horizon from map layers covering this country
  // Prefer short cultureLabel — full packs store long prose in `culture`
  const shortCulture =
    (region.cultureLabel || "").trim() ||
    (region.culture && String(region.culture).length <= 72
      ? String(region.culture).trim()
      : "");
  let horizon = shortCulture || region.culture || "";
  if (state.selectedIso) {
    const cov = countryStyleForPeriod(period, state.selectedIso);
    const names = (cov.labels || []).map((l) => l.label).filter(Boolean);
    if (names.length) horizon = names.join(" · ");
  }
  if (horizon && horizon.length > 120) {
    horizon = horizon.slice(0, 117).trim() + "…";
  }
  setPlainText($("#culture-title"), horizon);
  const horizonEl = $("#culture-horizon");
  if (horizonEl) {
    // Never dump long `culture` prose here — that belongs in the Region panel
    // below CONTINUITY (was duplicating Tumulus/Urnfield blurbs above the pill).
    const shortLabel = (region.cultureLabel || "").trim();
    const cultureIsShort =
      region.culture && String(region.culture).trim().length <= 72
        ? String(region.culture).trim()
        : "";
    const subtitle = shortLabel || cultureIsShort;
    if (subtitle && horizon && subtitle !== horizon && !horizon.startsWith(subtitle)) {
      horizonEl.textContent = `Regional horizon · ${subtitle}`;
    } else if (state.selectedIso && subtitle && horizon !== subtitle) {
      horizonEl.textContent = "Map layers here";
    } else {
      horizonEl.textContent = "Cultural horizon";
    }
  }
  updateSelectionTip();

  const modeEl = $("#mode-pill");
  modeEl.textContent = region.mode;
  modeEl.dataset.mode = region.mode;
  modeEl.title = modeLegend[region.mode] || "";

  let desc = region.description;
  if (state.selectedIso) {
    const cov = countryStyleForPeriod(period, state.selectedIso);
    const layerBits = (cov.labels || []).map((l) => l.label).join(" · ");
    if (layerBits) {
      desc = `Map layers here: ${layerBits}. ${region.description}`;
    }
  }
  // culture-desc is filled after we know whether the Region panel will repeat it
  const cultureDescEl = $("#culture-desc");
  setPlainText(cultureDescEl, desc || "");
  if (cultureDescEl) cultureDescEl.hidden = false;

  // Region panel — same field richness as kingdom tabs once full packs land
  const polityPanel = $("#polity-panel");
  const polity =
    state.selectedIso && period.polities
      ? period.polities[state.selectedIso]
      : null;
  const cultureSource = mergeDeepTimeCulture(polity || {}, period);
  // Always prefer atlas-region culture label when panel is region-scoped
  if (region?.culture && !String(cultureSource.culture || "").trim()) {
    cultureSource.culture = region.culture;
  }
  const longSummary = pickLongestProse(
    cultureSource.summary,
    cultureSource.narrative,
    cultureSource.description,
    polity?.summary,
    region?.description
  );
  if (longSummary) cultureSource.summary = longSummary;
  const hasCulturePanel = deepTimePanelHasContent(cultureSource) || !!polity;
  if (polityPanel) {
    if (hasCulturePanel) {
      polityPanel.hidden = false;
      const kicker = $("#polity-panel-kicker");
      if (kicker) kicker.textContent = polity ? "Polity" : "Region";
      polityPanel.dataset.scope = polity ? "polity" : "region";
      const placeName =
        polity?.name ||
        (state.selectedIso
          ? state.geo?.features?.find((f) => f.properties.iso === state.selectedIso)
              ?.properties?.name
          : null) ||
        REGION_LABELS[rid] ||
        "—";
      setPlainText($("#polity-name"), placeName);
      setProseText($("#polity-summary"), longSummary || "");
      // Drop the pre-CONTINUITY/side blurb when the Region panel already carries it
      if (cultureDescEl && longSummary) {
        const d = (desc || "").trim();
        const s = longSummary.trim();
        const same =
          !d ||
          d === s ||
          (d.length > 40 && s.includes(d.slice(0, 80))) ||
          (s.length > 40 && d.includes(s.slice(0, 80))) ||
          (region?.description &&
            s.includes(String(region.description).trim().slice(0, 80)));
        if (same) {
          setPlainText(cultureDescEl, "");
          cultureDescEl.hidden = true;
        }
      }
      setPolityField("conflicts", cultureSource.conflicts || polity?.conflicts);
      setPolityField("leaders", cultureSource.leaders || polity?.leaders);
      setPolityField("religion", cultureSource.religion || polity?.religion);
      setPolityField(
        "culture",
        cultureSource.culture || polity?.culture || region?.culture
      );
      setPolityField(
        "story",
        cultureSource.stories || cultureSource.story || polity?.stories || polity?.story
      );
      setPolityField("literature", cultureSource.literature || polity?.literature);
      applyCultureFields(cultureSource);
      renderPolityChain(polity);
      renderPolityGalleries(cultureSource.images || polity?.images);
    } else {
      polityPanel.hidden = true;
      renderPolityChain(null);
      renderPolityGalleries(null);
    }
  }

  const note = $("#ancestry-note");
  if (region.ancestryNote) {
    note.hidden = false;
    setPlainText(note, region.ancestryNote);
  } else {
    note.hidden = true;
  }

  setPlainText($("#absorb-substrate"), region.substrate || "—");
  setPlainText($("#absorb-incoming"), region.incoming || "—");
  setPlainText($("#absorb-fused"), region.fused || "—");
  scrubBodyCopyMarkup();
  renderKeyEvents();

  const confLabels = state.data.meta.confidenceLabels || {};
  const conf = region.linguisticConfidence || "hypothetical";
  $("#ling-family").textContent = region.languageFamily || "—";
  $("#ling-languages").textContent = region.languages || "—";
  const confEl = $("#ling-confidence");
  confEl.textContent = conf;
  confEl.dataset.conf = conf;
  confEl.title = confLabels[conf] || "";
  $("#ling-note").textContent = region.linguisticNote || "";

  $("#stack-bar").innerHTML = entries
    .map((e) => {
      const tip = e.rangeLabel
        ? `${e.detail}: ${e.rangeLabel} (mid ~${Math.round(e.value)}%)`
        : `${e.detail}: ~${Math.round(e.value)}%`;
      return `<div class="stack-seg" style="width:${e.value}%;background:${safeColor(e.color)}" title="${escapeHtml(tip)}"></div>`;
    })
    .join("");

  const pie = $("#pie");
  if (pie) {
    pie.style.background = "transparent";
    pie.innerHTML = pieMarkup(entries);
  }
  $("#pie-list").innerHTML = entries
    .map((e) => {
      const pct = e.rangeLabel || `~${Math.round(e.value)}%`;
      const label = e.displayLabel || e.label;
      return `<li title="${escapeHtml(e.detail)}" style="--swatch:${safeColor(e.color)}"><strong>${escapeHtml(label)}</strong><span class="pct">${escapeHtml(pct)}</span></li>`;
    })
    .join("");

  renderAncestryCline(region, keys);
  renderGlossary(entries);
  highlightCultureChips();
}

function splitTickYear(yearStr) {
  // "2500 BCE" / "2500 BC" → { num: "2500", era: "BC" }; CE/AD → "AD"
  const cleaned = formatYearUi(yearStr).trim();
  const m = cleaned.match(/^(\d+)\s*(BC|AD)?$/i);
  if (!m) return { num: cleaned, era: "" };
  const era = (m[2] || "").toUpperCase();
  return { num: m[1], era };
}

/** Desktop sliders label every stop. Phones and tablets keep the sparse row. */
function desktopTickLabels() {
  try {
    return window.matchMedia("(min-width: 900px)").matches;
  } catch (_) {
    return false;
  }
}

/** How many year labels fit without crush on the current slider width. */
function maxTickLabelsForWidth(widthPx) {
  if (desktopTickLabels()) return Number.POSITIVE_INFINITY;
  const w = widthPx || 400;
  if (w < 360) return 4;
  if (w < 480) return 5;
  if (w < 640) return 6;
  return 7;
}

/** Min horizontal gap (px) between label centers on narrow screens. */
function minTickLabelGapPx(widthPx) {
  return widthPx < 400 ? 68 : widthPx < 560 ? 72 : 78;
}

/** Indices of year labels to show under the slider (always first + last).
 *  Scrubbing still snaps to every period — only the label row is sparse. */
function sparseTickLabelIndices(n, maxLabels = 7) {
  if (n <= 0) return [];
  if (n <= maxLabels) return Array.from({ length: n }, (_, i) => i);
  const out = new Set([0, n - 1]);
  const inner = maxLabels - 2;
  for (let k = 1; k <= inner; k++) {
    out.add(Math.round((k * (n - 1)) / (inner + 1)));
  }
  return [...out].sort((a, b) => a - b);
}

/** Drop inner labels that would sit closer than minGapPx (keep first/last). */
function thinTickLabelsByGap(indices, n, widthPx, minGapPx) {
  if (n <= 1 || indices.length <= 2) return indices;
  const pos = (i) => (n <= 1 ? 0 : (i / (n - 1)) * widthPx);
  const kept = [indices[0]];
  for (let k = 1; k < indices.length - 1; k++) {
    const i = indices[k];
    if (pos(i) - pos(kept[kept.length - 1]) >= minGapPx) kept.push(i);
  }
  const last = indices[indices.length - 1];
  while (kept.length > 1 && pos(last) - pos(kept[kept.length - 1]) < minGapPx) {
    kept.pop();
  }
  kept.push(last);
  return kept;
}

/** Conservative label width so the first paint does not overlap before fonts finish. */
function estimatedTickLabelWidth(yearText) {
  const len = (splitTickYear(yearText).num || "").length;
  if (len >= 4) return 50;
  if (len === 3) return 40;
  if (len === 2) return 32;
  return 24;
}

/** Same drop rule as pruneOverlappingTickLabels, using the slider width we already have. */
function prethinDesktopTickLabels(indices, periods, n, widthPx) {
  if (!widthPx || n <= 2 || indices.length <= 2) return indices;
  const kept = indices.slice();
  const box = (i) => {
    const year = formatYearUi(periods[i].tickYear || periods[i].yearLabel);
    const w = estimatedTickLabelWidth(year);
    const x = (i / (n - 1)) * widthPx;
    if (i === 0) return { left: 0, right: w };
    if (i === n - 1) return { left: widthPx - w, right: widthPx };
    return { left: x - w / 2, right: x + w / 2 };
  };
  let guard = 0;
  while (guard++ < 48 && kept.length > 2) {
    let dropAt = -1;
    for (let k = 0; k < kept.length - 1; k++) {
      const gap = box(kept[k + 1]).left - box(kept[k]).right;
      if (gap >= 4) continue;
      if (k === 0) dropAt = 1;
      else if (k + 1 === kept.length - 1) dropAt = k;
      else dropAt = k + 1;
      break;
    }
    if (dropAt < 0) break;
    kept.splice(dropAt, 1);
  }
  return kept;
}

/** Drop inner desktop labels whose boxes touch. First and last years always stay. */
function pruneOverlappingTickLabels(wrap) {
  if (!wrap) return;
  const minGap = 4;
  const nodes = () => [...wrap.querySelectorAll(".tick-label")];
  let guard = 0;
  while (guard++ < 48) {
    const list = nodes();
    if (list.length <= 2) return;
    const boxes = list.map((el) => ({ el, r: el.getBoundingClientRect() }));
    // Not laid out yet (or a web font has not painted). Caller retries after layout.
    if (boxes.some((b) => b.r.width < 1)) return;
    let drop = null;
    for (let i = 0; i < boxes.length - 1; i++) {
      const gap = boxes[i + 1].r.left - boxes[i].r.right;
      if (gap >= minGap) continue;
      if (i === 0) drop = boxes[1].el;
      else if (i + 1 === boxes.length - 1) drop = boxes[i].el;
      else drop = boxes[i + 1].el;
      break;
    }
    if (!drop) return;
    drop.remove();
  }
}

let tickLabelPruneGen = 0;

/** Measure after layout and after Sora loads. The sync pass often sees zero-width boxes. */
function scheduleDesktopTickPrune(wrap) {
  if (!desktopTickLabels() || !wrap) return;
  const gen = ++tickLabelPruneGen;
  const run = () => {
    if (gen !== tickLabelPruneGen || !wrap.isConnected) return;
    pruneOverlappingTickLabels(wrap);
  };
  const afterFrame = () => {
    requestAnimationFrame(() => requestAnimationFrame(run));
  };
  afterFrame();
  const fonts = document.fonts;
  if (fonts && fonts.status !== "loaded" && typeof fonts.ready?.then === "function") {
    fonts.ready.then(afterFrame).catch(() => {});
  }
}

/**
 * Center of the range thumb. pos is 0..1 along the slider, matching the input.
 * The thumb's used width does not come back from getComputedStyle (it reports the
 * input width), so this follows the widths in styles.css: 34px, 30px under 860px.
 */
function sliderThumbWidthPx() {
  try {
    if (window.matchMedia("(max-width: 860px)").matches) return 30;
  } catch (_) {
    /* matchMedia unavailable */
  }
  return 34;
}

function sliderThumbCenterPx(pos, trackWidth, thumbWidth) {
  const p = Math.max(0, Math.min(1, pos));
  const travel = Math.max(0, trackWidth - thumbWidth);
  return thumbWidth / 2 + p * travel;
}

function periodSliderPos(index, count) {
  if (count <= 1) return 0;
  return index / (count - 1);
}

/** Year → thumb position. Linear inside each period segment, because the slider itself steps by period. */
function yearToSliderPos(year, periods) {
  const n = periods.length;
  if (n <= 1) return 0;
  const y0 = Number(periods[0].yearApprox);
  const y1 = Number(periods[n - 1].yearApprox);
  if (year <= y0) return 0;
  if (year >= y1) return 1;
  for (let i = 0; i < n - 1; i++) {
    const a = Number(periods[i].yearApprox);
    const b = Number(periods[i + 1].yearApprox);
    const lo = Math.min(a, b);
    const hi = Math.max(a, b);
    if (year < lo || year > hi) continue;
    const span = b - a;
    const t = span === 0 ? 0 : (year - a) / span;
    return periodSliderPos(i, n) + t * (periodSliderPos(i + 1, n) - periodSliderPos(i, n));
  }
  return 1;
}

function scaleYearText(yearApprox) {
  const y = Math.round(Number(yearApprox));
  if (y < 0) return `${Math.abs(y)} BC`;
  return `${y} AD`;
}

/**
 * Labels for the desktop Deep-time scale.
 * Always the first period, the BC/AD step change, and the last period.
 * Other labels are round years on the period notches, at least two steps apart,
 * with no unlabeled run longer than three steps.
 */
function deepTimeLabelIndices(periods) {
  const n = periods.length;
  if (!n) return [];
  const breakIdx = Math.max(
    0,
    periods.findIndex((p) => Number(p.yearApprox) >= 1)
  );
  const kept = new Set([0, breakIdx, n - 1]);
  const score = (i) => {
    const y = Math.abs(Math.round(Number(periods[i].yearApprox)));
    if (y % 1000 === 0) return 3;
    if (y % 500 === 0) return 2;
    if (y % 100 === 0) return 1;
    return 0;
  };
  const order = [...Array(n).keys()].sort((a, b) => score(b) - score(a) || a - b);
  for (const i of order) {
    if (score(i) < 1) continue;
    if ([...kept].some((k) => Math.abs(k - i) < 2)) continue;
    kept.add(i);
  }
  let guard = 0;
  while (guard++ < n) {
    const list = [...kept].sort((a, b) => a - b);
    let gap = null;
    for (let k = 0; k < list.length - 1; k++) {
      const span = list[k + 1] - list[k];
      if (span >= 4 && (!gap || span > gap.span)) gap = { span, a: list[k], b: list[k + 1] };
    }
    if (!gap) break;
    const mid = (gap.a + gap.b) / 2;
    let best = -1;
    let bestKey = Infinity;
    for (let i = gap.a + 1; i < gap.b; i++) {
      const key = Math.abs(i - mid) - score(i) * 0.01;
      if (key < bestKey) {
        bestKey = key;
        best = i;
      }
    }
    if (best < 0) break;
    kept.add(best);
  }
  return [...kept].sort((a, b) => a - b);
}

/** Short notches on a year grid: 1000 years before AD 1, 250 years after. Stops are not repeated. */
function deepTimeMinorYears(periods) {
  if (periods.length < 2) return [];
  const start = Number(periods[0].yearApprox);
  const end = Number(periods[periods.length - 1].yearApprox);
  const breakYear = Number(periods.find((p) => Number(p.yearApprox) >= 1)?.yearApprox ?? 1);
  const stops = new Set(periods.map((p) => Math.round(Number(p.yearApprox))));
  const years = [];
  const firstBc = Math.ceil((start + 1) / 1000) * 1000;
  for (let y = firstBc; y < 0 && y < breakYear; y += 1000) {
    if (!stops.has(y)) years.push(y);
  }
  const firstAd = Math.floor(breakYear / 250) * 250 + 250;
  for (let y = firstAd; y < end; y += 250) {
    if (y <= breakYear || stops.has(y)) continue;
    years.push(y);
  }
  return years;
}

function sliderTrackGeometry(wrap) {
  const input = $("#time-slider");
  if (!input || !wrap) return null;
  const inputBox = input.getBoundingClientRect();
  const wrapBox = wrap.getBoundingClientRect();
  if (inputBox.width < 2) return null;
  const thumb = sliderThumbWidthPx(input);
  return {
    origin: inputBox.left - wrapBox.left,
    track: inputBox.width,
    thumb,
  };
}

function thumbX(geo, pos) {
  return geo.origin + sliderThumbCenterPx(pos, geo.track, geo.thumb);
}

function wireTickControls(wrap) {
  wrap.querySelectorAll(".tick-mark-btn, .tick-label").forEach((el) => {
    el.addEventListener("click", () => snapToPeriod(Number(el.dataset.i)));
  });
  wrap.querySelectorAll(".tick-mark-btn, .tick-label").forEach((el) => {
    el.classList.toggle("is-active", Number(el.dataset.i) === state.periodIndex);
  });
  updateTickCaption();
}

/** Drop an inner label if the painted boxes still touch. First, last, and the AD 1 hinge stay. */
function relieveScaleLabelOverlap(wrap) {
  const minGap = 20;
  const nodes = () => [...wrap.querySelectorAll(".tick-label")];
  let guard = 0;
  while (guard++ < 12) {
    const list = nodes();
    if (list.length <= 2) return;
    const boxes = list.map((el) => ({ el, r: el.getBoundingClientRect() }));
    if (boxes.some((b) => b.r.width < 1)) return;
    let drop = null;
    let tightest = minGap;
    for (let i = 0; i < boxes.length - 1; i++) {
      const gap = boxes[i + 1].r.left - boxes[i].r.right;
      if (gap >= tightest) continue;
      const a = boxes[i].el;
      const b = boxes[i + 1].el;
      const protectedA = a.classList.contains("is-scale-end") || a.classList.contains("is-scale-break");
      const protectedB = b.classList.contains("is-scale-end") || b.classList.contains("is-scale-break");
      if (protectedA && protectedB) continue;
      tightest = gap;
      drop = protectedA ? b : protectedB ? a : b;
    }
    if (!drop || tightest >= minGap) return;
    drop.remove();
  }
}

/**
 * Desktop Deep-time scale.
 * The thumb is linear in period index. Tall notches are the selectable periods.
 * Short notches are a year grid inside each segment (1000y before AD 1, 250y after).
 */
function buildDeepTimeYearScale(wrap, periods) {
  const n = periods.length;
  const geo = sliderTrackGeometry(wrap);
  wrap.classList.add("is-year-scale");
  if (!geo || n < 2) {
    const tries = Number(wrap.dataset.scaleTries || 0);
    if (tries > 8) return;
    wrap.dataset.scaleTries = String(tries + 1);
    requestAnimationFrame(() => {
      if (desktopTickLabels() && !isKingdomMode()) buildTicks();
    });
    return;
  }
  delete wrap.dataset.scaleTries;
  const breakIdx = Math.max(
    0,
    periods.findIndex((p) => Number(p.yearApprox) >= 1)
  );
  const labeled = new Set(deepTimeLabelIndices(periods));
  const xAt = (pos) => thumbX(geo, pos);
  const stopX = periods.map((_, i) => xAt(periodSliderPos(i, n)));

  const minors = deepTimeMinorYears(periods)
    .map((year) => ({ year, x: xAt(yearToSliderPos(year, periods)) }))
    .filter((tick) => stopX.every((sx) => Math.abs(sx - tick.x) >= 5));

  const minorHtml = minors
    .map(
      (tick) =>
        `<span class="tick-notch" style="left:${tick.x}px" title="${escapeHtml(scaleYearText(tick.year))}" aria-hidden="true"></span>`
    )
    .join("");

  const stopHtml = periods
    .map((p, i) => {
      const name = shortPeriodName(p);
      const text = scaleYearText(p.yearApprox);
      const title = `${text}: ${name}`;
      const breakCls = i === breakIdx ? " is-scale-break" : "";
      const active = i === state.periodIndex ? " is-active" : "";
      return `<button type="button" class="tick-mark-btn${breakCls}${active}" data-i="${i}" style="left:${stopX[i]}px" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}"><span class="tick-mark" aria-hidden="true"></span></button>`;
    })
    .join("");

  const labelHtml = [...labeled]
    .map((i) => {
      const p = periods[i];
      const text = scaleYearText(p.yearApprox);
      const name = shortPeriodName(p);
      const title = `${text}: ${name}`;
      const end = i === 0 || i === n - 1 ? " is-scale-end" : "";
      const hinge = i === breakIdx ? " is-scale-break" : "";
      const active = i === state.periodIndex ? " is-active" : "";
      return `<button type="button" class="tick-label${end}${hinge}${active}" data-i="${i}" style="left:${stopX[i]}px" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}">${escapeHtml(text)}</button>`;
    })
    .join("");

  wrap.innerHTML = `<div class="tick-rail" role="presentation">${minorHtml}${stopHtml}</div><div class="tick-label-layer">${labelHtml}</div>`;
  wireTickControls(wrap);
  const refreshLabels = () => {
    if (!wrap.isConnected || !wrap.classList.contains("is-year-scale")) return;
    relieveScaleLabelOverlap(wrap);
  };
  requestAnimationFrame(refreshLabels);
  if (document.fonts && document.fonts.status !== "loaded" && document.fonts.ready) {
    document.fonts.ready.then(() => requestAnimationFrame(refreshLabels)).catch(() => {});
  }
}

function buildTicks() {
  const wrap = $("#tick-labels");
  if (!wrap) return;
  const periods = activePeriods();
  if (desktopTickLabels() && !isKingdomMode()) {
    buildDeepTimeYearScale(wrap, periods);
    return;
  }
  wrap.classList.remove("is-year-scale");
  const n = periods.length;
  const widthPx = wrap.clientWidth || wrap.parentElement?.clientWidth || window.innerWidth || 400;
  const maxLabels = maxTickLabelsForWidth(widthPx);
  let labeledIdx = sparseTickLabelIndices(n, maxLabels);
  // Below 900px the sparse row is unchanged. Desktop starts from every stop.
  if (!desktopTickLabels()) {
    labeledIdx = thinTickLabelsByGap(
      labeledIdx,
      n,
      widthPx,
      minTickLabelGapPx(widthPx)
    );
  } else {
    labeledIdx = prethinDesktopTickLabels(labeledIdx, periods, n, widthPx);
  }
  const labeled = new Set(labeledIdx);

  const marks = periods
    .map((p, i) => {
      const name = shortPeriodName(p);
      const title = `${formatYearUi(p.yearLabel)}: ${name}`;
      return `<button type="button" class="tick-mark-btn" data-i="${i}" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}"><span class="tick-mark" aria-hidden="true"></span></button>`;
    })
    .join("");

  const labels = labeledIdx
    .map((i) => {
      const p = periods[i];
      const year = formatYearUi(p.tickYear || p.yearLabel);
      const { num, era } = splitTickYear(year);
      const name = shortPeriodName(p);
      const title = `${formatYearUi(p.yearLabel)}: ${name}`;
      const pct = n <= 1 ? 0 : (i / (n - 1)) * 100;
      const edge = i === 0 ? " is-first" : i === n - 1 ? " is-last" : "";
      const active = i === state.periodIndex ? " is-active" : "";
      return `<button type="button" class="tick-label${edge}${active}" data-i="${i}" style="left:${pct}%" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}"><span class="tick-num">${escapeHtml(num)}</span><span class="tick-era">${escapeHtml(era)}</span></button>`;
    })
    .join("");

  wrap.innerHTML = `<div class="tick-rail" role="presentation">${marks}</div><div class="tick-label-layer">${labels}</div>`;
  if (desktopTickLabels()) {
    // Force layout so a resize (fonts already in) can prune in this turn.
    void wrap.offsetWidth;
    pruneOverlappingTickLabels(wrap);
    scheduleDesktopTickPrune(wrap);
  }
  wireTickControls(wrap);
}

function syncAtlasTabs() {
  $$("#atlas-tabs .atlas-tab").forEach((btn) => {
    const mode = btn.dataset.mode;
    const on = mode === state.atlasMode;
    btn.classList.toggle("is-active", on);
    btn.setAttribute("aria-selected", on ? "true" : "false");

    if (mode === "deep-time") {
      btn.hidden = false;
      btn.disabled = false;
      return;
    }
    if (KINGDOM_PACK_IDS.includes(mode)) {
      const loading = PACK_LOADS.has(mode);
      btn.hidden = false;
      btn.disabled = false;
      btn.setAttribute("aria-busy", loading ? "true" : "false");
      btn.classList.toggle("is-loading", loading);
      btn.title = loading ? "Loading map…" : KINGDOM_TAB_LABELS[mode] || mode;
    }
    btn.setAttribute("tabindex", on ? "0" : "-1");
  });
  document.querySelector(".app")?.setAttribute("data-atlas-mode", state.atlasMode);
}

const PACK_LOADS = new Map();
/** Lazy-load a kingdom pack the first time its tab is opened. */
function requestKingdomPack(mode) {
  if (state.kingdomPacks[mode]) return Promise.resolve(state.kingdomPacks[mode]);
  if (PACK_LOADS.has(mode)) return PACK_LOADS.get(mode);
  const job = loadKingdomPack(mode).then((pack) => {
    PACK_LOADS.delete(mode);
    if (pack?.periods?.length) state.kingdomPacks[mode] = pack;
    syncAtlasTabs();
    return state.kingdomPacks[mode] || null;
  });
  PACK_LOADS.set(mode, job);
  syncAtlasTabs();
  return job;
}

function setAtlasMode(mode) {
  if (!ATLAS_TAB_ORDER.includes(mode) || mode === state.atlasMode) return;
  if (isKingdomMode(mode) && !state.kingdomPacks[mode]) {
    requestKingdomPack(mode).then((pack) => {
      if (pack) setAtlasMode(mode);
      else
        showLoadNotice(`The ${KINGDOM_TAB_LABELS[mode] || mode} map could not load.`, {
          retry: () => setAtlasMode(mode),
        });
    });
    return;
  }

  state.atlasMode = mode;
  state._kingdomGeoPeriodId = null;
  state._smoothGeoCache = new Map();
  syncAtlasTabs();

  state.selectedPolityId = null;

  if (isKingdomMode()) {
    state.selectedIso = null;
    state.svg?.selectAll("path.country").classed("is-active", false);
  } else {
    state.selectedRegion = "britain";
    state.selectedIso = "GBR";
  }

  buildTicks();
  initMap({ preserveZoom: false });
  if (isKingdomMode()) syncKingdomPolityLayer({ force: true });
  updateLegend();
  updateCulturesRail();
  renderGlossary();

  let startIdx = 0;
  if (isKingdomMode()) {
    const pack = activePack();
    const periods = activePeriods();
    if (pack?.defaultYear != null) {
      const i = periods.findIndex((p) => p.yearApprox === pack.defaultYear);
      if (i >= 0) startIdx = i;
    }
  } else {
    const i = state.data.periods.findIndex((p) => p.id === "beaker-corded");
    startIdx = i >= 0 ? i : 0;
  }
  snapToPeriod(startIdx);

  if (!isKingdomMode() && state.selectedIso) {
    state.svg
      ?.selectAll("path.country")
      .classed("is-active", (d) => d.properties.iso === state.selectedIso);
  }
  renderDetail();
  highlightCultureChips();
  updateSelectionTip();
}

function syncThemeColor() {
  const dark = document.documentElement.getAttribute("data-theme") === "dark";
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", dark ? "#111111" : "#f4f4f4");
}

function activeLegendLayer() {
  const id = state.legendHoverId || state.legendPinId;
  if (!id) return null;
  return legendLayers().find((l) => legendLayerId(l) === id) || null;
}

function applyLegendFocus() {
  const layer = activeLegendLayer();
  const activeId = layer ? legendLayerId(layer) : null;
  $("#map")?.classList.toggle("is-legend-on", Boolean(layer));
  $$("#map-legend .legend-row").forEach((row) => {
    const on = row.dataset.layer === activeId;
    row.classList.toggle("is-on", on);
    row.setAttribute("aria-pressed", row.dataset.layer === state.legendPinId ? "true" : "false");
  });
  if (!state.svg) return;
  if (!layer) {
    state.svg.selectAll("path.country, path.polity, path.country-extent").classed("is-legend-hot", false).classed("is-legend-dim", false);
    return;
  }
  const isos = new Set(layer.countries || []);
  const useCountries = !isKingdomMode() && isos.size > 0;
  const pid = legendLayerId(layer);
  state.svg
    .selectAll("path.country")
    .classed("is-legend-hot", (d) => useCountries && isos.has(d.properties.iso))
    .classed("is-legend-dim", (d) => useCountries && !isos.has(d.properties.iso));
  // Clipped culture-colour overlays (meta.fillExtents) follow their country
  state.svg
    .selectAll("path.country-extent")
    .classed("is-legend-hot", (d) => useCountries && isos.has(d.properties.iso))
    .classed("is-legend-dim", (d) => useCountries && !isos.has(d.properties.iso));
  state.svg
    .selectAll("path.polity")
    .classed("is-legend-hot", (d) => isKingdomMode() && d.properties.polityId === pid)
    .classed("is-legend-dim", (d) => isKingdomMode() && d.properties.polityId !== pid);
}

function bindLegendInteractions() {
  const box = $("#map-legend");
  if (!box || box.dataset.bound) return;
  box.dataset.bound = "1";
  const rowFrom = (target) => target?.closest?.(".legend-row") || null;
  box.addEventListener("pointerover", (e) => {
    if (e.pointerType === "touch") return;
    const row = rowFrom(e.target);
    if (!row) return;
    state.legendHoverId = row.dataset.layer;
    applyLegendFocus();
  });
  box.addEventListener("pointerout", (e) => {
    if (e.pointerType === "touch") return;
    const row = rowFrom(e.target);
    if (!row) return;
    const next = e.relatedTarget?.closest?.(".legend-row");
    if (next === row) return;
    if (state.legendHoverId === row.dataset.layer) state.legendHoverId = null;
    applyLegendFocus();
  });
  box.addEventListener("focusin", (e) => {
    const row = rowFrom(e.target);
    if (!row) return;
    state.legendHoverId = row.dataset.layer;
    applyLegendFocus();
  });
  box.addEventListener("focusout", (e) => {
    const row = rowFrom(e.target);
    if (!row) return;
    const next = e.relatedTarget?.closest?.(".legend-row");
    if (next) return;
    if (state.legendHoverId === row.dataset.layer) state.legendHoverId = null;
    applyLegendFocus();
  });
  box.addEventListener("click", (e) => {
    const row = rowFrom(e.target);
    if (!row) return;
    const id = row.dataset.layer;
    state.legendPinId = state.legendPinId === id ? null : id;
    // Mouse/pen stay hovered after a click. Touch and keyboard must be able
    // to clear the highlight on the second tap without waiting for a leave.
    const fromMouse = e.pointerType === "mouse" || e.pointerType === "pen";
    if (!fromMouse) state.legendHoverId = null;
    else if (!state.legendPinId) state.legendHoverId = id;
    applyLegendFocus();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !state.legendPinId) return;
    state.legendPinId = null;
    const focused = document.activeElement?.closest?.(".legend-row");
    state.legendHoverId = focused?.dataset.layer || null;
    applyLegendFocus();
    e.preventDefault();
    e.stopImmediatePropagation();
  });
}

function bindUI() {
  const slider = $("#time-slider");
  slider.max = String(SLIDER_MAX);

  let raf = null;
  slider.addEventListener("input", () => {
    const pos = Number(slider.value) / SLIDER_MAX;
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => setSliderPos(pos, { fromSlider: true }));
  });

  $("#btn-prev").addEventListener("click", () =>
    snapToPeriod(Math.max(0, state.periodIndex - 1))
  );
  $("#btn-next").addEventListener("click", () =>
    snapToPeriod(Math.min(activePeriods().length - 1, state.periodIndex + 1))
  );

  document.addEventListener("keydown", (e) => {
    if (e.defaultPrevented || e.altKey || e.metaKey || e.ctrlKey) return;
    if (e.target?.closest?.("input, textarea, select, [contenteditable], summary, .image-lightbox"))
      return;
    if (e.key === "ArrowLeft") snapToPeriod(Math.max(0, state.periodIndex - 1));
    if (e.key === "ArrowRight")
      snapToPeriod(Math.min(activePeriods().length - 1, state.periodIndex + 1));
  });

  // Event delegation — reliable taps even when tabs reflow/wrap
  $("#atlas-tabs")?.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    const tabs = [...$$("#atlas-tabs .atlas-tab")].filter((b) => !b.hidden);
    const i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    e.preventDefault();
    e.stopPropagation();
    const next = tabs[(i + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length];
    next.focus();
    setAtlasMode(next.dataset.mode);
  });
  $("#atlas-tabs")?.addEventListener("click", (e) => {
    const btn = e.target?.closest?.(".atlas-tab");
    if (!btn || btn.disabled || btn.hidden) return;
    e.preventDefault();
    setAtlasMode(btn.dataset.mode);
  });

  $("#theme-toggle").addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    storageSet("europa-strata-theme", next);
    syncThemeColor();
  });

  $("#btn-zoom-in")?.addEventListener("click", () => bumpMapZoom(1.35));
  $("#btn-zoom-out")?.addEventListener("click", () => bumpMapZoom(1 / 1.35));
  $("#btn-zoom-reset")?.addEventListener("click", () => resetMapZoom());

  bindLegendInteractions();
  bindLightboxUi();

  // Preceded by / Succeeded by chain jumps only (no inline body auto-links)
  document.addEventListener("click", (e) => {
    const link = e.target?.closest?.(".atlas-link");
    if (!link) return;
    e.preventDefault();
    e.stopPropagation();
    const periodId = link.getAttribute("data-period");
    const iso = link.getAttribute("data-iso");
    if (periodId && iso) goToAtlasTarget({ periodId, iso });
  });

  // Browser chrome show/hide fires resize and used to rebuild the map
  // at identity zoom. Only remap when the map *width* meaningfully changes;
  // always preserve zoom if a rebuild does run.
  let resizeTimer = null;
  try {
    window.matchMedia("(min-width: 900px)").addEventListener("change", () => buildTicks());
  } catch (_) {
    /* matchMedia unavailable */
  }
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const tickWrap = $("#tick-labels");
      const tw = tickWrap?.clientWidth || 0;
      const prevTw = state._tickWrapWidth || 0;
      if (Math.abs(tw - prevTw) > 12) {
        state._tickWrapWidth = tw;
        buildTicks();
      }

      if (!state.geo) return;
      const el = $("#map");
      if (!el) return;
      const w = el.clientWidth || 0;
      const h = el.clientHeight || 0;
      const prev = state.mapPixelSize || { w: 0, h: 0 };
      const widthChanged = Math.abs(w - prev.w) > 24;
      const heightChangedALot = Math.abs(h - prev.h) > 80;
      // Ignore small height-only changes (URL bar / scroll UI)
      if (!widthChanged && !heightChangedALot) return;
      state._kingdomGeoPeriodId = null;
      initMap({ preserveZoom: true });
      if (isKingdomMode()) syncKingdomPolityLayer({ force: true });
      updateLegend();
      if (isKingdomMode() && state.selectedPolityId) {
        applyPolitySelectionClass();
      } else if (state.selectedIso) {
        state.svg
          ?.selectAll("path.country")
          .classed("is-active", (d) => d.properties.iso === state.selectedIso);
      }
    }, 220);
  });
}

async function loadKingdomPack(id) {
  try {
    // Cache-bust so refined research geometry packs reload after deploy
    const r = await fetch(withV(`data/kingdom-eras/${id}.json`));
    if (!r.ok) return null;
    const raw = await r.json();
    // v2 borders: historical-basemaps (GPL-3.0) → TopoJSON with shared arcs
    let topo = null;
    try {
      const t = await fetch(withV(`data/kingdom-eras/geo/${id}.topo.json`));
      if (t.ok && window.topojson) topo = await t.json();
    } catch (_) {
      topo = null;
    }
    return normalizeKingdomPack(raw, topo);
  } catch (_) {
    return null;
  }
}

function showFatalLoadError(message) {
  const label = $("#period-label");
  if (label) label.textContent = "Atlas unavailable";
  const copy = $("#period-copy");
  if (copy) copy.textContent = message;
  showLoadNotice(message, { retry: () => location.reload() });
}

async function init() {
  syncThemeColor();

  // D3 comes from a CDN; if it was blocked or failed, nothing below can draw.
  if (typeof window.d3 === "undefined") {
    showFatalLoadError(
      "The map library (D3) could not load. Check your connection or content blocker, then retry."
    );
    return;
  }

  let keyEventsFailed = false;
  try {
    const [timeline, geo, keyEvents] = await Promise.all([
      fetch(withV("data/timeline.json")).then((r) => {
        if (!r.ok) throw new Error("timeline");
        return r.json();
      }),
      fetch(withV("data/europe.geojson")).then((r) => {
        if (!r.ok) throw new Error("geo");
        return r.json();
      }),
      fetch(withV("data/key-events.json"))
        .then((r) => {
          if (!r.ok) throw new Error("key-events");
          return r.json();
        })
        .catch(() => {
          keyEventsFailed = true;
          return { version: 1, periods: {} };
        }),
    ]);
    state.data = timeline;
    state.geo = geo;
    state.keyEvents = keyEvents?.periods
      ? keyEvents
      : { version: 1, periods: {} };
    state.kingdomPacks = {};
  } catch (err) {
    showFatalLoadError("Could not load the atlas data. Check your connection and retry.");
    return;
  }
  if (keyEventsFailed) showLoadNotice("Key events could not load.");

  try {
    renderInitialAtlas();
  } catch (err) {
    console.error("Europa Strata failed to render", err);
    showFatalLoadError("Something went wrong while drawing the atlas. Reload to try again.");
  }
}

function renderInitialAtlas() {
  state.atlasMode = "deep-time";
  syncAtlasTabs();
  $("#map-attr").textContent = state.data.meta.mapAttribution || "";
  renderGlossary();

  buildTicks();
  bindUI();
  initMap();

  const start = state.data.periods.findIndex((p) => p.id === "beaker-corded");
  snapToPeriod(start >= 0 ? start : 0);

  // Default selection: Britain
  state.selectedRegion = "britain";
  state.selectedIso = "GBR";
  state.svg
    ?.selectAll("path.country")
    .classed("is-active", (d) => d.properties.iso === "GBR");
  renderDetail();
  highlightCultureChips();
  updateSelectionTip();
}

init().catch((err) => {
  console.error("Europa Strata failed to start", err);
  showFatalLoadError("Something went wrong while starting the atlas. Reload to try again.");
});
