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

function shortTick(p) {
  const map = {
    mesolithic: "Meso",
    "early-neolithic": "EN",
    "middle-neolithic": "MN",
    yamnaya: "Yam",
    "beaker-corded": "CW",
    "nordic-bronze": "NBA",
    "iron-age": "Iron",
    classical: "Rome",
    migration: "Migr",
    frankish: "Frank",
    "high-medieval": "Med",
    "early-modern": "EM",
    modern: "Now",
  };
  return map[p.id] || p.label.slice(0, 4);
}

/* ——— Map ——— */

function initMap() {
  const el = $("#map");
  const w = el.clientWidth || 900;
  const h = el.clientHeight || 700;

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

  // Europe-focused projection
  const projection = d3
    .geoAzimuthalEqualArea()
    .rotate([-10, -52])
    .fitExtent(
      [
        [24, 28],
        [w - 16, h - 20],
      ],
      state.geo
    );

  state.path = d3.geoPath(projection);

  const g = svg.append("g").attr("class", "countries");

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

  paintMap(false);
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

  $$(".ticks span").forEach((el, i) => {
    el.classList.toggle("active", i === state.periodIndex);
  });
}

function snapToPeriod(index) {
  const n = state.data.periods.length;
  const pos = n <= 1 ? 0 : index / (n - 1);
  setSliderPos(pos);
}

function renderPeriodText() {
  const period = currentPeriod();
  $("#period-label").textContent = period.label;
  $("#period-year").textContent = period.yearLabel;
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

function updateLegend() {
  const period = currentPeriod();
  const layers = period.mapLayers || [];
  const box = $("#map-legend");
  box.innerHTML = layers
    .slice(0, 7)
    .map(
      (l) =>
        `<div class="legend-row"><span class="legend-swatch" style="background:${l.color}"></span>${escapeHtml(l.label)}</div>`
    )
    .join("");

  const roles = [...new Set(layers.map((l) => l.role))];
  $("#mode-row").innerHTML = roles
    .map((r) => `<span class="role-chip" data-role="${r}">${r}</span>`)
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
  $("#detail-kicker").textContent = `${place} · ${period.yearLabel}`;
  $("#culture-title").textContent = region.culture;

  // Map layers covering selection
  if (state.selectedIso) {
    const cov = countryStyleForPeriod(period, state.selectedIso);
    if (cov.labels?.length) {
      const top = cov.labels[0];
      $("#culture-title").textContent = `${top.label}`;
      // Keep regional culture as secondary context in description head
    }
  }

  const modeEl = $("#mode-pill");
  modeEl.textContent = region.mode;
  modeEl.dataset.mode = region.mode;
  modeEl.title = modeLegend[region.mode] || "";

  let desc = region.description;
  if (state.selectedIso) {
    const cov = countryStyleForPeriod(period, state.selectedIso);
    const layerBits = (cov.labels || [])
      .map((l) => `${l.label} (${l.role})`)
      .join("; ");
    if (layerBits) {
      desc = `On the map here: ${layerBits}. ${region.description}`;
    }
  }
  $("#culture-desc").textContent = desc;

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

function buildTicks() {
  const wrap = $("#tick-labels");
  wrap.innerHTML = state.data.periods
    .map((p, i) => `<span data-i="${i}" title="${p.yearLabel}">${shortTick(p)}</span>`)
    .join("");
  wrap.querySelectorAll("span").forEach((el) => {
    el.addEventListener("click", () => snapToPeriod(Number(el.dataset.i)));
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

  window.addEventListener("resize", () => {
    if (!state.geo) return;
    clearTimeout(window.__strataResize);
    window.__strataResize = setTimeout(() => initMap(), 180);
  });
}

async function init() {
  const saved = localStorage.getItem("europa-strata-theme");
  if (saved === "dark" || saved === "light") {
    document.documentElement.setAttribute("data-theme", saved);
  }

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
