#!/usr/bin/env python3
"""Regenerate og-image.png (1200x630 social share card) from the live atlas map.

Serve the repo first (python3 -m http.server 8765), then:
    python3 scripts/make_og_image.py [http://127.0.0.1:8765/]
Needs Playwright (pip install playwright) and a Chrome/Chromium; set CHROME=/path/to/chrome
if Playwright's bundled browser is not installed. Shows the default view (Beaker-era Britain).
"""
import os, pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
OUT = pathlib.Path(__file__).resolve().parent.parent / "og-image.png"
css = """
.atlas-tabs,.time-bar,.legend-bar,.side,.glossary,.below,.map-tools,.map-tip,#load-notice,.map-chrome{display:none!important}
html,body{overflow:hidden!important;background:#f4f4f4!important}
.map-stage{position:fixed!important;top:0!important;left:400px!important;width:800px!important;height:630px!important;margin:0!important;border:0!important;background:#f4f4f4!important}
#map,#map svg{width:800px!important;height:630px!important}
#og-card{position:fixed;left:56px;top:0;bottom:0;width:430px;display:flex;flex-direction:column;justify-content:center;z-index:50;color:#111;font-family:'Sora',sans-serif}
#og-card h1{font-family:'Instrument Serif',serif;font-weight:400;font-size:92px;line-height:.92;letter-spacing:-.02em;margin:0 0 22px}
#og-card p{font-size:24px;line-height:1.35;margin:0 0 14px;max-width:400px}
#og-card .yr{font-size:20px;color:#444}
"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    pg=b.new_page(viewport={'width':1200,'height':630})
    pg.goto(URL,wait_until='networkidle')
    pg.add_style_tag(content=css)
    pg.evaluate("window.dispatchEvent(new Event('resize'))"); pg.wait_for_timeout(1200)
    pg.evaluate("""(()=>{const d=document.createElement('div');d.id='og-card';d.innerHTML='<h1>Europa<br>Strata</h1><p>A deep-time atlas of European cultures, ancestry and kingdoms.</p><p class=yr>8000 BC to today</p>';document.body.appendChild(d)})()""")
    pg.mouse.move(1,1); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT))
    Image.open(OUT).convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(OUT, optimize=True)
    print('wrote', OUT)
    b.close()
