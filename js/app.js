/* Europa Strata — timeline-driven map + ancestry absorption UI */

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

const state = {
  data: null,
  periodIndex: 0,
  selectedRegion: "britain",
};

async function loadData() {
  const res = await fetch("data/timeline.json");
  if (!res.ok) throw new Error("Failed to load timeline.json");
  return res.json();
}

function $(sel) {
  return document.querySelector(sel);
}

function $$(sel) {
  return [...document.querySelectorAll(sel)];
}

function currentPeriod() {
  return state.data.periods[state.periodIndex];
}

function regionData(period, id) {
  return period.regions[id];
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
  if (!entries.length) return "#1a1a1a";
  let acc = 0;
  const parts = entries.map((e) => {
    const start = acc;
    acc += e.value;
    return `${e.color} ${start}% ${acc}%`;
  });
  if (acc < 100) parts.push(`#2a2a2a ${acc}% 100%`);
  return `conic-gradient(${parts.join(", ")})`;
}

function setPeriod(index, { animate = true } = {}) {
  const periods = state.data.periods;
  state.periodIndex = Math.max(0, Math.min(periods.length - 1, index));
  const period = currentPeriod();

  const label = $("#period-label");
  const year = $("#period-year");
  const era = $("#period-era");
  const copy = $("#period-copy");
  const slider = $("#time-slider");

  if (animate) {
    label.style.opacity = "0";
    label.style.transform = "translateY(6px)";
    copy.style.opacity = "0";
  }

  const applyText = () => {
    label.textContent = period.label;
    year.textContent = period.yearLabel;
    era.textContent = period.era || "";
    copy.textContent = period.narrative;
    const ling = $("#period-ling");
    if (ling) {
      if (period.linguistics) {
        ling.hidden = false;
        ling.textContent = `Languages: ${period.linguistics}`;
      } else {
        ling.hidden = true;
        ling.textContent = "";
      }
    }
    label.style.opacity = "1";
    label.style.transform = "translateY(0)";
    copy.style.opacity = "1";
  };

  if (animate) {
    requestAnimationFrame(() => setTimeout(applyText, 120));
  } else {
    applyText();
  }

  slider.value = String(state.periodIndex);
  $$(".tick-labels span").forEach((el, i) => {
    el.classList.toggle("active", i === state.periodIndex);
  });

  // Map fills
  REGION_IDS.forEach((id) => {
    const r = regionData(period, id);
    const el = document.getElementById(`region-${id}`);
    if (!el || !r) return;
    el.style.fill = r.color;
    el.dataset.culture = r.culture;
    el.dataset.mode = r.mode;
    if (animate) {
      el.classList.remove("just-changed");
      void el.offsetWidth;
      el.classList.add("just-changed");
    }
  });

  updateCulturesRail(period);
  renderDetail();
}

function updateCulturesRail(period) {
  const rail = $("#cultures-rail");
  if (!rail) return;
  const names = REGION_IDS.map((id) => regionData(period, id)?.culture).filter(Boolean);
  const unique = [...new Set(names)];
  rail.innerHTML = unique
    .map((name) => {
      const regionId = REGION_IDS.find((id) => regionData(period, id)?.culture === name);
      return `<button type="button" class="culture-chip" data-region="${regionId}">${escapeHtml(name)}</button>`;
    })
    .join("");
  rail.querySelectorAll(".culture-chip").forEach((btn) => {
    btn.addEventListener("click", () => selectRegion(btn.dataset.region));
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function selectRegion(id) {
  if (!REGION_IDS.includes(id)) return;
  state.selectedRegion = id;

  REGION_IDS.forEach((rid) => {
    const el = document.getElementById(`region-${rid}`);
    if (!el) return;
    el.classList.toggle("is-active", rid === id);
    el.classList.toggle("is-dim", rid !== id);
  });

  $$(".culture-chip").forEach((chip) => {
    chip.classList.toggle("is-focus", chip.dataset.region === id);
  });

  renderDetail();
}

function renderDetail() {
  const period = currentPeriod();
  const region = regionData(period, state.selectedRegion);
  if (!region) return;

  const keys = state.data.meta.ancestryKeys;
  const modeLegend = state.data.meta.modeLegend || {};
  const entries = ancestryEntries(region, keys);

  $("#detail-kicker").textContent = `${REGION_LABELS[state.selectedRegion]} · ${period.yearLabel}`;
  $("#culture-title").textContent = region.culture;
  const modeEl = $("#mode-pill");
  modeEl.textContent = region.mode;
  modeEl.dataset.mode = region.mode;
  modeEl.title = modeLegend[region.mode] || "";
  $("#culture-desc").textContent = region.description;
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

  // Linguistics
  const confLabels = state.data.meta.confidenceLabels || {};
  const conf = region.linguisticConfidence || "hypothetical";
  $("#ling-family").textContent = region.languageFamily || "—";
  $("#ling-languages").textContent = region.languages || "—";
  const confEl = $("#ling-confidence");
  confEl.textContent = conf;
  confEl.dataset.conf = conf;
  confEl.title = confLabels[conf] || "";
  $("#ling-note").textContent = region.linguisticNote || "";

  // Stacked bar
  const bar = $("#stack-bar");
  bar.innerHTML = entries
    .map(
      (e) =>
        `<div class="stack-seg" style="width:${e.value}%;background:${e.color}" title="${escapeHtml(e.detail)}: ~${e.value}%"></div>`
    )
    .join("");

  // Legend
  $("#ancestry-legend").innerHTML = entries
    .map(
      (e) =>
        `<div class="legend-item" title="${escapeHtml(e.detail)}"><span class="swatch" style="background:${e.color}"></span>${e.label} · ~${e.value}%</div>`
    )
    .join("");

  // Pie
  $("#pie").style.background = conicGradient(entries);
  $("#pie-list").innerHTML = entries
    .map(
      (e) =>
        `<li title="${escapeHtml(e.detail)}"><span><strong>${escapeHtml(e.label)}</strong> — ${escapeHtml(e.full)}</span><span class="pct">~${e.value}%</span></li>`
    )
    .join("");

  $("#mode-explain").textContent = modeLegend[region.mode] || "";
}

function buildTicks() {
  const wrap = $("#tick-labels");
  wrap.innerHTML = state.data.periods
    .map((p, i) => `<span data-i="${i}" title="${p.yearLabel}">${shortTick(p)}</span>`)
    .join("");
  wrap.querySelectorAll("span").forEach((el) => {
    el.addEventListener("click", () => setPeriod(Number(el.dataset.i)));
  });
}

function shortTick(p) {
  // Compact labels for the tick rail
  const map = {
    mesolithic: "Meso",
    "early-neolithic": "EN",
    "middle-neolithic": "MN",
    yamnaya: "Yam",
    "beaker-corded": "CW/BB",
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

function bindUI() {
  const slider = $("#time-slider");
  slider.max = String(state.data.periods.length - 1);
  slider.addEventListener("input", () => setPeriod(Number(slider.value)));

  $("#btn-prev").addEventListener("click", () => setPeriod(state.periodIndex - 1));
  $("#btn-next").addEventListener("click", () => setPeriod(state.periodIndex + 1));

  REGION_IDS.forEach((id) => {
    const el = document.getElementById(`region-${id}`);
    if (!el) return;
    el.addEventListener("click", () => selectRegion(id));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        selectRegion(id);
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") setPeriod(state.periodIndex - 1);
    if (e.key === "ArrowRight") setPeriod(state.periodIndex + 1);
  });
}

async function init() {
  try {
    state.data = await loadData();
  } catch (err) {
    console.error(err);
    $("#period-copy").textContent =
      "Could not load data/timeline.json. Serve this folder over HTTP (e.g. python -m http.server) rather than opening as a file if fetch is blocked.";
    return;
  }

  buildTicks();
  bindUI();

  const disc = $("#ling-disclaimer");
  if (disc && state.data.meta.linguisticDisclaimer) {
    disc.textContent = state.data.meta.linguisticDisclaimer;
  }

  // Start at Corded Ware / Beaker — the classic replacement showcase — then user can roam
  const start = state.data.periods.findIndex((p) => p.id === "beaker-corded");
  setPeriod(start >= 0 ? start : 0, { animate: false });
  selectRegion("britain");
}

init();
