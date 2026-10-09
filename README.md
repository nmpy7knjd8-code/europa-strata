# Europa Strata

Interactive atlas of European cultures, empires, archaeogenetic ancestry, and languages from the Mesolithic to the present.

**Live:** https://nmpy7knjd8-code.github.io/europa-strata/

Desktop-first layout: large **Natural Earth** basemap with schematic culture-extent overlays; sidebar for time + detail. Light theme by default (small “Theme” control in the footer for dark mode). Smooth round time slider with continuous color blending between periods. Click countries for culture / ancestry / language.

## Run locally

```bash
cd europa-strata
python3 -m http.server 8765
```

Open http://127.0.0.1:8765/

## Contents

| Path | Role |
|------|------|
| `index.html` | Desktop shell |
| `css/styles.css` | Light/dark themes, map-first layout |
| `js/app.js` | D3 map, slider, detail panel |
| `data/europe.geojson` | Natural Earth 50m Europe (public domain) |
| `data/timeline.json` | Periods → culture layers + region genetics/languages |
| `archaeogenetic-sources.md` | Bibliography & method notes |

## Notes

- Culture fills are **best-guess consensus extents** painted on modern borders — not site-precise excavation maps. Overlaps encode expansion / substrate / absorption roles.
- Ancestry percentages are approximate literature ranges.
- Archaeological culture names ≠ genetic clusters ≠ languages.
