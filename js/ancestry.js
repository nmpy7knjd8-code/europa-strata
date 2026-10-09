/* Europa Strata — ancestry component deep-dive page */

function $(sel) {
  return document.querySelector(sel);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function initTheme() {
  const saved = localStorage.getItem("europa-strata-theme");
  if (saved === "dark" || saved === "light") {
    document.documentElement.setAttribute("data-theme", saved);
  }
  $("#theme-toggle")?.addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    localStorage.setItem("europa-strata-theme", next);
  });
}

/** Drop overseas / Siberian rings so mini-maps frame the relevant core. */
function clipRingCentroid(ring) {
  let lon = 0;
  let lat = 0;
  const n = ring.length;
  for (let i = 0; i < n; i++) {
    lon += ring[i][0];
    lat += ring[i][1];
  }
  return [lon / n, lat / n];
}

function clipFeatureForAncestry(feature) {
  const g = feature.geometry;
  if (!g) return null;
  const iso = feature.properties?.iso;
  // European teaching frame — keeps RUS/TUR from swallowing the fit
  const ok = (lon, lat) => {
    if (iso === "RUS") return lon >= 19 && lon <= 55 && lat >= 44 && lat <= 70;
    if (iso === "TUR") return lon >= 26 && lon <= 45 && lat >= 36 && lat <= 42.5;
    return lon >= -25 && lon <= 48 && lat >= 34 && lat <= 72;
  };
  const ringOk = (ring) => {
    const [lon, lat] = clipRingCentroid(ring);
    return ok(lon, lat);
  };
  if (g.type === "Polygon") {
    return ringOk(g.coordinates[0]) ? feature : null;
  }
  if (g.type === "MultiPolygon") {
    const parts = g.coordinates.filter((poly) => ringOk(poly[0]));
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

function paintMiniMap(el, geo, component) {
  const w = Math.max(el.clientWidth || 320, 280);
  const h = Math.round(w * 0.78);
  el.innerHTML = "";

  const set = new Set(component.isos || []);
  const hot = geo.features
    .filter((f) => set.has(f.properties.iso))
    .map(clipFeatureForAncestry)
    .filter(Boolean);

  // Fit to highlighted land (zoomed), with a modest Europe fallback
  const fitTarget =
    hot.length > 0
      ? { type: "FeatureCollection", features: hot }
      : {
          type: "Feature",
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [-12, 36],
                [42, 36],
                [42, 68],
                [-12, 68],
                [-12, 36],
              ],
            ],
          },
        };

  const pad = hot.length > 0 ? 14 : 10;
  const projection = d3
    .geoAzimuthalEqualArea()
    .rotate([-12, -52])
    .fitExtent(
      [
        [pad, pad],
        [w - pad, h - pad],
      ],
      fitTarget
    );
  // Slight boost so cores fill the frame (esp. small SHG / CHG sets)
  const boost = hot.length && hot.length <= 4 ? 1.12 : hot.length ? 1.06 : 1;
  projection.scale(projection.scale() * boost);

  const path = d3.geoPath(projection);

  const svg = d3
    .select(el)
    .append("svg")
    .attr("viewBox", `0 0 ${w} ${h}`)
    .attr("role", "img")
    .attr(
      "aria-label",
      `Schematic map highlighting ${component.term} associated regions`
    );

  // Draw all land for context, then hot fill dominates
  svg
    .append("g")
    .selectAll("path")
    .data(geo.features)
    .join("path")
    .attr("d", path)
    .attr("class", (d) =>
      set.has(d.properties.iso) ? "anc-land is-hot" : "anc-land"
    )
    .attr("fill", (d) =>
      set.has(d.properties.iso) ? component.color : "var(--land-base)"
    )
    .attr("fill-opacity", (d) => (set.has(d.properties.iso) ? 0.9 : 1))
    .append("title")
    .text((d) => d.properties.name);
}

function renderPage(data, geo) {
  $("#anc-intro").textContent = data.intro;

  const toc = $("#anc-toc");
  toc.innerHTML = data.components
    .map(
      (c) =>
        `<a class="anc-toc-link" href="#${escapeHtml(c.id)}" style="--swatch:${escapeHtml(c.color)}"><span>${escapeHtml(c.term)}</span>${escapeHtml(c.name)}</a>`
    )
    .join("");

  const host = $("#anc-sections");
  host.innerHTML = data.components
    .map(
      (c) => `
      <article class="anc-section" id="${escapeHtml(c.id)}">
        <div class="anc-section-grid">
          <div class="anc-copy">
            <p class="kicker" style="color:${escapeHtml(c.color)}">${escapeHtml(c.term)}</p>
            <h2 class="anc-h2">${escapeHtml(c.name)}</h2>
            <p class="anc-years">${escapeHtml(c.years || "")}</p>
            <p class="anc-horizon">${escapeHtml(c.horizon)}</p>
            <p class="anc-summary">${escapeHtml(c.summary)}</p>
            ${
              c.phenotype
                ? `<div class="anc-phenotype"><p class="kicker">Inferred phenotype</p><p>${escapeHtml(c.phenotype)}</p></div>`
                : ""
            }
            ${c.body.map((p) => `<p>${escapeHtml(p)}</p>`).join("")}
            <div class="anc-meta">
              <div>
                <p class="kicker">Key proxies</p>
                <ul>${c.proxies.map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul>
              </div>
              <div>
                <p class="kicker">Role in the atlas</p>
                <p>${escapeHtml(c.role)}</p>
              </div>
            </div>
          </div>
          <figure class="anc-map-fig">
            <div class="anc-map" data-map="${escapeHtml(c.id)}"></div>
            <figcaption>${escapeHtml(c.mapNote)}</figcaption>
          </figure>
        </div>
      </article>`
    )
    .join("");

  data.components.forEach((c) => {
    const el = host.querySelector(`[data-map="${c.id}"]`);
    if (el) paintMiniMap(el, geo, c);
  });

  // Re-fit maps after layout (sticky/column widths settle)
  requestAnimationFrame(() => {
    data.components.forEach((c) => {
      const el = host.querySelector(`[data-map="${c.id}"]`);
      if (el) paintMiniMap(el, geo, c);
    });
    honorHash();
  });

  window.addEventListener(
    "hashchange",
    () => {
      honorHash();
    },
    { passive: true }
  );
}

function honorHash() {
  if (!location.hash) return;
  const target = document.getElementById(location.hash.slice(1));
  if (!target) return;
  // Ensure document can scroll (shared atlas CSS locks body on other pages)
  document.documentElement.style.overflow = "auto";
  document.body.style.overflow = "auto";
  requestAnimationFrame(() => {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

async function init() {
  initTheme();
  // Ancestry page must always page-scroll (atlas uses overflow:hidden on body)
  document.documentElement.classList.add("ancestry-page");
  document.body.classList.add("page-ancestry");
  document.documentElement.style.overflow = "auto";
  document.body.style.overflow = "auto";

  try {
    const [data, geo] = await Promise.all([
      fetch("data/ancestry.json").then((r) => {
        if (!r.ok) throw new Error("ancestry");
        return r.json();
      }),
      fetch("data/europe.geojson").then((r) => {
        if (!r.ok) throw new Error("geo");
        return r.json();
      }),
    ]);
    renderPage(data, geo);
  } catch (err) {
    console.error(err);
    $("#anc-intro").textContent =
      "Could not load ancestry guides. Serve this folder over HTTP.";
  }
}

init();
