# Europa Strata — project context

Interactive static atlas of European archaeological cultures, empires, and archaeogenetic ancestry from the Mesolithic/Neolithic to the present.

## Goals

- Black-and-white chrome; **color only on map regions** (culture/people per period).
- Time slider drives map fills, narratives, and ancestry absorption visuals.
- Distinguish **archaeological culture labels** from **genetic clusters** (WHG, EEF, WSH/steppe, etc.).
- Encode replacement vs absorption with approximate percentages from post-2015 literature; flag uncertainty.

## Stack

Self-contained static site: `index.html` + CSS + JS + JSON. No build step. Open `docs/europe-history-map/index.html` in a browser (or serve the folder).

## Regions (pulse points)

Iberia, Britain & Ireland, France, Central Europe, Scandinavia, Italy, Balkans, Eastern Europe / Pontic steppe.

## Period spine (13 stops)

Mesolithic → Early Neolithic → Middle–Late Neolithic → Copper / Yamnaya → Corded Ware & Bell Beaker → **Nordic & European Bronze** → Iron Age → Classical / early Rome → **Migration Period (incl. Wielbark)** → **Frankish & Early Medieval** → High Medieval → Early Modern → Modern.

Each stop names cultures/polities per region; click shows description + **languages** (family, names, evidence tag) + ancestry mix + substrate→incoming→fused absorption strip. Period slider also shows a short linguistic landscape line.

## Sources

See `docs/archaeogenetic-sources.md`. Numbers in the UI are approximate consensus ranges, not sample-level estimates.
