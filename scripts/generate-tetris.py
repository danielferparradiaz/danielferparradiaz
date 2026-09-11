#!/usr/bin/env python3
"""Genera output/tetris-board.svg — Tetris inverso: las fichas suben y se apilan.

GitHub README no ejecuta JS ni Python en vivo, asi que Python sirve como
generador: corre este script local y commitea el SVG. La animacion es
CSS/SMIL dentro del SVG, que GitHub si reproduce en <img>.
"""
import os

WIDTH, HEIGHT = 1200, 780
LEFT, RIGHT = 60, 1140
PLOT_W = RIGHT - LEFT
BOARD_TOP, BOARD_BASE = 96, 648

PIECES = [
    # (key, titulo, contenido, color, forma)
    ("I", "LENGUAJES",
     "Java  ·  TypeScript  ·  Python  ·  Ruby  ·  Bash",
     "#0A84FF", "I"),
    ("L", "BACKEND",
     "Spring Boot  ·  Spring Cloud  ·  Node.js  ·  NestJS  ·  Express  ·  Laravel",
     "#FF9F0A", "L"),
    ("T", "FRONTEND",
     "Angular  ·  React  ·  Svelte  ·  Flutter  ·  SwiftUI",
     "#BF5AF2", "T"),
    ("O", "INFRAESTRUCTURA",
     "Docker  ·  K8s  ·  PostgreSQL  ·  MySQL  ·  Redis  ·  Neo4j  ·  AWS  ·  Azure  ·  GCP",
     "#FFD60A", "O"),
    ("S", "IA · DATA",
     "Spark  ·  Kafka  ·  Debezium  ·  ETL",
     "#30D158", "S"),
    ("Z", "LIBRERIAS",
     "Pandas  ·  NumPy  ·  scikit-learn  ·  PyTorch  ·  Jupyter",
     "#FF453A", "Z"),
]

PIECE_H, GAP = 72, 12
# y de abajo hacia arriba (contrario al tetris: se apila subiendo)
ys = []
y = BOARD_BASE - PIECE_H
for _ in PIECES:
    ys.append(y)
    y -= (PIECE_H + GAP)
# ys[0] = abajo (LENGUAJES) ... ys[5] = arriba (LIBRERIAS)

DELAYS = [0.15, 1.0, 1.85, 2.7, 3.55, 4.4]


def mini_shape(kind, ox, oy, color):
    s = 13
    cells = {
        "I": [(0, 0), (1, 0), (2, 0), (3, 0)],
        "L": [(0, 0), (1, 0), (2, 0), (2, -1)],
        "T": [(0, 0), (1, 0), (2, 0), (1, -1)],
        "O": [(0, 0), (1, 0), (0, -1), (1, -1)],
        "S": [(1, 0), (2, 0), (0, -1), (1, -1)],
        "Z": [(0, 0), (1, 0), (1, -1), (2, -1)],
    }[kind]
    out = []
    for cx, cy in cells:
        out.append(
            f'<rect x="{ox + cx * (s + 2)}" y="{oy + cy * (s + 2)}" '
            f'width="{s}" height="{s}" rx="2.5" fill="{color}"/>'
        )
    return "".join(out)


pieces_svg = []
for i, ((key, title, techs, color, shape), py, delay) in enumerate(zip(PIECES, ys, DELAYS)):
    cy = py + PIECE_H / 2
    pieces_svg.append(f"""
    <g class="piece p{i}" style="animation-delay:{delay}s">
      <rect x="{LEFT}" y="{py}" width="{PLOT_W}" height="{PIECE_H}" rx="9"
            fill="#14161C" stroke="{color}" stroke-width="1.6"/>
      <rect x="{LEFT}" y="{py}" width="7" height="{PIECE_H}" rx="3.5" fill="{color}"/>
      <rect x="{LEFT}" y="{py}" width="{PLOT_W}" height="{PIECE_H}" rx="9"
            fill="{color}" opacity="0.07"/>
      <rect class="flash" x="{LEFT}" y="{py}" width="{PLOT_W}" height="{PIECE_H}" rx="9"
            fill="#FFFFFF" style="animation-delay:{delay + 1.05}s"/>
      <g opacity="0.95">{mini_shape(shape, LEFT + 26, cy + 6, color)}</g>
      <text x="{LEFT + 128}" y="{cy - 6}" class="mono tag" fill="{color}"
            font-size="14" letter-spacing="3">{key} · {title}</text>
      <text x="{LEFT + 128}" y="{cy + 18}" class="mono tech" fill="#D7DCE3"
            font-size="14.5">{techs}</text>
      <text x="{RIGHT - 18}" y="{cy + 6}" text-anchor="end" class="mono locked"
            font-size="11" letter-spacing="2" fill="{color}"
            style="animation-delay:{delay + 1.1}s">▮ LOCKED</text>
    </g>""")

# particulas que suben (polvo del tablero)
import random
random.seed(7)
particles = []
for k in range(16):
    px = LEFT + 20 + random.random() * (PLOT_W - 40)
    size = 3 + random.random() * 5
    dur = round(3.5 + random.random() * 4, 2)
    dly = round(random.random() * 6, 2)
    col = random.choice(["#0A84FF", "#4FC3FF", "#BF5AF2", "#30D158"])
    particles.append(
        f'<rect x="{px:.0f}" y="{BOARD_BASE - 4}" width="{size:.1f}" height="{size:.1f}" '
        f'rx="1" fill="{col}" class="dust" '
        f'style="animation-duration:{dur}s;animation-delay:{dly}s"/>'
    )

# lineas de grid verticales tipo pozo de tetris
grid = []
cols = 10
for c in range(cols + 1):
    gx = LEFT + c * PLOT_W / cols
    grid.append(f'<line x1="{gx:.1f}" y1="{BOARD_TOP}" x2="{gx:.1f}" y2="{BOARD_BASE}" '
                f'stroke="#1E2230" stroke-width="1"/>')
grid_svg = "\n    ".join(grid)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Reverse tetris stack">
  <defs>
    <style>
      .mono {{ font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace; }}
      .tag {{ font-weight: 700; }}
      .tech {{ font-weight: 400; }}
      .piece {{
        opacity: 0;
        animation: stackUp 1.15s cubic-bezier(.2,.85,.25,1) both;
      }}
      @keyframes stackUp {{
        0%   {{ opacity: 0; transform: translateY(330px) translateX(0); }}
        12%  {{ opacity: 1; }}
        32%  {{ opacity: 1; transform: translateY(190px) translateX(-48px); }}
        52%  {{ opacity: 1; transform: translateY(105px) translateX(42px); }}
        72%  {{ opacity: 1; transform: translateY(38px) translateX(-18px); }}
        86%  {{ opacity: 1; transform: translateY(9px) translateX(8px); }}
        100% {{ opacity: 1; transform: translateY(0) translateX(0); }}
      }}
      .flash {{ opacity: 0; animation: flash .45s ease-out both; }}
      @keyframes flash {{ 0% {{ opacity: 0; }} 25% {{ opacity: .55; }} 100% {{ opacity: 0; }} }}
      .locked {{ opacity: 0; animation: fadeIn .4s ease both; }}
      @keyframes fadeIn {{ to {{ opacity: 1; }} }}
      .dust {{
        opacity: 0;
        animation: dustUp 5s linear infinite;
      }}
      @keyframes dustUp {{
        0% {{ opacity: 0; transform: translateY(0); }}
        12% {{ opacity: .85; }}
        85% {{ opacity: .5; }}
        100% {{ opacity: 0; transform: translateY(-{BOARD_BASE - BOARD_TOP}px); }}
      }}
      .scan {{ animation: scanY 6s linear infinite; }}
      @keyframes scanY {{
        0% {{ transform: translateY(0); opacity: 0; }}
        6% {{ opacity: 1; }}
        92% {{ opacity: 1; }}
        100% {{ transform: translateY({BOARD_BASE - BOARD_TOP}px); opacity: 0; }}
      }}
      .blink {{ animation: blink 1.1s steps(2, start) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      .pulse {{ animation: pulse 2.6s ease-in-out infinite; }}
      @keyframes pulse {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
      .hudIn {{ opacity: 0; animation: fadeIn .6s ease both; animation-delay: 5.6s; }}
      @media (prefers-reduced-motion: reduce) {{
        .piece, .locked {{ opacity: 1; animation: none; }}
        .flash, .dust, .scan, .blink, .pulse {{ animation: none; opacity: 0; }}
        .hudIn {{ opacity: 1; animation: none; }}
      }}
    </style>
    <clipPath id="well"><rect x="{LEFT}" y="{BOARD_TOP}" width="{PLOT_W}" height="{BOARD_BASE - BOARD_TOP}"/></clipPath>
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

  <text x="60" y="40" class="mono" font-size="12" letter-spacing="2.5" fill="#8A8A8A">REVERSE TETRIS //</text>
  <text x="1140" y="40" text-anchor="end" class="mono pulse" font-size="12" letter-spacing="2" fill="#0A84FF">STACK ↑ UP · 6 PIECES</text>
  <text x="60" y="66" class="mono" font-size="11" letter-spacing="1.5" fill="#5B6472">LAS FICHAS SUBEN Y SE APILAN — CONTRARIO AL TETRIS CLASICO <tspan class="blink" fill="#0A84FF">▮</tspan></text>
  <text x="1140" y="66" text-anchor="end" class="mono" font-size="11" letter-spacing="1.5" fill="#5B6472">LEVEL 01 · SCORE 6000</text>

  <g>
    {grid_svg}
    <rect x="{LEFT}" y="{BOARD_TOP}" width="{PLOT_W}" height="{BOARD_BASE - BOARD_TOP}" fill="none" stroke="#2A2F3D"/>
    <line x1="{LEFT}" y1="{BOARD_BASE}" x2="{RIGHT}" y2="{BOARD_BASE}" stroke="#0A84FF" stroke-width="2" opacity="0.8"/>
  </g>

  <g clip-path="url(#well)">
    {''.join(particles)}
    {''.join(pieces_svg)}
    <g class="scan">
      <rect x="{LEFT}" y="{BOARD_TOP - 3}" width="{PLOT_W}" height="3" fill="#4FC3FF" opacity="0.9"/>
      <rect x="{LEFT}" y="{BOARD_TOP - 60}" width="{PLOT_W}" height="60" fill="#0A84FF" opacity="0.10"/>
    </g>
  </g>

  <text x="60" y="{BOARD_BASE + 34}" class="mono" font-size="11" letter-spacing="1.5" fill="#8A8A8A">PISO ↑ · LA BASE ESTA ABAJO, EL STACK CRECE HACIA ARRIBA</text>
  <g class="hudIn">
    <rect x="60" y="{HEIGHT - 78}" width="{PLOT_W}" height="44" rx="8" fill="#0A84FF" opacity="0.12"/>
    <rect x="60" y="{HEIGHT - 78}" width="{PLOT_W}" height="44" rx="8" fill="none" stroke="#0A84FF"/>
    <text x="600" y="{HEIGHT - 50}" text-anchor="middle" class="mono" font-size="13" letter-spacing="3" fill="#4FC3FF">STACK COMPLETE ▮ 6/6 PIECES LOCKED · GG</text>
  </g>
</svg>
"""

os.makedirs("output", exist_ok=True)
with open("output/tetris-board.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print(f"ok: {len(PIECES)} piezas -> output/tetris-board.svg")
