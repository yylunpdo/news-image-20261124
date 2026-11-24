#!/usr/bin/env python3
"""news-image-20261124: sum up Tuesday 24 November 2026 in one image.

Pure Python 3.13 standard library only. Draws a 1024x1024
newspaper-style front page -- masthead, three lead stories, a numbered
world map, a day-in-numbers panel, and a 64-story index across 8
regions -- and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). Runs twice byte-identical, no network.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
NAVY = (11, 31, 58)
GOLD = (242, 193, 78)
CREAM = (244, 241, 234)
RED = (192, 57, 43)
INK = (30, 30, 30)
GREY = (110, 110, 110)
OCEAN = (186, 214, 235)
LAND = (196, 196, 178)
LAND_EDGE = (150, 150, 135)
DOT = (192, 57, 43)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, written as strings, '#' = ink.
_GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
}

FONT = {}
for _ch, _rows in _GLYPHS.items():
    FONT[_ch] = tuple(int(_r, 2) for _r in _rows)
BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(text, scale):
    return len(text) * 6 * scale - scale


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def rect(self, x, y, w, h, color):
        r, g, b = color
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def disc(self, cx, cy, rad, color):
        r, g, b = color
        for yy in range(cy - rad, cy + rad + 1):
            for xx in range(cx - rad, cx + rad + 1):
                dx, dy = xx - cx, yy - cy
                if dx * dx + dy * dy <= rad * rad:
                    if 0 <= xx < self.w and 0 <= yy < self.h:
                        i = (yy * self.w + xx) * 3
                        self.px[i] = r
                        self.px[i + 1] = g
                        self.px[i + 2] = b

    def text(self, x, y, s, scale, color):
        r, g, b = color
        cx = x
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT.get(ch, BLANK))
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        px0 = cx + col * scale
                        py0 = y + row * scale
                        for yy in range(py0, py0 + scale):
                            if 0 <= yy < self.h:
                                for xx in range(px0, px0 + scale):
                                    if 0 <= xx < self.w:
                                        i = (yy * self.w + xx) * 3
                                        self.px[i] = r
                                        self.px[i + 1] = g
                                        self.px[i + 2] = b
            cx += 6 * scale

    def text_center(self, y, s, scale, color, cx_mid=None):
        if cx_mid is None:
            cx_mid = self.w // 2
        self.text(cx_mid - text_width(s, scale) // 2, y, s, scale, color)


def wrap(text, max_chars):
    """Greedy word wrap, returns list of lines of at most max_chars."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- content
# All stories first reported on Tuesday 24 November 2026, drawn from
# Reuters, AP, BBC, CNN, UN News, Euronews, The Kyiv Independent,
# Just Security, Carbon Brief, PINA and other public news sources.
LEADS = [
    ("1", "IRAN SHUTS HORMUZ AS MINES HIT TANKERS",
     "4 tankers hit; Tehran sets terms to reopen"),
    ("2", "HUANG BACK AT NVIDIA",
     "Trump pressed board; shares jump 31% in a day"),
    ("3", "MYANMAR GUILTY OF GENOCIDE",
     "ICJ rules on Rohingya; UK announces sanctions"),
]

REGIONS = [
    ("NORTH AMERICA", (31, 78, 121), [
        "Nvidia brings back Huang as CEO; +31%",
        "S&P 500 jumps 4.73% on Nvidia relief",
        "Trump orders faster federal executions",
        "Trump slams Newsom death-row move",
        "Trump approval 45%, lowest of 2nd term",
        "Mexico arrests Sinaloa cartel kingpin",
        "Pentagon: Canada falls short as partner",
        "Oregon, Virginia sue SpaceX over Grok",
    ]),
    ("LATIN AMERICA", (123, 45, 139), [
        "Car bomb injures 23 in Colombia",
        "Maduro spends first birthday behind bars",
        "Bolsonaro rushed to ICU in Brasilia",
        "Bukele seeks third term in El Salvador",
        "Brazil cuts growth outlook; real weakens",
        "3 Salvadoran soldiers die in Haiti blast",
        "Argentina moves to scrap open primaries",
        "Chile sends 2027 budget to the Senate",
    ]),
    ("EUROPE", (20, 90, 50), [
        "UK warns firms of Russian sabotage risk",
        "EU proposes 22nd Russia sanctions pack",
        "Germany first into Ukraine Delta system",
        "NATO vows space defence vs Russia threat",
        "Zelensky urges NATO to admit Ukraine",
        "Hungary PM meets Zelensky in Uzhhorod",
        "Russian drone enters Polish airspace",
        "Spain court amnesties Puigdemont",
    ]),
    ("MIDDLE EAST", (126, 81, 9), [
        "4 tankers hit mines in Strait of Hormuz",
        "Israel kills Hamas security chief, Gaza",
        "UK sanctions Houthis and 4 officials",
        "Saudi strikes kill 25 in Yemen: Saba",
        "Iraq takes over Kurdish oilfields",
        "Haftar visits Turkey for first time",
        "Ukraine 'sank Russian ship off Libya'",
        "Qatar PM seeks to revive US-Iran talks",
    ]),
    ("AFRICA", (147, 81, 22), [
        "DRC fighting traps Ebola responders: WHO",
        "Somalia, Uganda step up anti-Shabaab ops",
        "Boat capsizes in Nigeria; 24 dead",
        "Gunmen kill 6 at Delta campaign event",
        "Kenya, DRC restore full diplomatic ties",
        "Amnesty seeks probe on Ethiopia killings",
        "S Sudan sets Feb 2027 for first election",
        "Sudan drones kill 4 near Khartoum",
    ]),
    ("ASIA", (176, 58, 46), [
        "India overtakes Russia as Asia's No.3",
        "Indonesia factory fire kills 26",
        "S Korea scrambles jets on Russian planes",
        "ICJ: Myanmar guilty of Rohingya genocide",
        "China: official gets death for spying",
        "Japan-India first missile drills on land",
        "India pledges $1.6bn to rebuild Nepal",
        "Trump to meet Xi in Shenzhen at APEC",
    ]),
    ("OCEANIA", (14, 102, 85), [
        "Australia blamed for COP31 flop",
        "Pacific islands get no relief from COP31",
        "Fiji shuts schools in El Nino drought",
        "Solomons ditch China pact for Australia",
        "Solomons PM heads to Canberra for treaty",
        "NZ-India Test drawn in Wellington",
        "England level T20 series in Australia",
        "Kiribati evacuates remote Kanton Island",
    ]),
    ("SPORT, TECH & CLIMATE", (90, 60, 110), [
        "COP31 ends in deadlock, first since 2009",
        "El Nino 'public-health emergency' urged",
        "AI drops climate facts when pressed: UN",
        "Geoengineering 'could backfire': study",
        "US data centres use 1.8% of US power",
        "Arm extends CEO Haas tenure to 2033",
        "FIFA names 2031, 2035 Women's Cup hosts",
        "Babar Azam stars on ILT20 debut: 86",
    ]),
]

NUMBERS = [
    "S&P 500  +4.73%",
    "Nikkei 225  +3.91%",
    "Brent crude  $86.71",
    "Nvidia  +31% in a day",
    "700k+ Russian troops killed",
    "$375k bounty on AI cheats",
    "24  dead in Indonesia fire",
    "COP31: no deal since 2009",
]

# Coarse equirectangular world map, 64 x 22 cells (lon -180..180,
# lat 85..-55). Each row: list of (first, last) inclusive land columns.
MAP_ROWS = [
    [(8, 15), (18, 20), (40, 58)],
    [(5, 16), (17, 20), (31, 32), (37, 60)],
    [(4, 16), (18, 19), (30, 33), (36, 60)],
    [(5, 16), (29, 34), (36, 58)],
    [(6, 18), (28, 35), (37, 56)],
    [(7, 18), (28, 38), (39, 55), (58, 59)],
    [(8, 18), (29, 34), (38, 54), (57, 59)],
    [(8, 18), (29, 35), (37, 55), (57, 58)],
    [(8, 17), (30, 35), (37, 39), (40, 53), (57, 58)],
    [(9, 14), (30, 38), (38, 40), (41, 46), (47, 52)],
    [(10, 15), (30, 38), (42, 44), (47, 52)],
    [(12, 13), (15, 18), (30, 38), (48, 51)],
    [(14, 19), (31, 37), (49, 54)],
    [(14, 19), (31, 38), (50, 55)],
    [(14, 17), (32, 36), (50, 56)],
    [(14, 17), (32, 35), (53, 59)],
    [(14, 16), (32, 34), (53, 59)],
    [(14, 16), (32, 34), (53, 58)],
    [(14, 15), (32, 33), (54, 58)],
    [(15, 15), (54, 59), (60, 61)],
    [(60, 61)],
    [(60, 60)],
]

# (lon, lat) of the numbered dots on the map.
DOTS = [
    (-77, 39), (-99, 19), (-73, 4), (0, 51.5), (30.5, 50.5),
    (34.5, 31.5), (56.5, 26.5), (6, 4.5), (29, 1.5), (77, 28.6),
    (106, -6), (127, 37.5), (151, -33.9), (114, 22.5),
]
LEGEND_1 = "1 Washington  2 Mexico City  3 Villavicencio  4 London  5 Kyiv  6 Gaza  7 Hormuz"
LEGEND_2 = "8 Bayelsa  9 Ituri  10 New Delhi  11 Banten  12 Seoul  13 Sydney  14 Shenzhen"


def dot_xy(lon, lat, mx, my, cell):
    col = (lon + 180.0) / 360.0 * 64.0
    row = (85.0 - lat) / 140.0 * 22.0
    return (int(mx + col * cell), int(my + row * cell))


# ------------------------------------------------------------------- drawing
def draw(c):
    # Masthead.
    c.rect(0, 0, W, 76, NAVY)
    c.text(16, 12, "MAKE.FUN", 1, GOLD)
    c.text(W - 16 - text_width("100 USDC IN PRIZES", 1), 12,
           "100 USDC IN PRIZES", 1, GOLD)
    c.text_center(8, "THE WORLD IN ONE DAY", 4, WHITE)
    c.text_center(46, "TUESDAY, 24 NOVEMBER 2026", 2, GOLD)

    # Lead stories.
    c.rect(0, 76, W, 88, CREAM)
    col_w = W // 3
    for i, (num, head, sub) in enumerate(LEADS):
        x = i * col_w
        c.disc(x + 28, 108, 13, RED)
        c.text(x + 28 - 3, 102, num, 1, WHITE)
        lines = wrap(head, 24)
        ly = 84
        for line in lines:
            c.text(x + 48, ly, line, 2, INK)
            ly += 15
        c.text(x + 48, ly + 2, sub, 1, GREY)
        if i:
            c.rect(x, 84, 2, 72, (210, 205, 190))

    # World map panel.
    map_y = 164
    c.rect(0, map_y, W, 240, WHITE)
    c.text(16, map_y + 6, "WHERE IT HAPPENED", 2, NAVY)
    mx, my, cell = 16, map_y + 26, 9
    c.rect(mx - 2, my - 2, 64 * cell + 4, 22 * cell + 4, (160, 190, 210))
    c.rect(mx, my, 64 * cell, 22 * cell, OCEAN)
    for r, spans in enumerate(MAP_ROWS):
        for a, b in spans:
            c.rect(mx + a * cell, my + r * cell,
                   (b - a + 1) * cell, cell, LAND)
    for i, (lon, lat) in enumerate(DOTS):
        dx, dy = dot_xy(lon, lat, mx, my, cell)
        c.disc(dx + cell // 2, dy + cell // 2, 10, DOT)
        label = str(i + 1)
        c.text(dx + cell // 2 - text_width(label, 1) // 2,
               dy + cell // 2 - 4, label, 1, WHITE)
    c.text(16, map_y + 26 + 22 * cell + 8, LEGEND_1, 1, INK)
    c.text(16, map_y + 26 + 22 * cell + 18, LEGEND_2, 1, INK)

    # Day in numbers panel (right of the map).
    px = 668
    c.rect(px, map_y, W - px, 240, NAVY)
    c.text(px + 16, map_y + 10, "THE DAY IN NUMBERS", 2, GOLD)
    ny = map_y + 40
    for line in NUMBERS:
        c.text(px + 16, ny, line, 2, WHITE)
        ny += 25

    # Index: 8 region blocks, 2 columns x 4 rows.
    idx_y = 404
    block_w = 500
    block_h = 144
    gap = 6
    for k, (name, color, stories) in enumerate(REGIONS):
        row, col = divmod(k, 2)
        bx = 8 + col * (block_w + 8)
        by = idx_y + row * (block_h + gap)
        c.rect(bx, by, block_w, 22, color)
        c.text(bx + 10, by + 4, name, 2, WHITE)
        c.text(bx + block_w - 10 - text_width("8 STORIES", 1), by + 7,
               "8 STORIES", 1, (220, 220, 220))
        for j, story in enumerate(stories):
            c.text(bx + 10, by + 25 + j * 15, story, 2, INK)
        c.rect(bx, by + 22, block_w, 1, (200, 200, 200))

    # Footer.
    c.rect(0, 998, W, 26, NAVY)
    c.text_center(1005,
                  "Sources: Reuters, AP, BBC, CNN, UN News, Euronews, PINA - all stories first reported 24 Nov 2026",
                  1, (200, 210, 225))


# ------------------------------------------------------------------- PNG out
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * canvas.w * 3:(y + 1) * canvas.w * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h,
                                      8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    canvas = Canvas(W, H, WHITE)
    draw(canvas)
    size = write_png(os.path.join(outdir, "entry.png"), canvas)
    print("wrote %s (%d bytes, %dx%d)"
          % (os.path.join(outdir, "entry.png"), size, W, H))


if __name__ == "__main__":
    main()
