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

const REGION_LABELS = {
  iberia: "Iberia",
  britain: "Britain & Ireland",
  france: "France",
  central: "Central Europe",
  scandinavia: "Scandinavia",
  italy: "Italy",
  balkans: "Balkans",
  eastern: "Eastern Europe / Steppe",
};

const SLIDER_MAX = 1000;

const state = {
  data: null,
  geo: null,
  keyEvents: { version: 1, periods: {} },
  periodIndex: 0,
  sliderPos: 0, // 0..1 continuous
  selectedIso: null,
  selectedRegion: "britain",
  path: null,
  svg: null,
  tip: null,
  zoom: null,
  zoomLayer: null,
  mapSize: { w: 900, h: 700 },
};

function $(sel) {
  return document.querySelector(sel);
}

function $$(sel) {
  return [...document.querySelectorAll(sel)];
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
  const idx = state.data.periods.findIndex((p) => p.id === target.periodId);
  if (idx < 0) return;
  state.selectedIso = target.iso;
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
      "#period-copy",
      "#period-ling",
      "#ling-note",
      "#absorb-substrate",
      "#absorb-incoming",
      "#absorb-fused",
      "#cultures-blurb",
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
  return state.data.periods[state.periodIndex];
}

function regionData(period, id) {
  return period.regions[id];
}

function isoToRegion(iso) {
  const map = state.data.meta.regionCountries || {};
  for (const [rid, list] of Object.entries(map)) {
    if (list.includes(iso)) return rid;
  }
  return null;
}

function periodIndexFromSlider(pos) {
  const n = state.data.periods.length;
  if (n <= 1) return 0;
  return Math.min(n - 1, Math.round(pos * (n - 1)));
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
      return {
        ...k,
        value,
        rangeLabel,
        detail: k.detail || k.full,
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
          return `<div class="stack-seg" style="width:${w}%;background:${e.color}" title="${escapeHtml(e.label)}: ~${Math.round(e.value)}%"></div>`;
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

function conicGradient(entries) {
  if (!entries.length) return "var(--land-base)";
  let acc = 0;
  const parts = entries.map((e) => {
    const start = acc;
    acc += e.value;
    return `${e.color} ${start}% ${acc}%`;
  });
  if (acc < 100) parts.push(`var(--land-base) ${acc}% 100%`);
  return `conic-gradient(${parts.join(", ")})`;
}

function shortPeriodName(p) {
  // Compact but full words for the secondary tick line
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
    frankish: "Frankish / Viking",
    "high-medieval": "High Medieval",
    "early-modern": "Early Modern",
    modern: "Modern",
  };
  return map[p.id] || p.label;
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
  state.mapPixelSize = { w, h };

  const projection = d3.geoAzimuthalEqualArea();

  // Open/Reset: fit clipped European land (+ east-of-Moscow & N. Africa
  // anchors) so Iceland→Black Sea / Scandinavia→Maghreb fills the stage.
  const LAND_ROTATE = [-10.5, -52];
  const LAND_PAD = [5, 12, 5, 6]; // L,T,R,B
  const LAND_BOOST = 1.03;
  const LAND_ISOS = [
    "ISL", "IRL", "GBR", "PRT", "ESP", "FRA", "AND", "BEL", "NLD", "LUX",
    "DEU", "CHE", "AUT", "ITA", "DNK", "NOR", "SWE", "FIN", "POL", "CZE",
    "SVK", "HUN", "SVN", "HRV", "BIH", "SRB", "MNE", "ALB", "MKD", "KOS",
    "ROU", "BGR", "GRC", "MDA", "UKR", "BLR", "LTU", "LVA", "EST", "TUR",
  ];
  const mainland = state.geo.features
    .filter((f) => LAND_ISOS.includes(f.properties.iso))
    .map(clipFeatureToEurope)
    .filter(Boolean);
  const land = {
    type: "FeatureCollection",
    features: [
      ...mainland,
      // East-of-Moscow / Black Sea / Maghreb anchors (RUS polygon is too huge)
      {
        type: "Feature",
        properties: { iso: "_anchor_moscow_e" },
        geometry: { type: "Point", coordinates: [40.5, 55.8] },
      },
      {
        type: "Feature",
        properties: { iso: "_anchor_black_sea_e" },
        geometry: { type: "Point", coordinates: [41.5, 42.5] },
      },
      {
        type: "Feature",
        properties: { iso: "_anchor_maghreb" },
        geometry: { type: "Point", coordinates: [-5.8, 35.4] },
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
  projection.translate([t0[0], t0[1] + 2]);
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
      if (state.selectedIso) updateSelectionTip();
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
    .duration(320)
    .ease(d3.easeCubicOut)
    .call(state.zoom.transform, d3.zoomIdentity);
}

function bumpMapZoom(factor) {
  if (!state.svg || !state.zoom) return;
  state.svg
    .transition()
    .duration(220)
    .ease(d3.easeCubicOut)
    .call(state.zoom.scaleBy, factor);
}

function paintMap(animate = true) {
  if (!state.svg) return;
  const paths = state.svg.selectAll("path.country");
  paths.each(function (d) {
    const iso = d.properties.iso;
    const style = interpolatedCountryStyle(iso, state.sliderPos);
    const node = d3.select(this);
    const fill = style.fill || "var(--land-base)";
    const opacity = style.fill ? Math.max(0.35, style.opacity) : 1;
    if (animate) {
      node
        .transition()
        .duration(420)
        .ease(d3.easeCubicOut)
        .style("fill", fill)
        .style("fill-opacity", opacity);
    } else {
      node.style("fill", fill).style("fill-opacity", opacity);
    }
  });
}

function culturesForIso(iso) {
  const style = interpolatedCountryStyle(iso, state.sliderPos);
  const labels = (style.labels || []).map((l) => l.label).filter(Boolean);
  return labels;
}

function tipHtml(name, cultures) {
  const line = cultures.length ? cultures.join(" · ") : "—";
  return `<strong>${escapeHtml(name)}</strong><span class="map-tip-cultures">${escapeHtml(line)}</span>`;
}

/** Pin tip on selected country; culture line follows the slider. */
function updateSelectionTip() {
  if (!state.tip || !state.svg || !state.selectedIso || !state.geo) return;
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

function onCountryEnter(event, d) {
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
  const iso = d.properties.iso;
  state.selectedIso = iso;
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
  slider.style.setProperty("--slider-pct", `${state.sliderPos * 100}%`);

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

  // Selected country's groups follow the slider continuously
  if (state.selectedIso) {
    updateSelectionTip();
    updateSelectedHorizonLive();
  }

  $$(".ticks .tick").forEach((el, i) => {
    el.classList.toggle("active", i === state.periodIndex);
  });
  updateTickCaption();
}

function updateTickCaption() {
  const el = $("#tick-caption");
  if (!el) return;
  const period = currentPeriod();
  el.textContent = shortPeriodName(period);
}

function snapToPeriod(index) {
  const n = state.data.periods.length;
  const pos = n <= 1 ? 0 : index / (n - 1);
  setSliderPos(pos);
}

function formatYearUi(s) {
  // Prefer BC / AD in the UI (data may still say BCE / CE)
  return String(s || "")
    .replace(/\bBCE\b/g, "BC")
    .replace(/\bCE\b/g, "AD");
}

function periodKeyEventsPack(periodId) {
  return state.keyEvents?.periods?.[periodId] || null;
}

/** All key events for a period, or place-filtered by ISO / atlas region. */
function eventsForPeriod(periodId, { iso = null, region = null, placeOnly = false } = {}) {
  const pack = periodKeyEventsPack(periodId);
  const list = pack?.keyEvents || [];
  if (!list.length) return [];
  if (!placeOnly) return list;
  if (!iso && !region) return [];
  return list.filter((e) => {
    if (iso && e.iso && e.iso === iso) return true;
    const regs = e.regions || (e.region ? [e.region] : []);
    if (region && regs.includes(region)) return true;
    return false;
  });
}

function keyEventTeaser(ev) {
  if (ev.teaser) return String(ev.teaser);
  if (ev.title) return String(ev.title);
  const raw = String(ev.text || ev.detail || "");
  const cut = raw.split(/(?<=[.!?])\s+/)[0] || raw;
  return cut.length > 140 ? cut.slice(0, 137).trimEnd() + "…" : cut;
}

function keyEventDetail(ev) {
  return String(ev.detail || ev.text || "").trim();
}

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
      summary.appendChild(document.createTextNode(" — "));
    }
    const teaser = document.createElement("span");
    teaser.className = "key-events-teaser";
    teaser.textContent = keyEventTeaser(ev);
    summary.appendChild(teaser);
    details.appendChild(summary);

    const detailText = keyEventDetail(ev);
    if (detailText) {
      const body = document.createElement("div");
      body.className = "key-events-body";
      // Preserve paragraph breaks from enriched detail
      for (const para of detailText.split(/\n\n+/)) {
        const p = document.createElement("p");
        p.textContent = para.trim();
        if (p.textContent) body.appendChild(p);
      }
      details.appendChild(body);
    }

    li.appendChild(details);
    listEl.appendChild(li);
  }
}

function renderPeriodKeyEvents() {
  const period = currentPeriod();
  const section = $("#period-key-events");
  const listEl = $("#period-key-events-list");
  if (!section || !listEl) return;
  const events = eventsForPeriod(period.id, { placeOnly: false });
  if (!events.length) {
    section.hidden = true;
    listEl.replaceChildren();
    return;
  }
  renderKeyEventsList(listEl, events);
  section.hidden = false;
}

function renderPlaceKeyEvents() {
  const period = currentPeriod();
  const section = $("#place-key-events");
  const listEl = $("#place-key-events-list");
  if (!section || !listEl) return;
  const region =
    state.selectedRegion ||
    (state.selectedIso ? isoToRegion(state.selectedIso) : null);
  const events = eventsForPeriod(period.id, {
    iso: state.selectedIso,
    region,
    placeOnly: true,
  });
  if (!events.length) {
    section.hidden = true;
    listEl.replaceChildren();
    return;
  }
  renderKeyEventsList(listEl, events);
  section.hidden = false;
}

function renderPeriodText() {
  const period = currentPeriod();
  const yearEl = $("#period-year");
  const labelEl = $("#period-label");
  if (yearEl) yearEl.textContent = formatYearUi(period.tickYear || period.yearLabel);
  if (labelEl) labelEl.textContent = period.label;
  $("#period-era").textContent = period.era || "";
  $("#period-copy").textContent = period.narrative;
  const ling = $("#period-ling");
  if (period.linguistics) {
    ling.hidden = false;
    ling.textContent = period.linguistics;
  } else {
    ling.hidden = true;
  }
  renderPeriodKeyEvents();
}

function clearLegacyLayoutStorage() {
  try {
    localStorage.removeItem("europa-strata-layout-override");
    localStorage.removeItem("europa-strata-layout");
  } catch (_) {
    /* ignore */
  }
}

function updateLegend() {
  const period = currentPeriod();
  const layers = period.mapLayers || [];
  const box = $("#map-legend");
  if (!box) return;
  // Always visible under the slider — never overlays the map
  box.hidden = false;
  box.innerHTML = layers
    .map(
      (l) =>
        `<div class="legend-row"><span class="legend-swatch" style="background:${l.color}"></span>${escapeHtml(l.label)}</div>`
    )
    .join("");
}

function renderGlossary() {
  const grid = $("#glossary-grid");
  if (!grid) return;
  const items = state.data.meta.glossary || [];
  grid.innerHTML = items
    .map(
      (g) =>
        `<dl class="glossary-item"><dt><a class="glossary-link" href="ancestry.html#${escapeHtml(g.id)}">${escapeHtml(g.term)}</a> <span>· ${escapeHtml(g.name)}</span></dt><dd>${escapeHtml(g.text)}</dd></dl>`
    )
    .join("");
}

function updateCulturesRail() {
  const period = currentPeriod();
  const layers = period.mapLayers || [];
  const rail = $("#cultures-rail");
  rail.innerHTML = layers
    .map(
      (l) =>
        `<button type="button" class="culture-chip" data-layer="${escapeHtml(l.id)}">${escapeHtml(l.label)}</button>`
    )
    .join("");
  rail.querySelectorAll(".culture-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      const layer = layers.find((l) => l.id === btn.dataset.layer);
      if (!layer?.countries?.length) return;
      // Select first country of layer in a known region
      const iso = layer.countries.find((c) => isoToRegion(c));
      if (!iso) return;
      state.selectedIso = iso;
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
  const iso = state.selectedIso;
  const style = iso ? countryStyleForPeriod(period, iso) : { labels: [] };
  const ids = new Set((style.labels || []).map((l) => l.id));
  $$(".culture-chip").forEach((chip) => {
    chip.classList.toggle("is-focus", ids.has(chip.dataset.layer));
  });
}

function setPolityField(key, value) {
  const block = $(`#polity-${key}-block`);
  const el = $(`#polity-${key}`);
  if (!block || !el) return;
  const text = (value || "").trim();
  block.hidden = !text;
  setPlainText(el, text);
}

function figureHtml(img) {
  const alt = escapeHtml(img.alt || img.caption || "Historical image");
  const caption = escapeHtml(img.caption || "");
  const src = escapeHtml(img.src);
  return `<figure class="polity-figure">
    <button type="button" class="polity-figure-open" data-full-src="${src}" data-caption="${caption}" data-alt="${alt}" aria-label="View larger: ${alt}">
      <img src="${src}" alt="${alt}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.closest('figure')?.remove()" />
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
    if (e.key === "Escape") closeLightbox();
  });
}

function inferImageRole(img) {
  if (img?.role) return img.role;
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
    /book|manuscript|folio|thes|print|tapestry|chronicle|poem|poetry|saga|text|letter|codex|quill|dante|shakespeare|cervantes|monet|meninas|venus|fresco|miniature|joan/.test(
      t
    )
  ) {
    return "literature";
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

/** Route images into leaders / religion / literature / art galleries */
function renderPolityGalleries(images) {
  const buckets = {
    leader: [],
    religion: [],
    literature: [],
    art: [],
  };
  const list = Array.isArray(images) ? images.filter((img) => img && img.src) : [];
  list.forEach((img) => {
    const role = inferImageRole(img);
    (buckets[role] || buckets.art).push(img);
  });

  fillInlineGallery($("#polity-leaders-gallery"), buckets.leader);
  fillInlineGallery($("#polity-religion-gallery"), buckets.religion);
  fillInlineGallery($("#polity-literature-gallery"), buckets.literature);
  fillInlineGallery($("#polity-art-gallery"), buckets.art);

  const show = (id, has) => {
    const block = $(id);
    if (!block) return;
    const textEl = block.querySelector("p:not(.kicker)");
    const hasText = !!(textEl?.textContent || "").trim();
    block.hidden = !(has || hasText);
  };
  show("#polity-leaders-block", buckets.leader.length > 0);
  show("#polity-religion-block", buckets.religion.length > 0);
  show("#polity-literature-block", buckets.literature.length > 0);
  show("#polity-art-block", buckets.art.length > 0);
}

function renderDetail() {
  const period = currentPeriod();
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
  let horizon = region.culture;
  if (state.selectedIso) {
    const cov = countryStyleForPeriod(period, state.selectedIso);
    const names = (cov.labels || []).map((l) => l.label).filter(Boolean);
    if (names.length) horizon = names.join(" · ");
  }
  setPlainText($("#culture-title"), horizon);
  const horizonEl = $("#culture-horizon");
  if (horizonEl) {
    const first = horizon.split(" · ")[0];
    horizonEl.textContent =
      first && first !== region.culture
        ? `Regional horizon · ${region.culture}`
        : state.selectedIso && horizon !== region.culture
          ? "Map layers here"
          : "Cultural horizon";
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
  setPlainText($("#culture-desc"), desc);

  // Polity-specific panel
  const polityPanel = $("#polity-panel");
  const polity =
    state.selectedIso && period.polities
      ? period.polities[state.selectedIso]
      : null;
  if (polityPanel) {
    if (polity) {
      polityPanel.hidden = false;
      setPlainText($("#polity-name"), polity.name || "—");
      setPlainText($("#polity-summary"), polity.summary || "");
      setPlainText($("#polity-conflicts"), polity.conflicts || "");
      setPolityField("leaders", polity.leaders);
      setPolityField("religion", polity.religion);
      setPolityField("culture", polity.culture);
      setPolityField("story", polity.story);
      setPolityField("literature", polity.literature);
      setPolityField("art", polity.art);
      renderPolityChain(polity);
      renderPolityGalleries(polity.images);
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
  renderPlaceKeyEvents();
  renderPeriodKeyEvents();

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
      return `<div class="stack-seg" style="width:${e.value}%;background:${e.color}" title="${escapeHtml(tip)}"></div>`;
    })
    .join("");

  // Legend omitted — pie-list shows label + % tightly (no triple display)
  const legendEl = $("#ancestry-legend");
  if (legendEl) legendEl.innerHTML = "";

  $("#pie").style.background = conicGradient(entries);
  $("#pie-list").innerHTML = entries
    .map((e) => {
      const pct = e.rangeLabel || `~${Math.round(e.value)}%`;
      return `<li title="${escapeHtml(e.detail)}" style="--swatch:${escapeHtml(e.color)}"><strong>${escapeHtml(e.label)}</strong><span class="pct">${escapeHtml(pct)}</span></li>`;
    })
    .join("");
  // Ensure legend stays empty / hidden
  if (legendEl) {
    legendEl.hidden = true;
    legendEl.setAttribute("aria-hidden", "true");
  }

  renderAncestryCline(region, keys);
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

function buildTicks() {
  const wrap = $("#tick-labels");
  wrap.innerHTML = state.data.periods
    .map((p, i) => {
      const year = formatYearUi(p.tickYear || p.yearLabel);
      const { num, era } = splitTickYear(year);
      const name = shortPeriodName(p);
      const title = `${formatYearUi(p.yearLabel)} — ${name}`;
      return `<button type="button" class="tick" data-i="${i}" title="${escapeHtml(title)}"><span class="tick-num">${escapeHtml(num)}</span><span class="tick-era">${escapeHtml(era)}</span></button>`;
    })
    .join("");
  wrap.querySelectorAll(".tick").forEach((el) => {
    el.addEventListener("click", () => snapToPeriod(Number(el.dataset.i)));
  });
  updateTickCaption();
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
    snapToPeriod(Math.min(state.data.periods.length - 1, state.periodIndex + 1))
  );

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") snapToPeriod(Math.max(0, state.periodIndex - 1));
    if (e.key === "ArrowRight")
      snapToPeriod(Math.min(state.data.periods.length - 1, state.periodIndex + 1));
  });

  $("#theme-toggle").addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    localStorage.setItem("europa-strata-theme", next);
  });

  $("#btn-zoom-in")?.addEventListener("click", () => bumpMapZoom(1.35));
  $("#btn-zoom-out")?.addEventListener("click", () => bumpMapZoom(1 / 1.35));
  $("#btn-zoom-reset")?.addEventListener("click", () => resetMapZoom());

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
  window.addEventListener("resize", () => {
    if (!state.geo) return;
    clearTimeout(window.__strataResize);
    window.__strataResize = setTimeout(() => {
      const el = $("#map");
      if (!el) return;
      const w = el.clientWidth || 0;
      const h = el.clientHeight || 0;
      const prev = state.mapPixelSize || { w: 0, h: 0 };
      const widthChanged = Math.abs(w - prev.w) > 24;
      const heightChangedALot = Math.abs(h - prev.h) > 80;
      // Ignore small height-only changes (URL bar / scroll UI)
      if (!widthChanged && !heightChangedALot) return;
      initMap({ preserveZoom: true });
      updateLegend();
      if (state.selectedIso) {
        state.svg
          ?.selectAll("path.country")
          .classed("is-active", (d) => d.properties.iso === state.selectedIso);
      }
    }, 220);
  });
}

async function init() {
  const saved = localStorage.getItem("europa-strata-theme");
  if (saved === "dark" || saved === "light") {
    document.documentElement.setAttribute("data-theme", saved);
  }
  clearLegacyLayoutStorage();

  try {
    const [timeline, geo, keyEvents] = await Promise.all([
      fetch("data/timeline.json").then((r) => {
        if (!r.ok) throw new Error("timeline");
        return r.json();
      }),
      fetch("data/europe.geojson").then((r) => {
        if (!r.ok) throw new Error("geo");
        return r.json();
      }),
      fetch("data/key-events.json")
        .then((r) => (r.ok ? r.json() : { version: 1, periods: {} }))
        .catch(() => ({ version: 1, periods: {} })),
    ]);
    state.data = timeline;
    state.geo = geo;
    state.keyEvents = keyEvents?.periods
      ? keyEvents
      : { version: 1, periods: {} };
  } catch (err) {
    console.error(err);
    $("#period-copy").textContent =
      "Could not load map data. Serve this folder over HTTP (python3 -m http.server).";
    return;
  }

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

init();
