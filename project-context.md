# Europa Strata — project context

Interactive static atlas of European archaeological cultures, polities, and archaeogenetic ancestry from the Mesolithic to the present. See `README.md` for file layout and how to run it.

## Goals

- Black-and-white chrome; **color only on map regions** (culture/people per period).
- Time slider drives map fills, narratives, and ancestry absorption visuals.
- Distinguish **archaeological culture labels** from **genetic clusters** (WHG, EEF, WSH/steppe, etc.) and from languages.
- Encode replacement vs absorption with approximate percentages from post-2015 literature; flag uncertainty.

## Stack

Static site served from the repo root on GitHub Pages: `index.html`, `ancestry.html`, `sources.html` + `css/styles.css` + `js/app.js` / `js/ancestry.js` + JSON in `data/`. D3 7 and topojson-client load from jsDelivr. No build step; `scripts/` holds one-off data pipelines and `scripts/bump_version.py` for cache-busting.

## Regions (pulse points)

Iberia, Britain & Ireland, France, Central Europe, Scandinavia, Italy, Balkans, Eastern Europe / Pontic steppe.

## Period spine (Deep-time tab, 16 stops)

Mesolithic → Early Neolithic → Middle Neolithic → Yamnaya → Corded Ware & Bell Beaker → Nordic Bronze → Iron Age → Classical → Migration (incl. Wielbark) → Frankish → Vikings / millennium kingdoms → High Medieval → Late Medieval → Reformation → Early Modern → Modern.

Each stop names cultures/polities per region; clicking a country shows description, **languages** (family, names, evidence tag), ancestry mix, and a substrate → incoming → result absorption strip.

## Kingdom-era tabs

High Medieval, Renaissance, Early Modern and Modern each load their own pack (`data/kingdom-eras/<tab>.json`) and polity borders (`data/kingdom-eras/geo/<tab>.topo.json`, from historical-basemaps, GPL-3.0) on first use, with leader / religion / culture / conflict prose per polity.

## Sources

`sources.html` (styled, DOI-linked) and `archaeogenetic-sources.md` (method notes). Numbers in the UI are approximate consensus ranges, not sample-level estimates.
