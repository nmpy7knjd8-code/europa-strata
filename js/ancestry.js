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

function paintMiniMap(el, geo, component) {
  const w = Math.max(el.clientWidth || 320, 280);
  const h = Math.round(w * 0.72);
  el.innerHTML = "";

  const frame = {
    type: "Feature",
    geometry: {
      type: "Polygon",
      coordinates: [
        [
          [-25, 34],
          [55, 34],
          [55, 72],
          [-25, 72],
          [-25, 34],
        ],
      ],
    },
  };

  const projection = d3
    .geoAzimuthalEqualArea()
    .rotate([-15, -52])
    .fitExtent(
      [
        [8, 8],
        [w - 8, h - 8],
      ],
      frame
    );
  const path = d3.geoPath(projection);
  const set = new Set(component.isos || []);

  const svg = d3
    .select(el)
    .append("svg")
    .attr("viewBox", `0 0 ${w} ${h}`)
    .attr("role", "img")
    .attr(
      "aria-label",
      `Schematic map highlighting ${component.term} associated regions`
    );

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
    .attr("fill-opacity", (d) => (set.has(d.properties.iso) ? 0.88 : 1))
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
            <p class="anc-horizon">${escapeHtml(c.horizon)}</p>
            <p class="anc-summary">${escapeHtml(c.summary)}</p>
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

  // Honor hash after render (GitHub Pages / late layout)
  if (location.hash) {
    const target = document.getElementById(location.hash.slice(1));
    if (target) {
      requestAnimationFrame(() =>
        target.scrollIntoView({ behavior: "smooth", block: "start" })
      );
    }
  }
}

async function init() {
  initTheme();
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
