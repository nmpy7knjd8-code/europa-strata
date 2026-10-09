# Europa Strata

Interactive atlas of European cultures, empires, archaeogenetic ancestry, and languages from the Mesolithic to the present.

**Black-and-white UI chrome; color only on map regions.** Drag the time slider, click a region for culture + ancestry mix + languages (attested / reconstructed / hypothetical).

## Live site

**Live:** `https://nmpy7knjd8-code.github.io/europa-strata/`

## Run locally

```bash
cd europa-strata
python3 -m http.server 8765
```

Open http://127.0.0.1:8765/

## Contents

| Path | Role |
|------|------|
| `index.html` | App shell + SVG map |
| `css/styles.css` | B&W chrome, layout |
| `js/app.js` | Slider, region detail, ancestry viz |
| `data/timeline.json` | Periods → regions → culture / genetics / languages |
| `archaeogenetic-sources.md` | Bibliography & method notes |

## Notes

- Percentages are approximate literature ranges, not sample-level qpAdm outputs.
- Archaeological culture names ≠ genetic clusters ≠ languages.
- Indo-European ↔ steppe ancestry is framed as correlation, not proof.
