#!/usr/bin/env python3
"""The World Today - Thursday 26 November 2026.

Pure standard library: draws a 1024x1024 newspaper front page as a PNG and
writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output). No network, no
randomness, no clock: two runs write byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (179, 32, 44)
BLUE = (31, 78, 121)
GOLD = (176, 141, 60)
DARK = (24, 38, 58)
ORANGE = (232, 116, 30)
FLAME = (240, 170, 40)
GREY = (112, 112, 105)
LIGHT = (232, 227, 213)
STEEL = (150, 165, 180)

# 5x7 pixel font, uppercase only. Each glyph is 7 rows of 5 characters.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#.###"),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "\\": ("#....", "#....", ".#...", "..#..", "...#.", "....#", "....#"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "{": ("...##", "..#..", "..#..", ".##..", "..#..", "..#..", "...##"),
    "}": ("##...", "..#..", "..#..", "..##.", "..#..", "..#..", "##..."),
    "^": ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "~": (".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."),
}


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER * (W * H))

    def put(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.put(xx, cy + dy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Filled triangle by scanlines; vertices in any order.
        ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
        (ya, xa), (yb, xb), (yc, xc) = ys
        if yc == ya:
            return
        for y in range(ya, yc + 1):
            if y < yb:
                t1 = (y - ya) / (yb - ya) if yb != ya else 0.0
                xa_y = xa + (xb - xa) * t1
            else:
                t1 = (y - yb) / (yc - yb) if yc != yb else 0.0
                xa_y = xb + (xc - xb) * t1
            t2 = (y - ya) / (yc - ya)
            xc_y = xa + (xc - xa) * t2
            lo, hi = int(min(xa_y, xc_y)), int(max(xa_y, xc_y))
            for xx in range(lo, hi + 1):
                self.put(xx, y, color)

    def char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def text(self, x, y, text, scale, color):
        cx = x
        for ch in text.upper():
            self.char(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def wrap(self, text, scale, maxw):
        words = text.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, text, scale, color, maxw, leading):
        for line in self.wrap(text, scale, maxw):
            self.text(x, y, line, scale, color)
            y += 7 * scale + leading
        return y


def png_bytes(c):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += c.px[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        return out + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))


def refinery_scene(c, x, y, w, h):
    """Stylised Ras Tanura refinery at dusk: towers, flames, sea."""
    c.rect(x, y, w, h, DARK)
    # dusk sun
    c.circle(x + w - 52, y + 46, 26, FLAME)
    c.circle(x + w - 52, y + 46, 18, ORANGE)
    # ground + sea
    c.rect(x, y + h - 26, w, 26, (16, 26, 40))
    c.hline(x, y + h - 26, w, STEEL, 2)
    # distillation towers
    towers = [(28, 150, 34), (86, 118, 30), (140, 168, 36), (196, 132, 30),
              (246, 176, 32)]
    base = y + h - 26
    for tx, th, tw in towers:
        c.rect(x + tx, base - th, tw, th, STEEL)
        c.rect(x + tx - 4, base - th, tw + 8, 6, STEEL)
        c.rect(x + tx - 4, base - th // 2, tw + 8, 5, STEEL)
        c.rect(x + tx + tw // 2 - 2, base - th - 22, 4, 22, STEEL)
    # flames on two stacks
    c.triangle(x + 28 + 13, base - 150 - 44, x + 28 + 2, base - 150 - 8,
               x + 28 + 30, base - 150 - 8, ORANGE)
    c.triangle(x + 28 + 13, base - 150 - 30, x + 28 + 7, base - 150 - 8,
               x + 28 + 24, base - 150 - 8, FLAME)
    c.triangle(x + 196 + 11, base - 132 - 36, x + 196 + 2, base - 132 - 8,
               x + 196 + 26, base - 132 - 8, ORANGE)
    # flare stack on the right
    c.rect(x + w - 34, base - 190, 10, 190, STEEL)
    c.triangle(x + w - 29, base - 190 - 34, x + w - 38, base - 190 - 6,
               x + w - 16, base - 190 - 6, ORANGE)
    c.triangle(x + w - 29, base - 190 - 22, x + w - 35, base - 190 - 6,
               x + w - 19, base - 190 - 6, FLAME)
    # caption bar
    c.rect(x, y + h - 26, w, 26, INK)
    c.text(x + 12, y + h - 19, "RAS TANURA REFINERY, SAUDI ARABIA", 1,
           PAPER)


def tile(c, x, y, w, h, kicker, kcolor, headline, body):
    c.rect(x, y, w, 2, INK)
    c.text(x, y + 8, kicker, 2, kcolor)
    yy = c.para(x, y + 28, headline, 3, INK, w, 6)
    c.para(x, yy + 4, body, 2, (58, 58, 52), w, 4)


def main():
    c = Canvas()
    mx = 28
    cw = W - 2 * mx  # 968

    # Masthead
    title = "THE WORLD TODAY"
    c.text((W - c.text_width(title, 7)) // 2, 30, title, 7, INK)
    c.hline(mx, 118, cw, INK, 4)
    c.hline(mx, 126, cw, INK, 1)
    date = "THURSDAY 26 NOVEMBER 2026"
    c.text((W - c.text_width(date, 3)) // 2, 140, date, 3, RED)
    c.text(mx, 140, "WORLD EDITION", 2, GREY)
    right = "PRICE: ONE DAY"
    c.text(W - mx - c.text_width(right, 2), 140, right, 2, GREY)
    c.hline(mx, 168, cw, INK, 2)

    # Lead story
    ly = 186
    c.text(mx, ly, "MIDDLE EAST  -  OIL", 2, RED)
    head = "HOUTHIS HIT SAUDI REFINERY AS BRENT TOPS $94"
    yy = c.para(mx, ly + 26, head, 4, INK, 592, 8)
    deck = ("Yemen's Houthis say they struck Ras Tanura, Saudi Arabia's "
            "largest refinery, and Riyadh's financial district. Saudi "
            "defences down four drones over the site. Brent crude settles "
            "$94.61 a barrel, up 3.5%, and WTI $83.68. A day earlier a "
            "Houthi drone hit a Riyadh tower and hurt 11 people.")
    c.para(mx, yy + 6, deck, 2, (58, 58, 52), 592, 6)
    refinery_scene(c, 648, ly + 4, 348, 268)
    c.hline(mx, 472, cw, INK, 2)

    # Six tiles, two columns x three rows
    tiles = [
        ("MARKETS", RED,
         "TARIFF SHOCK SINKS STOCKS",
         "US proposes tariffs up to 15% on Taiwan goods. The Nasdaq falls "
         "almost 4% as AI fears spread."),
        ("SPACE", BLUE,
         "FIRST FOREIGN CREW ABOARD TIANGONG",
         "Pakistan's Muhammad Zeeshan Ali joins the Shenzhou-24 mission, "
         "the first foreign astronaut to visit Tiangong."),
        ("UKRAINE", RED,
         "MOSCOW'S OWN TOLL: 500,000 DEAD",
         "Russia's own figures show nearly 500,000 military deaths in the "
         "Ukraine war."),
        ("GAZA", BLUE,
         "ISRAELI STRIKE KILLS HAMAS OFFICIAL",
         "An Israeli airstrike in Gaza kills a senior Hamas official and "
         "his family, as the fragile truce strains."),
        ("EGYPT", RED,
         "31 KILLED IN CAIRO TANKER FIRE",
         "A fuel tanker crashes on a Cairo highway and bursts into flames, "
         "killing 31 people."),
        ("NORTH KOREA", BLUE,
         "PYONGYANG EXPELS SWISS DIPLOMAT",
         "North Korea orders Switzerland to close its diplomatic office in "
         "Pyongyang in a row over sanctions."),
    ]
    colw = (cw - 20) // 2
    rowy = [488, 638, 788]
    rowh = 128
    for i, (kick, kcol, head, body) in enumerate(tiles):
        tx = mx + (i % 2) * (colw + 20)
        ty = rowy[i // 2]
        tile(c, tx, ty, colw, rowh, kick, kcol, head, body)
    c.vline(mx + colw + 10, 488, 432, LIGHT, 1)

    # Footer strip
    c.hline(mx, 936, cw, INK, 2)
    foot = ("FED BEIGE BOOK: MODEST GROWTH, STICKY PRICES  -  BANGLADESH "
            "LIFTS GARMENT WAGE 36%  -  COLOMBIA MARKS 10 YEARS OF PEACE "
            "DEAL  -  BEPICOLOMBO REACHES MERCURY")
    c.para(mx, 948, foot, 2, (58, 58, 52), cw, 6)
    c.hline(mx, 996, cw, INK, 4)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png_bytes(c))


if __name__ == "__main__":
    main()
