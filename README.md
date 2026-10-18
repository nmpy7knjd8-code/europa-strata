# Europa Strata

Interactive atlas of European cultures, empires, archaeogenetic ancestry, and languages from the Mesolithic to the present.

**Live:** https://nmpy7knjd8-code.github.io/europa-strata/

Mobile-stacked layout (map → time slider → content) on every screen width: **Natural Earth** basemap with schematic culture-extent overlays, then detail below. Light theme by default (small “Theme” control in the footer for dark mode). Smooth round time slider with continuous color blending between periods. Tap countries for culture / ancestry / language.

## Run locally

```bash
cd europa-strata
python3 -m http.server 8765
```

Open http://127.0.0.1:8765/

## Contents

| Path | Role |
|------|------|
| `index.html` | Atlas app shell (era tabs → map → time slider → detail panel) |
| `ancestry.html` + `js/ancestry.js` | Ancestry-component guides (WHG, EHG, SHG, EEF, WSH, CHG) with a mini-map each; reads `data/ancestry.json`; supports `#component` deep links |
| `sources.html` | Styled, DOI-linked bibliography for the ancestry figures (linked from `ancestry.html`) |
| `archaeogenetic-sources.md` | Bibliography & method notes in Markdown (served as raw text on Pages) |
| `css/styles.css` | Light/dark themes, stacked map-first layout, ancestry/sources pages |
| `js/app.js` | D3 map, slider, era tabs, detail panel |
| `data/europe.geojson` | Natural Earth 50m Europe (public domain) |
| `data/timeline.json` | Deep-time spine: 16 periods → map layers, region genetics/languages (loaded at start) |
| `data/timeline-text/<period>.json` | Long region/polity prose per Deep-time period, fetched when that period is first shown |
| `data/key-events.json` | Key events listed under the map for the selected time and place |
| `data/kingdom-eras/<tab>.json` | Polity packs for the four kingdom-era tabs, fetched the first time a tab opens |
| `data/kingdom-eras/geo/<tab>.topo.json` | Polity borders for those tabs (TopoJSON, see below) |
| `scripts/` | Data pipelines (enrichment, era-map build) and `bump_version.py` |

### Loading

`timeline.json`, `europe.geojson` and `key-events.json` load at startup. Everything else is lazy: per-period prose
(`timeline-text/`) when a period is first viewed, and each kingdom-era pack plus its borders when its tab is first
opened. Every data URL carries `?v=<build>` from `<meta name="build">`.

### Releasing

After changing CSS, JS or data, bump the build so browsers fetch fresh copies:

```bash
python3 scripts/bump_version.py my-change-1   # updates <meta name="build"> and every ?v= tag
```

## Notes

- Culture fills are **best-guess consensus extents** painted on modern borders — not site-precise excavation maps. Overlaps encode expansion / substrate / absorption roles.
- Ancestry percentages are approximate literature ranges.
- Archaeological culture names ≠ genetic clusters ≠ languages.

## Kingdom-era borders (v2)

The High Medieval, Renaissance, Early Modern and Modern tabs draw polity borders from
[aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps) (GPL-3.0),
clipped to Europe, snapped to Natural Earth coastlines, matched to Europa Strata polity ids and
simplified to TopoJSON with shared borders (`data/kingdom-eras/geo/*.topo.json`).
Slider years with no dataset map (1450, 1750, 1871, 1990) and polities the dataset lacks keep the
hand-drawn outlines, noted as approximate. See `data/LICENSE-historical-basemaps`.
Rebuild: `python3 scripts/build_era_maps_v2.py --hb <historical-basemaps>/geojson --report scripts/era_maps_v2_report.json`
(needs `shapely` and `mapshaper`). Matching overrides: `scripts/era_maps_v2_overrides.json`.
