#!/usr/bin/env python3
"""Generate animated project hero banners (dark + light SVG) for Ahmed Sameh's repos.

Standard library only. Reuses the profile design system: grid canvas, signature
cyan -> violet -> amber edge, a six-step medallion motif (source -> bronze ->
gate -> silver -> gold -> serve), system font stacks, CSS-only animation, and a
prefers-reduced-motion static fallback. No JavaScript, no external fonts/images,
no <foreignObject>. Output is deterministic.

Usage:
    python scripts/make_banner.py --title "Nile Delta Crop Monitoring" \
        --subtitle "Sentinel-2 + Open-Meteo -> Bronze/Silver/Gold Parquet lakehouse" \
        --tags Python Prefect DuckDB Pandera XGBoost --outdir assets

    python scripts/make_banner.py --title "E-commerce Data Pipeline" \
        --subtitle "Olist CSV -> validated PostgreSQL star schema" \
        --tags Python SQL PostgreSQL pandas "Docker Compose" --basename banner

    python scripts/make_banner.py --title "Phishing URL Detection" \
        --subtitle "Domain-grouped lexical URL triage (research demo)" \
        --tags Python LightGBM scikit-learn FastAPI Streamlit

    python scripts/make_banner.py --title "Customer Churn Prediction" \
        --subtitle "Telco churn -> simulated retention-cost thresholds" \
        --tags Python pandas scikit-learn Matplotlib pytest

    python scripts/make_banner.py --title "Credit Risk Analysis" \
        --subtitle "South German Credit -> cost-sensitive threshold study" \
        --tags Python pandas scikit-learn Matplotlib Jupyter

Writes <basename>-dark.svg and <basename>-light.svg into --outdir (default ".").
--height defaults to 320 (hero). Heights below 300 switch to a compact strip
with a horizontal medallion motif; 160 is the recommended project-card size.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

WIDTH = 1200
MARGIN = 48
MAX_TAGS = 5

DARK = {
    "canvas": "#0B1020", "surface": "#121A2A", "raised": "#182337",
    "border": "#2B3A4F", "text": "#E6EDF5", "muted": "#93A4B7",
    "bronze": "#D99245", "silver": "#9CB0C3", "gold": "#F2C14E",
    "cyan": "#36C5D8", "violet": "#A78BFA",
}
LIGHT = {
    "canvas": "#F5F8FB", "surface": "#FFFFFF", "raised": "#EAF0F5",
    "border": "#D3DEE8", "text": "#172533", "muted": "#52687C",
    "bronze": "#A75D13", "silver": "#637D91", "gold": "#946500",
    "cyan": "#007F92", "violet": "#6941B6",
}
SIGNATURE = ("#22D3EE", "#8B5CF6", "#F59E0B")

SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif'
MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace'

STAGES = (
    ("SOURCE", "landing", "cyan"),
    ("BRONZE", "raw zone", "bronze"),
    ("QUALITY GATE", "checks", "violet"),
    ("SILVER", "typed tables", "silver"),
    ("GOLD", "curated", "gold"),
    ("SERVE", "consumers", "cyan"),
)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def esc_attr(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def fit_font(text: str, max_width: float, start: float, minimum: float,
             factor: float) -> tuple[float, bool]:
    """Shrink font until the estimated width fits; report if textLength is needed."""
    size = start
    while size > minimum and len(text) * factor * size > max_width:
        size -= 0.5
    forced = len(text) * factor * size > max_width
    return size, forced


def text_el(x: float, y: float, content: str, cls: str, size: float, *,
            weight: str | None = None, spacing: float | None = None,
            max_width: float | None = None, anchor: str | None = None) -> str:
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'class="{cls}"', f'font-size="{size:g}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if max_width is not None:
        attrs.append(f'textLength="{max_width:g}"')
        attrs.append('lengthAdjust="spacingAndGlyphs"')
    return f"<text {' '.join(attrs)}>{escape(content)}</text>"


def chip_layout(tags: list[str], max_w: float, font: float, pad: float,
                gap: float) -> tuple[list[float], float, float, float, bool]:
    """Return chip widths plus the font/pad/gap that fit them, and force flag."""
    widths = [len(t) * font * 0.60 + pad for t in tags]
    if tags and sum(widths) + gap * (len(tags) - 1) > max_w:
        font, pad, gap = 10.0, 18.0, 8.0
        widths = [len(t) * font * 0.60 + pad for t in tags]
    forced = False
    if tags and sum(widths) + gap * (len(tags) - 1) > max_w:
        forced = True
        avail = max_w - gap * (len(tags) - 1)
        scale = avail / sum(widths)
        widths = [w * scale for w in widths]
    return widths, font, pad, gap, forced


def build_svg(title: str, subtitle: str, tags: list[str], height: int,
              pal: dict[str, str]) -> str:
    h = height
    hero = h >= 300
    left_w = 628 if hero else 700

    eyebrow_y = round(h * 0.19, 1)
    if hero:
        title_y = round(h * 0.40, 1)
        title_start = clamp(h * 0.145, 22, 46)
        sub_font = 12.5
        sub_gap = 26
        tags_top = h - 54
        chip_h, chip_font, chip_pad, chip_gap = 28, 11.5, 26.0, 10.0
    else:
        title_y = round(h * 0.42, 1)
        title_start = clamp(h * 0.22, 24, 46)
        sub_font = 11.0
        sub_gap = 21
        tags_top = h - 42
        chip_h, chip_font, chip_pad, chip_gap = 24, 10.5, 22.0, 8.0

    title_size, title_forced = fit_font(title, left_w, title_start, 16, 0.55)
    subtitle_y = round(title_y + sub_gap, 1)
    sub_size, sub_forced = (0.0, False)
    if subtitle:
        sub_size, sub_forced = fit_font(subtitle, left_w, sub_font, 9, 0.58)

    widths, chip_font, chip_pad, chip_gap, forced_chips = chip_layout(
        tags, left_w, chip_font, chip_pad, chip_gap)

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" '
        f'viewBox="0 0 {WIDTH} {h}" role="img" '
        f'aria-label="{esc_attr(title)}'
        + (f" — {esc_attr(subtitle)}" if subtitle else "")
        + (f" Technologies: {esc_attr(', '.join(tags))}." if tags else "")
        + ' Decorative batch-pipeline motif; not a live DAG.">'
    )
    parts.append(f"""  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{pal['border']}" stroke-width="0.75" stroke-opacity="0.4"/>
    </pattern>
    <linearGradient id="sig" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{SIGNATURE[0]}"/>
      <stop offset="50%" stop-color="{SIGNATURE[1]}"/>
      <stop offset="100%" stop-color="{SIGNATURE[2]}"/>
    </linearGradient>
    <style>
      .sans{{font-family:{SANS}}}
      .mono{{font-family:{MONO}}}
      .t{{fill:{pal['text']}}}.m{{fill:{pal['muted']}}}
      .cyan{{fill:{pal['cyan']}}}.bronze{{fill:{pal['bronze']}}}.silver{{fill:{pal['silver']}}}.gold{{fill:{pal['gold']}}}.violet{{fill:{pal['violet']}}}
      .chip{{fill:{pal['raised']};stroke:{pal['border']};stroke-width:1}}
      .panel{{fill:{pal['surface']};stroke:{pal['border']};stroke-width:1.2}}
      .gate{{fill:{pal['surface']};stroke:{pal['violet']};stroke-width:1.5}}
      .wire{{fill:none;stroke:{pal['border']};stroke-width:1.5;stroke-opacity:0.55}}
      @keyframes vflow{{to{{stroke-dashoffset:-158}}}}
      @keyframes hflow{{to{{stroke-dashoffset:-362}}}}
      @keyframes pulse{{0%,100%{{opacity:0.9}}50%{{opacity:0.3}}}}
      .vpacket{{fill:none;stroke:url(#sig);stroke-width:2;stroke-dasharray:8 150;stroke-linecap:round;animation:vflow 3.8s linear infinite}}
      .hpacket{{fill:none;stroke:url(#sig);stroke-width:2;stroke-dasharray:8 354;stroke-linecap:round;animation:hflow 4.6s linear infinite}}
      .pulse{{animation:pulse 3.4s ease-in-out infinite}}
      .d1{{animation-delay:-0.9s}}.d2{{animation-delay:-1.7s}}.d3{{animation-delay:-2.4s}}
      @media (prefers-reduced-motion:reduce){{.vpacket,.hpacket,.pulse{{animation:none}}}}
    </style>
  </defs>""")
    parts.append(f'  <rect width="{WIDTH}" height="{h}" rx="16" fill="{pal["canvas"]}"/>')
    parts.append(f'  <rect width="{WIDTH}" height="{h}" rx="16" fill="url(#grid)"/>')
    parts.append(
        f'  <rect x="0.75" y="0.75" width="{WIDTH - 1.5}" height="{h - 1.5}" '
        f'rx="15.25" fill="none" stroke="{pal["border"]}" stroke-width="1.5"/>')
    parts.append(f'  <path d="M16 1.5H{WIDTH - 16}" stroke="url(#sig)" stroke-width="3" stroke-linecap="round"/>')

    # --- left identity block -------------------------------------------------
    parts.append(f'  <rect x="{MARGIN}" y="{eyebrow_y - 9:g}" width="18" height="3" rx="1.5" fill="url(#sig)"/>')
    parts.append(text_el(78, eyebrow_y, "PROJECT CASE STUDY · DATA ENGINEERING",
                         "mono m", 9.5, spacing=1.6))
    parts.append(text_el(MARGIN, title_y, title, "sans t", title_size, weight="800",
                         spacing=-0.6, max_width=left_w if title_forced else None))
    if subtitle:
        parts.append(text_el(MARGIN, subtitle_y, subtitle, "mono m", sub_size,
                             max_width=left_w if sub_forced else None))

    if tags:
        if hero or h >= 210:
            parts.append(text_el(MARGIN, tags_top - 12, "STACK · FROM REPOSITORY DEPENDENCIES",
                                 "mono m", 8.5, spacing=1.2))
        x = float(MARGIN)
        for tag, w in zip(tags, widths):
            parts.append(f'  <rect x="{x:g}" y="{tags_top}" width="{w:g}" height="{chip_h}" rx="{chip_h / 2:g}" class="chip"/>')
            inner = w - 20 if forced_chips else None
            parts.append(text_el(round(x + w / 2, 1), tags_top + round(chip_h * 0.64, 1),
                                 tag, "mono t", chip_font, anchor="middle", max_width=inner))
            x += w + chip_gap

    # --- right-side motif ----------------------------------------------------
    if hero:
        panel_x, panel_w = 740, 412
        panel_h = min(h - 112, 260)
        panel_y = round((h - panel_h) / 2, 1)
        rows_start = round(panel_y + 60, 1)
        rows_end = round(panel_y + panel_h - 20, 1)
        step = (rows_end - rows_start) / 5
        spine = panel_x + 32

        parts.append(f'  <path d="M712 56V{h - 56}" stroke="{pal["border"]}" stroke-width="1.2" stroke-opacity="0.55"/>')
        parts.append(f'  <rect x="{panel_x}" y="{panel_y:g}" width="{panel_w}" height="{panel_h:g}" rx="14" class="panel"/>')
        parts.append(f'  <path d="M{panel_x + 22} {panel_y + 0.75:g}H{panel_x + panel_w - 22}" stroke="url(#sig)" stroke-width="2" stroke-linecap="round" stroke-opacity="0.9"/>')
        parts.append(text_el(panel_x + 24, panel_y + 30, "PIPELINE SHAPE",
                             "mono m", 9, spacing=1.4))
        parts.append(text_el(panel_x + panel_w - 24, panel_y + 30, "VISUAL MOTIF",
                             "mono m", 8, spacing=1.2, anchor="end"))
        parts.append(f'  <path d="M{panel_x + 24} {panel_y + 41:g}H{panel_x + panel_w - 24}" stroke="{pal["border"]}" stroke-width="1" stroke-opacity="0.7"/>')

        parts.append(f'  <path d="M{spine} {rows_start:g}V{rows_end:g}" class="wire"/>')
        parts.append(f'  <path d="M{spine} {rows_start:g}V{rows_end:g}" class="vpacket"/>')

        for idx, (label, state, color) in enumerate(STAGES):
            cy = round(rows_start + step * idx, 1)
            if color == "violet":
                parts.append(f'  <polygon points="{spine},{cy - 6:g} {spine + 6},{cy:g} {spine},{cy + 6:g} {spine - 6},{cy:g}" class="gate"/>')
                parts.append(f'  <polygon points="{spine},{cy - 9:g} {spine + 9},{cy:g} {spine},{cy + 9:g} {spine - 9},{cy:g}" fill="none" stroke="{pal["violet"]}" stroke-width="1" stroke-opacity="0.35" class="pulse d2"/>')
            else:
                parts.append(f'  <circle cx="{spine}" cy="{cy:g}" r="3.6" class="{color}"/>')
            parts.append(text_el(spine + 16, round(cy + 3.5, 1), label, "mono t", 10.5, spacing=0.2))
            parts.append(text_el(panel_x + panel_w - 22, round(cy + 3.5, 1), state,
                                 "mono m", 8.5, anchor="end"))
    else:
        line_y = round(h * 0.5, 1)
        x1, x2 = 790, 1152
        parts.append(text_el(x1, line_y - 26, "PIPELINE SHAPE", "mono m", 8.5, spacing=1.3))
        parts.append(f'  <path d="M{x1} {line_y:g}H{x2}" class="wire"/>')
        parts.append(f'  <path d="M{x1} {line_y:g}H{x2}" class="hpacket"/>')
        nodes = (
            (838, "bronze", "bronze", "bronze"),
            (925, "gate", "violet", "gate"),
            (1012, "silver", "silver", "silver"),
            (1100, "gold", "gold", "gold"),
        )
        for nx, label, color, shape in nodes:
            if shape == "gate":
                parts.append(f'  <polygon points="{nx},{line_y - 6:g} {nx + 6},{line_y:g} {nx},{line_y + 6:g} {nx - 6},{line_y:g}" class="gate"/>')
            else:
                parts.append(f'  <circle cx="{nx}" cy="{line_y:g}" r="4" class="{color} pulse d1"/>')
            parts.append(text_el(nx, round(line_y + 17, 1), label, "mono m", 8.5, anchor="middle"))
        parts.append(f'  <path d="M{x2 - 6} {line_y - 4:g}L{x2} {line_y:g}L{x2 - 6} {line_y + 4:g}" fill="none" stroke="{pal["muted"]}" stroke-width="1.2" stroke-opacity="0.7"/>')

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate dark + light animated project hero banner SVGs (stdlib only).")
    parser.add_argument("--title", required=True, help="Project title (required).")
    parser.add_argument("--subtitle", default="", help="One-line subtitle.")
    parser.add_argument("--tags", nargs="*", default=[],
                        help=f"Up to {MAX_TAGS} technology tags.")
    parser.add_argument("--outdir", default=".", help="Output directory (default: cwd).")
    parser.add_argument("--basename", default="banner",
                        help="Output basename; writes <basename>-dark.svg and <basename>-light.svg.")
    parser.add_argument("--height", type=int, default=320,
                        help="Canvas height in px (140-480, default 320).")
    args = parser.parse_args(argv)

    if not args.title.strip():
        parser.error("--title must not be empty")
    if len(args.tags) > MAX_TAGS:
        parser.error(f"at most {MAX_TAGS} tags are allowed (got {len(args.tags)})")
    if not 140 <= args.height <= 480:
        parser.error("--height must be between 140 and 480")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    written = []
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        svg = build_svg(args.title.strip(), args.subtitle.strip(),
                        [t.strip() for t in args.tags if t.strip()],
                        args.height, pal)
        path = outdir / f"{args.basename}-{theme}.svg"
        path.write_text(svg, encoding="utf-8")
        written.append(path)
        print(f"wrote {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
