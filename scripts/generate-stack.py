#!/usr/bin/env python3
"""Genera output/stack-board.svg — bloques de colores por stack.

Entran de arriba hacia abajo con animaciones aleatorias: impactos
laterales tipo camion de carga, caidas con rebote y derrapes.
CSS dentro del SVG = GitHub lo reproduce en <img>.
"""
import os
import random

WIDTH, HEIGHT = 1200, 780
LEFT, RIGHT = 60, 1140
PLOT_W = RIGHT - LEFT
BOARD_TOP, BOARD_BASE = 96, 648

# Orden visual de arriba hacia abajo. El primero en aparecer es LIBRERIAS.
LAYERS = [
    # (titulo, contenido, color, anim, delay)
    ("LIBRERIAS",
     "Pandas  ·  NumPy  ·  scikit-learn  ·  PyTorch  ·  Jupyter",
     "#FF453A", "crashLeft", 0.15),
    ("IA · DATA",
     "Spark  ·  Kafka  ·  Debezium  ·  ETL",
     "#30D158", "crashRight", 0.95),
    ("INFRAESTRUCTURA",
     "Docker  ·  K8s  ·  PostgreSQL  ·  MySQL  ·  Redis  ·  Neo4j  ·  AWS  ·  Azure  ·  GCP",
     "#FFD60A", "dropBounce", 1.75),
    ("FRONTEND",
     "Angular  ·  React  ·  Svelte  ·  Flutter  ·  SwiftUI",
     "#BF5AF2", "driftLeft", 2.55),
    ("BACKEND",
     "Spring Boot  ·  Spring Cloud  ·  Node.js  ·  NestJS  ·  Express  ·  Laravel",
     "#FF9F0A", "driftRight", 3.35),
    ("LENGUAJES",
     "Java  ·  TypeScript  ·  Python  ·  Ruby  ·  Bash  ·  Rust  ·  Go",
     "#0A84FF", "dropSpin", 4.15),
]

BLOCK_H, GAP = 72, 12
ys = []
y = BOARD_TOP + 8
for _ in LAYERS:
    ys.append(y)
    y += (BLOCK_H + GAP)


def layer_icon(ox, oy, color, num):
    # Cubo-nivel generico: circulo con numero + 3 lineas de "capas"
    return (
        f'<circle cx="{ox}" cy="{oy}" r="17" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<text x="{ox}" y="{oy + 5}" text-anchor="middle" class="mono" '
        f'font-size="13" font-weight="700" fill="{color}">{num}</text>'
        f'<g stroke="{color}" stroke-width="2.4" opacity="0.85">'
        f'<line x1="{ox + 26}" y1="{oy - 8}" x2="{ox + 58}" y2="{oy - 8}"/>'
        f'<line x1="{ox + 26}" y1="{oy}" x2="{ox + 66}" y2="{oy}"/>'
        f'<line x1="{ox + 26}" y1="{oy + 8}" x2="{ox + 52}" y2="{oy + 8}"/>'
        f"</g>"
    )


blocks_svg = []
for i, ((title, techs, color, anim, delay), by) in enumerate(zip(LAYERS, ys)):
    cy = by + BLOCK_H / 2
    num = f"{i + 1:02d}"
    blocks_svg.append(f"""
    <g class="block {anim}" style="animation-delay:{delay}s">
      <rect x="{LEFT}" y="{by}" width="{PLOT_W}" height="{BLOCK_H}" rx="9"
            fill="#14161C" stroke="{color}" stroke-width="1.6"/>
      <rect x="{LEFT}" y="{by}" width="7" height="{BLOCK_H}" rx="3.5" fill="{color}"/>
      <rect x="{LEFT}" y="{by}" width="{PLOT_W}" height="{BLOCK_H}" rx="9"
            fill="{color}" opacity="0.07"/>
      <rect class="impact" x="{LEFT}" y="{by}" width="{PLOT_W}" height="{BLOCK_H}" rx="9"
            fill="#FFFFFF" style="animation-delay:{delay + 0.95}s"/>
      <g opacity="0.95">{layer_icon(LEFT + 30, cy, color, num)}</g>
      <text x="{LEFT + 128}" y="{cy - 6}" class="mono tag" fill="{color}"
            font-size="14" letter-spacing="3">{title}</text>
      <text x="{LEFT + 128}" y="{cy + 18}" class="mono tech" fill="#D7DCE3"
            font-size="14.5">{techs}</text>
      <text x="{RIGHT - 18}" y="{cy + 6}" text-anchor="end" class="mono layerTag"
            font-size="11" letter-spacing="2" fill="{color}"
            style="animation-delay:{delay + 1.0}s">LAYER {num} / 06</text>
    </g>""")

random.seed(11)
particles = []
for _ in range(14):
    px = LEFT + 20 + random.random() * (PLOT_W - 40)
    size = round(3 + random.random() * 5, 1)
    dur = round(3.5 + random.random() * 4, 2)
    dly = round(random.random() * 6, 2)
    col = random.choice(["#0A84FF", "#4FC3FF", "#BF5AF2", "#30D158", "#FFD60A"])
    particles.append(
        f'<rect x="{px:.0f}" y="{BOARD_BASE - 4}" width="{size}" height="{size}" '
        f'rx="1" fill="{col}" class="dust" '
        f'style="animation-duration:{dur}s;animation-delay:{dly}s"/>'
    )

# repisas horizontales: cada bloque es un nivel
shelves = []
for by in ys:
    shelves.append(
        f'<line x1="{LEFT}" y1="{by + BLOCK_H + GAP / 2}" x2="{RIGHT}" '
        f'y2="{by + BLOCK_H + GAP / 2}" stroke="#20242F" stroke-width="1" '
        f'stroke-dasharray="2 6"/>'
    )
shelves_svg = "\n    ".join(shelves)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Stack de tecnologias por capas">
  <defs>
    <style>
      .mono {{ font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace; }}
      .tag {{ font-weight: 700; }}
      .tech {{ font-weight: 400; }}
      .block {{ opacity: 0; animation-duration: 1.05s; animation-timing-function: cubic-bezier(.2,.85,.25,1); animation-fill-mode: both; }}
      /* 01 LIBRERIAS — camion que se estrella desde la izquierda */
      .crashLeft {{ animation-name: crashLeft; }}
      @keyframes crashLeft {{
        0%   {{ opacity: 0; transform: translateX(-1150px) rotate(-7deg); }}
        12%  {{ opacity: 1; }}
        55%  {{ opacity: 1; transform: translateX(46px) rotate(2.5deg); }}
        72%  {{ opacity: 1; transform: translateX(-16px) rotate(-1.2deg); }}
        86%  {{ opacity: 1; transform: translateX(7px) rotate(.5deg); }}
        100% {{ opacity: 1; transform: translateX(0) rotate(0); }}
      }}
      /* 02 IA·DATA — camion que se estrella desde la derecha */
      .crashRight {{ animation-name: crashRight; }}
      @keyframes crashRight {{
        0%   {{ opacity: 0; transform: translateX(1150px) rotate(7deg); }}
        12%  {{ opacity: 1; }}
        55%  {{ opacity: 1; transform: translateX(-46px) rotate(-2.5deg); }}
        72%  {{ opacity: 1; transform: translateX(16px) rotate(1.2deg); }}
        86%  {{ opacity: 1; transform: translateX(-7px) rotate(-.5deg); }}
        100% {{ opacity: 1; transform: translateX(0) rotate(0); }}
      }}
      /* 03 INFRA — caida pesada con rebote */
      .dropBounce {{ animation-name: dropBounce; }}
      @keyframes dropBounce {{
        0%   {{ opacity: 0; transform: translateY(-460px) scaleY(1.06); }}
        14%  {{ opacity: 1; }}
        58%  {{ opacity: 1; transform: translateY(26px) scaleY(.96); }}
        74%  {{ opacity: 1; transform: translateY(-12px) scaleY(1.02); }}
        88%  {{ opacity: 1; transform: translateY(5px) scaleY(.99); }}
        100% {{ opacity: 1; transform: translateY(0) scaleY(1); }}
      }}
      /* 04 FRONTEND — derrape lateral con inclinacion */
      .driftLeft {{ animation-name: driftLeft; }}
      @keyframes driftLeft {{
        0%   {{ opacity: 0; transform: translateX(-700px) translateY(-120px) rotate(-4deg); }}
        15%  {{ opacity: 1; }}
        60%  {{ opacity: 1; transform: translateX(34px) translateY(10px) rotate(1.6deg); }}
        78%  {{ opacity: 1; transform: translateX(-10px) translateY(-3px) rotate(-.7deg); }}
        100% {{ opacity: 1; transform: translateX(0) translateY(0) rotate(0); }}
      }}
      /* 05 BACKEND — derrape espejo desde la derecha */
      .driftRight {{ animation-name: driftRight; }}
      @keyframes driftRight {{
        0%   {{ opacity: 0; transform: translateX(700px) translateY(-140px) rotate(4deg); }}
        15%  {{ opacity: 1; }}
        60%  {{ opacity: 1; transform: translateX(-34px) translateY(10px) rotate(-1.6deg); }}
        78%  {{ opacity: 1; transform: translateX(10px) translateY(-3px) rotate(.7deg); }}
        100% {{ opacity: 1; transform: translateX(0) translateY(0) rotate(0); }}
      }}
      /* 06 LENGUAJES — caida con giro que se asienta */
      .dropSpin {{ animation-name: dropSpin; }}
      @keyframes dropSpin {{
        0%   {{ opacity: 0; transform: translateY(-520px) rotate(-9deg); }}
        14%  {{ opacity: 1; }}
        58%  {{ opacity: 1; transform: translateY(20px) rotate(3deg); }}
        75%  {{ opacity: 1; transform: translateY(-9px) rotate(-1.4deg); }}
        89%  {{ opacity: 1; transform: translateY(4px) rotate(.6deg); }}
        100% {{ opacity: 1; transform: translateY(0) rotate(0); }}
      }}
      .impact {{ opacity: 0; animation: impact .45s ease-out both; }}
      @keyframes impact {{ 0% {{ opacity: 0; }} 25% {{ opacity: .5; }} 100% {{ opacity: 0; }} }}
      .layerTag {{ opacity: 0; animation: fadeIn .4s ease both; }}
      @keyframes fadeIn {{ to {{ opacity: 1; }} }}
      .dust {{ opacity: 0; animation: dustUp 5s linear infinite; }}
      @keyframes dustUp {{
        0% {{ opacity: 0; transform: translateY(0); }}
        12% {{ opacity: .8; }}
        85% {{ opacity: .45; }}
        100% {{ opacity: 0; transform: translateY(-{BOARD_BASE - BOARD_TOP}px); }}
      }}
      .blink {{ animation: blink 1.1s steps(2, start) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      .pulse {{ animation: pulse 2.6s ease-in-out infinite; }}
      @keyframes pulse {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
      .hudIn {{ opacity: 0; animation: fadeIn .6s ease both; animation-delay: 5.4s; }}
      @media (prefers-reduced-motion: reduce) {{
        .block, .layerTag {{ opacity: 1; animation: none; }}
        .impact, .dust, .blink, .pulse {{ animation: none; opacity: 0; }}
        .hudIn {{ opacity: 1; animation: none; }}
      }}
    </style>
    <clipPath id="stage"><rect x="{LEFT}" y="{BOARD_TOP}" width="{PLOT_W}" height="{BOARD_BASE - BOARD_TOP}"/></clipPath>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0E1420"/>
      <stop offset="100%" stop-color="#0A0A0A"/>
    </linearGradient>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bgGrad)"/>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" fill="none" stroke="#2B2B2B"/>
  <g stroke="#3A3A3A">
    <path d="M 44 30 h 12 M 44 30 v 12 M 44 {HEIGHT - 30} h 12 M 44 {HEIGHT - 30} v -12 M {WIDTH - 44} 30 h -12 M {WIDTH - 44} 30 v 12 M {WIDTH - 44} {HEIGHT - 30} h -12 M {WIDTH - 44} {HEIGHT - 30} v -12"/>
  </g>

  <text x="60" y="40" class="mono" font-size="12" letter-spacing="2.5" fill="#8A8A8A">SYSTEM //</text>
  <text x="1140" y="40" text-anchor="end" class="mono pulse" font-size="12" letter-spacing="2" fill="#0A84FF">6 LAYERS · LIVE</text>
  <text x="60" y="66" class="mono" font-size="11" letter-spacing="1.5" fill="#5B6472">THE TECHNOLOGY UPGRADES EVERY TIME <tspan class="blink" fill="#0A84FF">▮</tspan></text>
  <text x="1140" y="66" text-anchor="end" class="mono" font-size="11" letter-spacing="1.5" fill="#5B6472">BUILD 2026 · v3.0</text>

  <g>
    <rect x="{LEFT}" y="{BOARD_TOP}" width="{PLOT_W}" height="{BOARD_BASE - BOARD_TOP}" fill="none" stroke="#2A2F3D"/>
    {shelves_svg}
  </g>

  <g clip-path="url(#stage)">
    {''.join(particles)}
    {''.join(blocks_svg)}
  </g>

  <text x="60" y="{BOARD_BASE + 34}" class="mono" font-size="11" letter-spacing="1.5" fill="#8A8A8A">THE TECHNOLOGY UPGRADES EVERY TIME</text>
  <g class="hudIn">
    <rect x="60" y="{HEIGHT - 78}" width="{PLOT_W}" height="44" rx="8" fill="#0A84FF" opacity="0.12"/>
    <rect x="60" y="{HEIGHT - 78}" width="{PLOT_W}" height="44" rx="8" fill="none" stroke="#0A84FF"/>
    <text x="600" y="{HEIGHT - 50}" text-anchor="middle" class="mono" font-size="13" letter-spacing="3" fill="#4FC3FF">SYSTEM ONLINE ▮ 6/6 LAYERS READY</text>
  </g>
</svg>
"""

os.makedirs("output", exist_ok=True)
with open("output/stack-board.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print(f"ok: {len(LAYERS)} bloques -> output/stack-board.svg")
