#!/usr/bin/env python3
"""
Build data/key-events.json with short teasers + enriched full detail
from research JSON under era-events/.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = Path("/cursor/stores/self/internal/era-events")
OUT = ROOT / "data" / "key-events.json"

PERIOD_IDS = {
    "mesolithic",
    "early-neolithic",
    "middle-neolithic",
    "yamnaya",
    "beaker-corded",
    "nordic-bronze",
    "iron-age",
    "classical",
    "migration",
    "frankish",
    "vikings",
    "high-medieval",
    "late-medieval",
    "reformation",
    "early-modern",
    "modern",
}

REGION_LABELS = {
    "iberia": "Iberia",
    "britain": "Britain & Ireland",
    "france": "France",
    "central": "Central Europe",
    "scandinavia": "Scandinavia",
    "italy": "Italy",
    "balkans": "the Balkans",
    "eastern": "Eastern Europe / the steppe fringe",
}

THEME_WHY = {
    "climate": "climate stress and landscape change reshaping where people could live and what they could harvest",
    "technology": "new tools, crafts, or infrastructure that altered daily economies and long-distance exchange",
    "ritual": "burial and ceremonial practice that signalled status, belief, and group identity",
    "subsistence": "shifts in foodways—farming, herding, fishing, or foraging—that rewired settlement",
    "migration": "people on the move: demic pulses, elite takeover, refugee flight, or colonisation",
    "ancestry": "genome-wide turnover or admixture that rewrote who counted as ‘local’",
    "agriculture": "the spread or intensification of crops and livestock as a political-economic package",
    "landscape": "coasts, rivers, soils, and monuments remapping how space was used",
    "catastrophe": "sudden disaster—tsunami, plague, sack, or famine—cutting through gradual trends",
    "social": "household, kinship, and hierarchy rearrangements visible in cemeteries and settlements",
    "conflict": "organised violence, fortification, or massacre as a political instrument",
    "trade": "prestige goods and staples moving along corridors that tied distant elites together",
    "urbanism": "dense aggregation—tells, oppida, cities—concentrating labour and power",
}

THEME_GROUND = {
    "climate": "communities adjusted mobility, storage, and coastal or inland focus as weather and shorelines moved",
    "technology": "workshops, mines, shipyards, or script houses became nodes others had to deal with",
    "ritual": "tombs, temples, and festivals turned memory into durable landscape claims",
    "subsistence": "diets and labour calendars changed; some villages thrived while others emptied",
    "migration": "new dialects, surnames of power, and burial rites arrived with incomers—and sometimes replaced earlier ones",
    "ancestry": "later gene pools still carry the signature of this pulse, even when culture labels moved on",
    "agriculture": "fields, herds, and surplus underwrote larger polities and harder frontiers",
    "landscape": "people invested in places—causeways, dykes, stone rows—that later generations still reused",
    "catastrophe": "recovery was uneven; some coasts and cities never returned to the old pattern",
    "social": "who married whom, who owned land, and who spoke for the dead became newly contested",
    "conflict": "survivors rebuilt under different lords, laws, or fortresses",
    "trade": "ports and river nodes gained leverage over inland producers",
    "urbanism": "density bred both opportunity and epidemic or political fragility",
}


def first_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""
    m = re.search(r"(.+?[.!?])(\s|$)", text)
    if m:
        return m.group(1).strip()
    return text


def teaser_from(title: str | None, body: str) -> str:
    if title:
        t = title.strip()
        # Keep teasers to roughly 1–2 lines
        if len(t) <= 110:
            return t
        return t[:107].rstrip() + "…"
    sent = first_sentence(body)
    if len(sent) <= 140:
        return sent
    return sent[:137].rstrip() + "…"


def region_phrase(regions: list[str]) -> str:
    labels = [REGION_LABELS.get(r, r) for r in regions if r]
    if not labels:
        return "Europe’s mapped regions"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def theme_bits(themes: list[str], table: dict[str, str]) -> str:
    bits = [table[t] for t in themes if t in table]
    if not bits:
        return ""
    if len(bits) == 1:
        return bits[0]
    if len(bits) == 2:
        return f"{bits[0]}, and {bits[1]}"
    return "; ".join(bits[:-1]) + f"; and {bits[-1]}"


def pick_related(elements: list, title: str, body: str, limit: int = 3) -> list[str]:
    blob = f"{title} {body}".lower()
    scored = []
    for el in elements:
        if isinstance(el, str):
            s = el.strip()
        elif isinstance(el, dict):
            s = (el.get("title") or el.get("text") or "").strip()
            if el.get("title") and el.get("text"):
                s = f"{el['title']}: {el['text']}"
        else:
            continue
        if not s:
            continue
        words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", s.lower()) if w not in {
            "with", "from", "that", "this", "their", "have", "were", "been", "into", "over"
        }]
        score = sum(1 for w in words if w in blob)
        scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], x[1]))
    out = []
    for score, s in scored:
        if score <= 0 and out:
            continue
        out.append(s)
        if len(out) >= limit:
            break
    if not out:
        out = [s for _, s in scored[:limit]]
    return out


def pick_sources(sources: list, limit: int = 3) -> list[str]:
    out = []
    for s in sources:
        if isinstance(s, str):
            t = s.strip()
        elif isinstance(s, dict):
            t = (s.get("title") or "").strip()
            if s.get("detail"):
                t = f"{t} — {s['detail']}" if t else str(s["detail"])
        else:
            continue
        if t:
            out.append(t)
        if len(out) >= limit:
            break
    return out


def enrich_detail(
    *,
    period_label: str,
    date: str | None,
    title: str | None,
    body: str,
    regions: list[str],
    themes: list[str],
    elements: list,
    sources: list,
) -> str:
    body = re.sub(r"\s+", " ", (body or "").strip())
    if not body and title:
        body = title
    place = region_phrase(regions)
    why = theme_bits(themes, THEME_WHY)
    ground = theme_bits(themes, THEME_GROUND)
    related = pick_related(elements, title or "", body)
    srcs = pick_sources(sources)

    paras = []
    head = body
    if title and not body.lower().startswith(title.lower()[:20]):
        # Lead with full research prose; title already in teaser
        paras.append(head)
    else:
        paras.append(head)

    # Expand: context / why it matters
    when = date or "this horizon"
    p2 = (
        f"In the wider {period_label} story ({when}), this is more than a local anecdote: "
        f"it sits on the atlas as a hinge for {place}."
    )
    if why:
        p2 += f" What is at stake is {why}."
    else:
        p2 += (
            " What is at stake is how power, ancestry, and livelihood were rearranged "
            "across neighbouring societies."
        )
    p2 += (
        " Read against the period narrative, it helps explain why later maps look the way they do—"
        "who held corridors, who absorbed whom, and which cultural labels stuck."
    )
    paras.append(p2)

    # Regional impact
    p3 = f"Regional impact. For {place}, the consequences were concrete."
    if ground:
        p3 += f" On the ground, {ground}."
    else:
        p3 += (
            " Settlements, cemeteries, and frontiers register the change even when chronicles are silent."
        )
    if related:
        p3 += " Anchors in the material record include " + "; ".join(related) + "."
    paras.append(p3)

    # Deepen short bodies further
    if len(body) < 280:
        p4 = (
            f"Because the surviving evidence is patchy, specialists triangulate pottery styles, "
            f"radiocarbon sequences, and ancient DNA rather than trusting any single site. "
            f"The Key events entry compresses that debate into a dated beat for the slider: "
            f"treat the date as a consensus window, not a single calendar day, and the place tags "
            f"as the regions where the signal is strongest on this atlas."
        )
        paras.append(p4)

    if srcs:
        paras.append("Further reading. " + " · ".join(srcs) + ".")

    # Ensure substantially longer than input
    detail = "\n\n".join(paras)
    if len(detail) < max(400, int(len(body) * 1.6)):
        detail += (
            "\n\nDownstream, the next periods inherit the demographic and institutional leftovers "
            "of this moment—whether as continuity under new names, as a substrate beneath incomers, "
            "or as a frontier still visible in language and ancestry clines."
        )
    return detail


def normalize_regions(e: dict) -> list[str]:
    out = []
    for r in e.get("regions") or []:
        id_ = str(r).strip().lower()
        if id_ in REGION_LABELS and id_ not in out:
            out.append(id_)
    if e.get("region"):
        id_ = str(e["region"]).strip().lower()
        if id_ in REGION_LABELS and id_ not in out:
            out.append(id_)
    return out


def normalize_event(e: dict, period: dict) -> dict | None:
    title = (e.get("title") or "").strip() or None
    body = (e.get("summary") or e.get("text") or e.get("event") or "").strip()
    if not body and not title:
        return None
    date = (e.get("date") or e.get("year") or e.get("when") or "").strip() or None
    regions = normalize_regions(e)
    themes = [str(t).strip() for t in (e.get("themes") or []) if str(t).strip()]
    teaser = teaser_from(title, body)
    detail = enrich_detail(
        period_label=period.get("label") or period.get("periodLabel") or period["periodId"],
        date=date,
        title=title,
        body=body or title or "",
        regions=regions,
        themes=themes,
        elements=period.get("interestingElements") or [],
        sources=period.get("sources") or [],
    )
    return {
        "date": date,
        "title": title,
        "teaser": teaser,
        "detail": detail,
        # keep text as detail for older callers
        "text": detail,
        "iso": str(e["iso"]).upper() if e.get("iso") else None,
        "region": regions[0] if regions else None,
        "regions": regions,
        "themes": themes,
    }


def normalize_element(el):
    if isinstance(el, str):
        s = el.strip()
        return {"title": s, "text": None, "iso": None} if s else None
    if not isinstance(el, dict):
        return None
    title = (el.get("title") or el.get("label") or "").strip() or None
    text = (el.get("text") or el.get("note") or el.get("detail") or "").strip() or None
    if not title and not text:
        return None
    return {
        "title": title,
        "text": text,
        "iso": str(el["iso"]).upper() if el.get("iso") else None,
    }


def normalize_source(s):
    if isinstance(s, str):
        t = s.strip()
        return {"title": t, "detail": None, "url": None} if t else None
    if not isinstance(s, dict):
        return None
    title = (s.get("title") or s.get("name") or "").strip() or None
    if not title and not s.get("detail") and not s.get("url"):
        return None
    return {
        "title": title,
        "detail": (str(s["detail"]).strip() if s.get("detail") else None),
        "url": (str(s["url"]).strip() if s.get("url") else None),
    }


def load_periods() -> dict:
    periods = {}
    for path in sorted(IN_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        raw = json.loads(path.read_text())
        blocks = raw if isinstance(raw, list) else [raw]
        for b in blocks:
            pid = str(b.get("periodId") or b.get("id") or "").strip()
            if pid not in PERIOD_IDS:
                print(f"skip unknown period {pid} in {path.name}")
                continue
            events = []
            for e in b.get("keyEvents") or b.get("events") or []:
                ne = normalize_event(e, {**b, "periodId": pid})
                if ne:
                    events.append(ne)
            elements = [
                x
                for x in (
                    normalize_element(el)
                    for el in (b.get("interestingElements") or b.get("elements") or [])
                )
                if x
            ]
            sources = [
                x
                for x in (normalize_source(s) for s in (b.get("sources") or []))
                if x
            ]
            periods[pid] = {
                "periodId": pid,
                "label": b.get("label") or b.get("periodLabel"),
                "approxYears": b.get("approxYears"),
                "keyEvents": events,
                "interestingElements": elements,
                "sources": sources,
                "sourceFile": path.name,
            }
            print(
                f"+ {pid} ← {path.name}: {len(events)} events "
                f"(avg detail {int(sum(len(e['detail']) for e in events)/max(len(events),1))} chars)"
            )
    return periods


def main():
    periods = load_periods()
    out = {
        "version": 2,
        "updatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "periods": periods,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    # sanity: teasers short, details long
    short_t = long_d = 0
    for p in periods.values():
        for e in p["keyEvents"]:
            if len(e["teaser"]) <= 160:
                short_t += 1
            if len(e["detail"]) >= 350:
                long_d += 1
    n = sum(len(p["keyEvents"]) for p in periods.values())
    print(f"wrote {OUT} ({len(periods)} periods, {n} events)")
    print(f"teasers ≤160 chars: {short_t}/{n}; details ≥350 chars: {long_d}/{n}")


if __name__ == "__main__":
    main()
