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

function ancestryEntries(region, keys) {
  const a = region.ancestry || {};
  return keys
    .map((k) => ({
      ...k,
      value: Number(a[k.id]) || 0,
      detail: k.detail || k.full,
    }))
    .filter((k) => k.value > 0);
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

  const mobile = isMobileLayout();
  const projection = d3.geoAzimuthalEqualArea();

  // Mobile open/Reset: fit clipped European land (+ east-of-Moscow & N. Africa
  // anchors) so Iceland→Black Sea / Scandinavia→Maghreb fills the stage —
  // matching the reference phone screenshot. Desktop uses a simple bbox.
  let fitMeta;
  if (mobile) {
    const MOBILE_ROTATE = [-10.5, -52];
    const MOBILE_PAD = [5, 12, 5, 6]; // L,T,R,B
    const MOBILE_BOOST = 1.03;
    const MOBILE_ISOS = [
      "ISL", "IRL", "GBR", "PRT", "ESP", "FRA", "AND", "BEL", "NLD", "LUX",
      "DEU", "CHE", "AUT", "ITA", "DNK", "NOR", "SWE", "FIN", "POL", "CZE",
      "SVK", "HUN", "SVN", "HRV", "BIH", "SRB", "MNE", "ALB", "MKD", "KOS",
      "ROU", "BGR", "GRC", "MDA", "UKR", "BLR", "LTU", "LVA", "EST", "TUR",
    ];
    const mainland = state.geo.features
      .filter((f) => MOBILE_ISOS.includes(f.properties.iso))
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
    projection.rotate(MOBILE_ROTATE).fitExtent(
      [
        [MOBILE_PAD[0], MOBILE_PAD[1]],
        [w - MOBILE_PAD[2], h - MOBILE_PAD[3]],
      ],
      land
    );
    const baseScale = projection.scale();
    projection.scale(baseScale * MOBILE_BOOST);
    const t0 = projection.translate();
    projection.translate([t0[0], t0[1] + 2]);
    fitMeta = {
      mode: "mobile-land",
      rotate: MOBILE_ROTATE,
      pad: MOBILE_PAD,
      boost: MOBILE_BOOST,
      baseScale,
      scale: projection.scale(),
      translate: projection.translate(),
      stage: [w, h],
    };
  } else {
    const DESKTOP_ROTATE = [-14.5, -52];
    const DESKTOP_BOOST = 1.22;
    const europeFrame = {
      type: "Feature",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-12, 35.5],
            [40, 35.5],
            [40, 62],
            [-12, 62],
            [-12, 35.5],
          ],
        ],
      },
    };
    projection.rotate(DESKTOP_ROTATE).fitExtent(
      [
        [16, 14],
        [w - 16, h - 14],
      ],
      europeFrame
    );
    const baseScale = projection.scale();
    projection.scale(baseScale * DESKTOP_BOOST);
    const t0 = projection.translate();
    projection.translate([t0[0] - w * 0.01, t0[1] + h * 0.015]);
    fitMeta = {
      mode: "desktop-bbox",
      rotate: DESKTOP_ROTATE,
      boost: DESKTOP_BOOST,
      baseScale,
      scale: projection.scale(),
      translate: projection.translate(),
      stage: [w, h],
    };
  }
  state.mapFit = fitMeta;

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
      // Never steal taps from layout / zoom chrome
      const t = event.target;
      if (t && t.closest && t.closest(".layout-toggle, .map-tools, .map-chrome")) {
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

function onCountryEnter(event, d) {
  d3.select(this).classed("is-hover", true);
  const iso = d.properties.iso;
  const style = interpolatedCountryStyle(iso, state.sliderPos);
  const cultures = (style.labels || []).map((l) => l.label).join(" · ") || "—";
  state.tip
    .style("opacity", 1)
    .html(
      `<strong>${escapeHtml(d.properties.name)}</strong>${escapeHtml(cultures)}`
    );
}

function onCountryMove(event) {
  const stage = $("#map-stage").getBoundingClientRect();
  state.tip
    .style("left", `${event.clientX - stage.left}px`)
    .style("top", `${event.clientY - stage.top}px`);
}

function onCountryLeave() {
  d3.select(this).classed("is-hover", false);
  state.tip.style("opacity", 0);
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
  } else {
    // soft update year blend feel — still show nearest period text
    renderPeriodText();
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
}

const LAYOUT_MQ = "(max-width: 960px)";
const LAYOUT_OVERRIDE_KEY = "europa-strata-layout-override";

function isNarrowViewport() {
  return window.matchMedia(LAYOUT_MQ).matches;
}

function deviceLayout() {
  return isNarrowViewport() ? "mobile" : "desktop";
}

function layoutOverride() {
  const o = localStorage.getItem(LAYOUT_OVERRIDE_KEY);
  return o === "mobile" || o === "desktop" ? o : null;
}

/** True when phone layout is active (override or viewport). */
function isMobileLayout() {
  return document.documentElement.getAttribute("data-layout") === "mobile";
}

function syncLayoutToggle() {
  const btn = $("#layout-toggle");
  if (!btn) return;
  const mobile = isMobileLayout();
  const overridden = !!layoutOverride();
  btn.setAttribute("aria-pressed", mobile ? "true" : "false");
  // Quiet label: offer the other mode
  btn.textContent = mobile ? "Desktop" : "Mobile";
  btn.title = overridden
    ? `Using ${mobile ? "mobile" : "desktop"} layout (tap to switch; clears when you choose the other). First visits follow your screen size.`
    : `Layout follows this device (${mobile ? "mobile" : "desktop"}). Tap for ${mobile ? "desktop" : "mobile"}.`;
  btn.dataset.override = overridden ? "1" : "0";
}

function applyLayout(mode, { remap = true } = {}) {
  const next = mode === "mobile" ? "mobile" : "desktop";
  document.documentElement.setAttribute("data-layout", next);
  document.body.classList.toggle("is-mobile-layout", next === "mobile");
  document.body.classList.toggle("is-desktop-layout", next === "desktop");
  syncLayoutToggle();
  if (remap && state.geo) {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        try {
          initMap();
          updateLegend();
          if (state.selectedIso) {
            state.svg
              ?.selectAll("path.country")
              .classed(
                "is-active",
                (d) => d.properties.iso === state.selectedIso
              );
          }
          if (state.mapFit) {
            console.info("[europa-strata] map fit", state.mapFit);
          }
        } catch (err) {
          console.error("layout remap failed", err);
        }
      });
    });
  }
}

function initLayoutPreference() {
  // Drop legacy forced key so returning users get normal responsive behavior
  try {
    localStorage.removeItem("europa-strata-layout");
  } catch (_) {
    /* ignore */
  }
  applyLayout(layoutOverride() || deviceLayout(), { remap: false });

  const mq = window.matchMedia(LAYOUT_MQ);
  const onViewport = () => {
    if (layoutOverride()) return; // manual override wins until changed
    applyLayout(deviceLayout(), { remap: !!state.geo });
  };
  if (mq.addEventListener) mq.addEventListener("change", onViewport);
  else if (mq.addListener) mq.addListener(onViewport);
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
    .map((g) => {
      const tip = g.phenotype
        ? ` title="${escapeHtml(g.phenotype)}"`
        : "";
      return `<dl class="glossary-item"${tip}><dt><a class="glossary-link" href="ancestry.html#${escapeHtml(g.id)}">${escapeHtml(g.term)}</a> <span>· ${escapeHtml(g.name)}</span></dt><dd>${escapeHtml(g.text)}</dd></dl>`;
    })
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
  el.textContent = text;
}

function figureHtml(img) {
  const alt = escapeHtml(img.alt || img.caption || "Historical image");
  const caption = escapeHtml(img.caption || "");
  const src = escapeHtml(img.src);
  return `<figure class="polity-figure">
    <img src="${src}" alt="${alt}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.closest('figure')?.remove()" />
    <figcaption>${caption}</figcaption>
  </figure>`;
}

function isLiteraryImage(img) {
  const t = `${img.caption || ""} ${img.alt || ""} ${img.src || ""}`.toLowerCase();
  return /book|kells|manuscript|folio|bible|thes|print|tapestry|chronicle|poem|poetry|saga|gospel|psalter|text|letter|codex|quill|dante|shakespeare|cervantes|luther|monet|night watch|meninas|venus|rublev|icon|pantocrator|fresco|miniature|joan/.test(
    t
  );
}

function fillInlineGallery(el, images) {
  if (!el) return;
  const list = (images || []).filter((img) => img && img.src);
  el.innerHTML = list.map(figureHtml).join("");
  el.hidden = !list.length;
}

/** Split images into literature vs art sections — no separate gallery heading */
function renderPolityGalleries(images) {
  const litGal = $("#polity-literature-gallery");
  const artGal = $("#polity-art-gallery");
  const list = Array.isArray(images) ? images.filter((img) => img && img.src) : [];
  if (!list.length) {
    fillInlineGallery(litGal, []);
    fillInlineGallery(artGal, []);
    return;
  }
  const literary = [];
  const material = [];
  list.forEach((img) => {
    if (isLiteraryImage(img)) literary.push(img);
    else material.push(img);
  });
  // Keep at least one image under art when everything looked "literary"
  if (!material.length && literary.length > 1) {
    material.push(literary.pop());
  }
  if (!material.length && literary.length === 1 && !($("#polity-art")?.textContent || "").trim()) {
    // art section empty — leave image with literature
  } else if (!material.length && literary.length) {
    material.push(literary.pop());
  }
  fillInlineGallery(litGal, literary);
  fillInlineGallery(artGal, material);

  // If a section has images but no text, still show the block
  const litBlock = $("#polity-literature-block");
  const artBlock = $("#polity-art-block");
  if (litBlock && literary.length) litBlock.hidden = false;
  if (artBlock && material.length) artBlock.hidden = false;
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

  // Overall culture horizon from map layer
  let horizon = region.culture;
  if (state.selectedIso) {
    const cov = countryStyleForPeriod(period, state.selectedIso);
    if (cov.labels?.length) horizon = cov.labels[0].label;
  }
  $("#culture-title").textContent = horizon;
  const horizonEl = $("#culture-horizon");
  if (horizonEl) {
    horizonEl.textContent =
      horizon !== region.culture ? `Regional horizon · ${region.culture}` : "Cultural horizon";
  }

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
  $("#culture-desc").textContent = desc;

  // Polity-specific panel
  const polityPanel = $("#polity-panel");
  const polity =
    state.selectedIso && period.polities
      ? period.polities[state.selectedIso]
      : null;
  if (polityPanel) {
    if (polity) {
      polityPanel.hidden = false;
      $("#polity-name").textContent = polity.name || "—";
      $("#polity-summary").textContent = polity.summary || "";
      $("#polity-conflicts").textContent = polity.conflicts || "";
      setPolityField("leaders", polity.leaders);
      setPolityField("religion", polity.religion);
      setPolityField("culture", polity.culture);
      setPolityField("story", polity.story);
      setPolityField("literature", polity.literature);
      setPolityField("art", polity.art);
      renderPolityGalleries(polity.images);
    } else {
      polityPanel.hidden = true;
      renderPolityGalleries(null);
    }
  }

  const note = $("#ancestry-note");
  if (region.ancestryNote) {
    note.hidden = false;
    note.textContent = region.ancestryNote;
  } else {
    note.hidden = true;
  }

  $("#absorb-substrate").textContent = region.substrate || "—";
  $("#absorb-incoming").textContent = region.incoming || "—";
  $("#absorb-fused").textContent = region.fused || "—";

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
    .map(
      (e) =>
        `<div class="stack-seg" style="width:${e.value}%;background:${e.color}" title="${escapeHtml(e.detail)}: ~${e.value}%"></div>`
    )
    .join("");

  $("#ancestry-legend").innerHTML = entries
    .map(
      (e) =>
        `<div class="legend-item" title="${escapeHtml(e.detail)}"><span class="swatch" style="background:${e.color}"></span>${e.label} · ~${e.value}%</div>`
    )
    .join("");

  $("#pie").style.background = conicGradient(entries);
  $("#pie-list").innerHTML = entries
    .map(
      (e) =>
        `<li title="${escapeHtml(e.detail)}"><span><strong>${escapeHtml(e.label)}</strong></span><span class="pct">~${e.value}%</span></li>`
    )
    .join("");

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

  const layoutBtn = $("#layout-toggle");
  if (layoutBtn) {
    let lastToggle = 0;
    layoutBtn.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const now = Date.now();
      if (now - lastToggle < 400) return;
      lastToggle = now;
      const next = isMobileLayout() ? "desktop" : "mobile";
      try {
        // Persist only an explicit override; choosing the device default clears it
        if (next === deviceLayout()) localStorage.removeItem(LAYOUT_OVERRIDE_KEY);
        else localStorage.setItem(LAYOUT_OVERRIDE_KEY, next);
      } catch (_) {
        /* ignore */
      }
      applyLayout(next, { remap: true });
    });
  }

  // Mobile browser chrome show/hide fires resize and used to rebuild the map
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
  initLayoutPreference();

  try {
    const [timeline, geo] = await Promise.all([
      fetch("data/timeline.json").then((r) => {
        if (!r.ok) throw new Error("timeline");
        return r.json();
      }),
      fetch("data/europe.geojson").then((r) => {
        if (!r.ok) throw new Error("geo");
        return r.json();
      }),
    ]);
    state.data = timeline;
    state.geo = geo;
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
}

init();
