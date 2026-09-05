import datetime as dt
import re
import urllib.request

USER = "danielferparradiaz"
WIDTH, HEIGHT = 1200, 320
LEFT, RIGHT = 60, 1140
TOP, BASE = 92, 262
PLOT_W = RIGHT - LEFT
PLOT_H = BASE - TOP
FILL_W = 200


def fetch():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "mozill a/5.0"},
    )
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


html = fetch()

dates = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"', html)
counts = []
for m in re.finditer(
    r"((\d+) contributions?|No contributions) on \w+", html
):
    if m.group(2):
        counts.append(int(m.group(2)))
    else:
        counts.append(0)
counts = counts[: len(dates)]
if len(counts) < len(dates):
    counts += [0] * (len(dates) - len(counts))

if not dates:
    dates = [dt.date.today() - dt.timedelta(days=i) for i in range(364, -1, -1)]
    counts = [0] * len(dates)

days = [dt.date.fromisoformat(d) for d in dates]
first = days[0]
n_weeks = (days[-1] - first).days // 7 + 1

weekly = [0] * n_weeks
for day, cnt in zip(days, counts):
    weekly[(day - first).days // 7] += cnt

max_c = max(weekly) or 1
total = sum(counts)
active = sum(1 for w in weekly if w > 0)

n_bars = len(weekly)
gap = 3
bar_w = (PLOT_W - gap * (n_bars - 1)) / n_bars

rects = []
css_bars = []
for i, c in enumerate(weekly):
    h = 3 if c == 0 else max(4, round(3 + (c / max_c) * (PLOT_H - 24)))
    x = LEFT + i * (bar_w + gap)
    y = BASE - h
    opacity = 0.25 if c == 0 else round(0.35 + 0.65 * (c / max_c), 3)
    delay = round(i * 0.035, 3)
    rects.append(
        f'<rect x="{x:.1f}" y="{y}" width="{bar_w:.1f}" height="{h}" '
        f'fill="url(#barGrad)" fill-opacity="{opacity}" rx="1.5" '
        f'class="bar" style="animation-delay:{delay}s" />'
    )

month_last = {}
prev_month = None
for i in range(n_bars):
    wk_start = first + dt.timedelta(days=i * 7)
    m = wk_start.month
    if i == 0 or m != prev_month:
        month_last[m] = i
        ch = i * (bar_w + gap) + LEFT
        css_bars.append(
            f'<text x="{ch:.0f}" y="288" class="mo">'
            f"{wk_start.strftime('%b')}</text>"
        )
    prev_month = m

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Contribution pulse - 52 week waveform">
  <defs>
    <style>
      .mono {{ font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace; }}
      .dim {{ fill: #8A8A8A; }}
      .lit {{ fill: #0A84FF; }}
      .mo {{ font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace; font-size: 10; fill: #6B7280; }}
      .bar {{ transform-box: fill-box; transform-origin: 50% 100%; animation: rise .6s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes rise {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
      @keyframes scan {{ 0% {{ transform: translateX(0); opacity: 0; }} 6% {{ opacity: 1; }} 92% {{ opacity: 1; }} 100% {{ transform: translateX({PLOT_W:.0f}px); opacity: 0; }} }}
      .scan-group {{ animation: scan 7s linear infinite; }}
      @media (prefers-reduced-motion: reduce) {{
        .bar, .scan-group {{ animation: none; }}
      }}
    </style>
    <linearGradient id="barGrad" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#0A84FF" stop-opacity="1"/>
      <stop offset="100%" stop-color="#4FC3FF" stop-opacity="1"/>
    </linearGradient>
    <clipPath id="plot"><rect x="{LEFT}" y="{TOP}" width="{PLOT_W}" height="{PLOT_H}"/></clipPath>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feFlood flood-color="#0A84FF" flood-opacity="0.5"/>
      <feComposite in2="SourceGraphic" operator="in"/>
      <feGaussianBlur stdDeviation="4"/>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" fill="#0A0A0A"/>
  <rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" fill="none" stroke="#2B2B2B"/>

  <g stroke="#3A3A3A">
    <path d="M 44 30 h 12 M 44 30 v 12 M 44 {HEIGHT-30} h 12 M 44 {HEIGHT-30} v -12 M {WIDTH-44} 30 h -12 M {WIDTH-44} 30 v 12 M {WIDTH-44} {HEIGHT-30} h -12 M {WIDTH-44} {HEIGHT-30} v -12"/>
  </g>

  <text x="60" y="34" class="mono dim" font-size="11" letter-spacing="2">ACTIVITY //</text>
  <text x="{RIGHT}" y="37" text-anchor="end" class="mono lit" font-size="11" letter-spacing="1.5">CONTRIBUTION PULSE</text>

  <line x1="{LEFT}" y1="{BASE+2}" x2="{RIGHT}" y2="{BASE+2}" stroke="#2E2E2E"/>
  <line x1="{LEFT}" y1="{TOP-2}" x2="{RIGHT}" y2="{TOP-2}" stroke="#1E1E1E"/>

  <g clip-path="url(#plot)">
    {' '.join(rects)}
    <g class="scan-group" filter="url(#glow)">
      <rect x="{LEFT}" y="{TOP-2}" width="3" height="{BASE-TOP+4}" fill="#4FC3FF"/>
      <rect x="{LEFT}" y="{TOP-2}" width="{FILL_W}" height="{BASE-TOP+4}" fill="url(#barGrad)" opacity="0.18"/>
    </g>
  </g>

  <g class="mono">
    {' '.join(css_bars)}
  </g>

  <text x="{LEFT}" y="{HEIGHT-14}" class="mono dim" font-size="10" letter-spacing="1.5">TOTAL CONTRIBUTIONS · {total}</text>
  <text x="{RIGHT}" y="{HEIGHT-14}" text-anchor="end" class="mono lit" font-size="10" letter-spacing="1">ACTIVE WEEKS · {active}/{n_weeks}</text>
</svg>
"""

with open("output/contribution-wave.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print(f"weeks={n_weeks} total={total} active={active} max={max_c}")