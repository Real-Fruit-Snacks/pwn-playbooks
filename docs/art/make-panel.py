"""Draw the README's animated panel: docs/assets/panel-dark.svg and panel-light.svg.

The panel acts out one playbook in a 16 s loop. On the left, a box's note in vim: :Pb sm, Tab
completes smb, and the SMB playbook is read in. Three values are typed over <Replace> in its run
block, V} selects the block, "qy copies it into register q, and @q runs it: every one of those
placeholders in the playbook becomes its value, and the cursor ends two lines below my, where the
run block leaves it. On the right, the playbooks tree, with smb.md lit once it is read.

Every line of the playbook comes from playbooks/02-enum/smb.md as build.py renders it, at the
newest release in CHANGELOG.md. The run block's lines for the placeholders not filled here are
left out, as if deleted with dd before the run, as is all of the body but one line. A line
longer than the window is cut with an ellipsis. The keys typed in normal mode show at the bottom
right, where vim's showcmd shows part of them.

The SVG's base styles are the moment after the run, which is what a viewer that skips the
animation shows.

Text is converted to paths from the page's own fonts (docs/fonts), because an SVG shown through
<img> can't load fonts. Run from the repo root:

    python -m pip install -r docs/art/requirements.txt
    python docs/art/make-panel.py
"""
import os
import re
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "..", "assets")
sys.path.insert(0, ROOT)

import build as pb  # noqa: E402  (the repository's own build.py)

# RFS Cyclorama Dawn v2.1.0 (LX 263 dark / LX 512 light)
THEMES = {
    "dark": dict(plate="#0D0E12", glass="#050507", line="#242834", ink="#F2F4F8", mute="#8F95A6",
                 ember="#FF9254", mint="#3DDC97", steel="#1F547A", beacon="#F06E2B"),
    "light": dict(plate="#FFFFFF", glass="#F5F7F9", line="#CBD3DD", ink="#11141B", mute="#535B69",
                  ember="#AD3D0A", mint="#127247", steel="#164669", beacon="#BD4811"),
}

W, H = 1000, 430
CYCLE = 16.0        # seconds
TYPE = 0.045        # per typed character (BRAND-RULES.md)
FADE = 0.25         # a row on the right lighting up
EASE = "cubic-bezier(.2,.7,.2,1)"
STILL = 12.5        # the moment the base styles show
OUT_AT = 15.2       # everything fades out, then the loop starts again

MONO = ("azeret-mono-latin.woff2", 400)
MONO_B = ("azeret-mono-latin.woff2", 600)
CUT = "…"

# --- the playbook, as build.py renders it ---
NAME, REL = "smb", "02-enum/smb"
with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as fh:
    VERSION = re.search(r"^## v(\S+)$", fh.read(), re.M)[1]
NAMES, _ = pb.load_placeholders(pb.Path(ROOT) / "placeholders.toml")
with open(os.path.join(ROOT, "playbooks", *REL.split("/")) + ".md", encoding="utf-8") as fh:
    SOURCE, _ = pb.parse_source(fh.read(), REL)
USED = pb.placeholders_used(SOURCE.body, NAMES)
BUILT = pb.render(NAME, REL, SOURCE.title, VERSION, USED, SOURCE.body).split("\n")

FILL = {"TargetIP": "10.10.10.17", "Domain": "corp.local", "Username": "svc_sql"}
if USED[: len(FILL)] != list(FILL):
    sys.exit(f"{REL} no longer starts with the placeholders {list(FILL)}: {USED}")


def run_line(name, value="<Replace>"):
    return f":'y,'zs/<{name}>/{value}/ge"


(FILL_IN,) = [line for line in BUILT if line.startswith("Fill in:")]
(BODY, *_) = [line for line in SOURCE.body if all(f"<{n}>" in line for n in FILL)]
for line in [run_line(n) for n in FILL] + ["my", "mz", "'y"]:
    if line not in BUILT:
        sys.exit(f"the built playbook has no line {line!r}")

ROWS = [BUILT[0], BUILT[1], "my", BUILT[3], "mz", *[run_line(n) for n in FILL], "'y", "", FILL_IN, "",
        BODY]
RUN_ROWS = {name: 5 + i for i, name in enumerate(FILL)}
BLOCK_END = ROWS.index("", 3)  # the blank line that ends the run block, where V} stops
YANKED = BLOCK_END - 2 + 1
CMD_ROW = len(ROWS)          # vim's command line, under the note


def filled(line):
    """A line after @q: each filled placeholder replaced, in the run block's order."""
    for name, value in FILL.items():
        line = line.replace(f"<{name}>", value)
    return line


# --- the timeline ---
T_COLON = 0.6
CMD = ":Pb sm"
T_TAB = T_COLON + len(CMD) * TYPE + 0.5      # Tab completes the name
T_ENTER = T_TAB + 0.5
T_READ = T_ENTER + 0.1                       # the playbook is in the note
T_CA = [2.8, 4.0, 5.0]                       # ca> over each <Replace>
T_V = 6.2                                    # V} on the my line
T_Y = 7.0                                    # "qy
T_AT = 7.9                                   # @q
T_RUN = T_AT + 0.2                           # the run block has run


def typing_end(i):
    return T_CA[i] + 0.15 + len(list(FILL.values())[i]) * TYPE


# --- layout ---
LX, RX, TOP, BOTTOM = 28, 708, 72, 404       # left window from LX, right window from RX to W - 28
L_SIZE, L_PAD, L_FIRST, L_PITCH = 12.6, 18, 102, 22
R_SIZE, R_PAD, R_FIRST, R_PITCH, R_INDENT = 11.8, 14, 102, 20, 12
COLS = 74

# The tree: each folder of playbooks/ with how many playbooks it holds, and in the playbook's own
# folder the playbook between its neighbours. (depth, name, count, is the playbook read in)
_root = pb.Path(ROOT, "playbooks")
_all = sorted(p.relative_to(_root).as_posix() for p in _root.rglob("*.md"))
_home = REL + ".md"
_folder = _home.rsplit("/", 1)[0]
TREE = [(0, "playbooks/", "", False)]
for _top in sorted({r.split("/")[0] for r in _all}):
    TREE.append((1, _top + "/", str(sum(1 for r in _all if r.split("/")[0] == _top)), False))
    if _top == _folder:
        _near = [r for r in _all if r.rsplit("/", 1)[0] == _folder]
        _at = _near.index(_home)
        TREE += [(2, r.rsplit("/", 1)[1], "", r == _home) for r in _near[max(_at - 1, 0) : _at + 2]]
COUNT_COL = 17                               # where the counts end, in characters from the folders

_fonts = {}
_glyphs = {}   # (font, glyph name) -> (id, path in font units); drawn once in <defs>, reused by <use>


def font(spec):
    if spec not in _fonts:
        fname, wght = spec
        tt = TTFont(os.path.join(FONTS, fname))
        if "fvar" in tt:
            tt = instantiateVariableFont(tt, {"wght": wght}, inplace=True)
        _fonts[spec] = tt
    return _fonts[spec]


def char_w(size, fname=MONO):
    f = font(fname)
    return f.getGlyphSet()[f.getBestCmap()[ord("0")]].width * size / f["head"].unitsPerEm


def text(s, x, y, size, fname, fill):
    """Path for `s` with its baseline at y."""
    f = font(fname)
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    k = size / upm
    uses = []
    pen_x = x
    for ch in s:
        if ord(ch) not in cmap:
            sys.exit(f"{fname} has no glyph for {ch!r}")
        n = cmap[ord(ch)]
        key = (fname, n)
        if key not in _glyphs:
            pen = SVGPathPen(gs, ntos=lambda v: "%g" % round(v, 1))
            gs[n].draw(pen)
            _glyphs[key] = (f"g{len(_glyphs)}", pen.getCommands())
        gid, d = _glyphs[key]
        if d:
            uses.append(f'<use href="#{gid}" transform="matrix({k:.5f} 0 0 {-k:.5f} {pen_x:.2f} {y:.2f})"/>')
        pen_x += gs[n].width * k
    return f'<g fill="{fill}">{"".join(uses)}</g>'


_TOKEN = re.compile("|".join(
    [r"<Replace>"] + [re.escape(f"<{n}>") for n in sorted(NAMES, key=len, reverse=True)]
    + [re.escape(v) for v in sorted(FILL.values(), key=len, reverse=True)]
))


def pieces(line, base="ink", mint=False):
    """A line as (text, colour) pieces: placeholders in ember, as the note's syntax shows them,
    and, after the run, the values it put in in mint. Cut to the window with an ellipsis."""
    if len(line) > COLS:
        line = line[: COLS - 1] + CUT
    out, at = [], 0
    for m in _TOKEN.finditer(line):
        if m.start() > at:
            out.append((line[at : m.start()], base))
        word = m.group()
        out.append((word, "ember" if word.startswith("<") else ("mint" if mint else base)))
        at = m.end()
    if at < len(line):
        out.append((line[at:], base))
    return out


def row_face(row):
    return "mute" if row == 0 else "ink"


# Each row of the note is a list of states, (shown from, pieces); a state lasts until the next.
STATES = {row: [] for row in range(CMD_ROW + 1)}
for row, line in enumerate(ROWS):
    STATES[row].append((T_READ, pieces(line, row_face(row))))
for i, (name, value) in enumerate(FILL.items()):
    row = RUN_ROWS[name]
    for k in range(len(value) + 1):
        STATES[row].append((T_CA[i] + 0.15 + k * TYPE if k else T_CA[i], pieces(run_line(name, value[:k]))))
for row, line in enumerate(ROWS):
    if row in RUN_ROWS.values():
        typed = next(run_line(n, FILL[n]) for n, r in RUN_ROWS.items() if r == row)
        STATES[row].append((T_RUN, pieces(typed, row_face(row), mint=True)))
        continue
    final = filled(line)
    if final != line:
        STATES[row].append((T_RUN, pieces(final, row_face(row), mint=True)))

# the command line: :Pb sm typed, Tab completes it, Enter reads; then vim's mode and messages
cmd = STATES[CMD_ROW]
for k in range(1, len(CMD) + 1):
    cmd.append((T_COLON + (k - 1) * TYPE, [(CMD[:k], "ink")]))
cmd.append((T_TAB, [(CMD + "b", "ink")]))
cmd.append((T_ENTER, []))
for i in range(len(FILL)):
    cmd.append((T_CA[i], [("-- INSERT --", "mute")]))
    cmd.append((typing_end(i) + 0.25, []))
cmd.append((T_V + 0.1, [("-- VISUAL LINE --", "mute")]))
cmd.append((T_Y, [(f"{YANKED} lines yanked", "mute")]))
cmd.append((T_AT, []))
cmd.sort(key=lambda s: s[0])

KEYS = [(T_CA[i], "ca>") for i in range(len(FILL))] + [(T_V, "V}"), (T_Y, '"qy'), (T_AT, "@q")]

# the cursor: (from, row, column)
CURSOR = [(0.0, 0, 0)]
for k in range(1, len(CMD) + 1):
    CURSOR.append((T_COLON + (k - 1) * TYPE, CMD_ROW, k))
CURSOR.append((T_TAB, CMD_ROW, len(CMD) + 1))
CURSOR.append((T_READ, 2, 0))
for i, (name, value) in enumerate(FILL.items()):
    col = run_line(name).index("<Replace>")
    CURSOR.append((T_CA[i] - 0.35, RUN_ROWS[name], col))
    for k in range(1, len(value) + 1):
        CURSOR.append((T_CA[i] + 0.15 + k * TYPE, RUN_ROWS[name], col + k))
    CURSOR.append((typing_end(i) + 0.25, RUN_ROWS[name], col + len(value) - 1))
CURSOR.append((T_V, 2, 0))
CURSOR.append((T_RUN, 4, 0))                 # two lines below my, where the block leaves it


def pct(t):
    return f"{t / CYCLE * 100:.3f}%"


class Anim:
    """Collects the keyframes and the still-frame styles, one class per animated element."""

    def __init__(self):
        self.css, self.rules, self.base = [], [], []

    def window(self, name, start, end):
        """Shown from start until end (a terminal drawing), at once."""
        self.base.append(f".{name}{{opacity:{int(start <= STILL < end)}}}")
        frames = [f"0%{{opacity:{int(start <= 0)}}}"]
        if start > 0:
            frames.append(f"{pct(start)}{{opacity:1}}")
        if end < CYCLE:
            frames.append(f"{pct(end)}{{opacity:0}}")
        frames.append(f"100%{{opacity:{int(end >= CYCLE)}}}")
        self.css.append(f"@keyframes {name}{{{''.join(frames)}}}")
        self.rules.append(f".{name}{{animation:{name} {CYCLE}s step-end infinite}}")

    def fade(self, name, t, value):
        """Opacity easing from 1 - value to value at t, over FADE."""
        self.base.append(f".{name}{{opacity:{value if t <= STILL else 1 - value}}}")
        self.css.append(f"@keyframes {name}{{0%{{opacity:{1 - value}}}{pct(t)}{{opacity:{1 - value};"
                        f"animation-timing-function:{EASE}}}{pct(t + FADE)}{{opacity:{value}}}"
                        f"100%{{opacity:{value}}}}}")
        self.rules.append(f".{name}{{animation:{name} {CYCLE}s linear infinite}}")

    def style(self):
        return f"<style>{''.join(self.base)}@media (prefers-reduced-motion:no-preference){{{''.join(self.css)}{''.join(self.rules)}}}</style>"


def check_layout():
    """Stop if a piece leaves its window."""
    cw, rcw = char_w(L_SIZE), char_w(R_SIZE)
    if LX + L_PAD + COLS * cw > RX - 18 - L_PAD + 0.5:
        sys.exit(f"{COLS} columns run past the right edge of the note")
    if L_FIRST + CMD_ROW * L_PITCH + L_SIZE * 0.25 > BOTTOM:
        sys.exit("the note is taller than its window")
    for i, (depth, name, count, _) in enumerate(TREE):
        width = max(len(name), COUNT_COL if count else 0) + (len(NAME) + 6 if depth == 2 else 0)
        if count and len(name) + len(count) + 1 > COUNT_COL:
            sys.exit(f"{name!r} runs into its count")
        if RX + R_PAD + depth * R_INDENT + width * rcw > W - 28 - R_PAD:
            sys.exit(f"{name!r} runs past the right edge of the tree")
        if R_FIRST + i * R_PITCH + R_SIZE * 0.25 > BOTTOM:
            sys.exit(f"{name!r} is below the tree's window")


def draw(theme):
    c = THEMES[theme]
    a = Anim()
    run = []
    cw = char_w(L_SIZE)
    lx0 = LX + L_PAD

    def left_y(row):
        return L_FIRST + row * L_PITCH

    # the visual selection, my down to the blank line, behind the text
    for row in range(2, BLOCK_END + 1):
        name = f"v{row}"
        a.window(name, T_V + 0.1, T_Y)
        top = left_y(row) - L_SIZE * 0.85
        run.append(f'<rect class="{name}" x="{lx0 - 2:.2f}" y="{top:.2f}" width="{(len(ROWS[row]) + 1) * cw + 4:.2f}" '
                   f'height="{L_PITCH - 2}" rx="3" fill="{c["line"]}"/>')

    for row, states in STATES.items():
        states.sort(key=lambda s: s[0])
        for i, (start, parts) in enumerate(states):
            end = states[i + 1][0] if i + 1 < len(states) else CYCLE
            if not parts or end <= start:
                continue
            name = f"r{row}s{i}"
            a.window(name, start, end)
            g, col = [], 0
            for part, colour in parts:
                face = MONO_B if row == 1 else MONO
                g.append(text(part, lx0 + col * cw, left_y(row), L_SIZE, face, c[colour]))
                col += len(part)
            run.append(f'<g class="{name}">{"".join(g)}</g>')

    for i, (start, keys) in enumerate(KEYS):
        name = f"k{i}"
        a.window(name, start, start + 0.6)
        run.append(f'<g class="{name}">{text(keys, lx0 + (COLS - 8) * cw, left_y(CMD_ROW), L_SIZE, MONO, c["mute"])}</g>')

    frames, still = [], CURSOR[0]
    for t, row, col in CURSOR:
        at = f"translate({lx0 + col * cw:.2f}px,{left_y(row) - L_SIZE * 0.8:.2f}px)"
        frames.append(f"{pct(t)}{{transform:{at}}}")
        if t <= STILL:
            still = (t, row, col)
    a.base.append(f".cur{{transform:translate({lx0 + still[2] * cw:.2f}px,{left_y(still[1]) - L_SIZE * 0.8:.2f}px)}}")
    a.css.append(f"@keyframes cur{{{''.join(frames)}}}")
    a.rules.append(f".cur{{animation:cur {CYCLE}s step-end infinite}}")
    run.append(f'<rect class="cur" x="0" y="0" width="{cw:.2f}" height="{L_SIZE * 1.05:.2f}" fill="{c["ink"]}" fill-opacity=".7"/>')

    # the tree, the playbook lighting up once it is read
    rcw = char_w(R_SIZE)
    for i, (depth, name, count, lit) in enumerate(TREE):
        x, y = RX + R_PAD + depth * R_INDENT, R_FIRST + i * R_PITCH
        face = "mute" if name.endswith("/") else "ink"
        if count:
            run.append(text(count, x + (COUNT_COL - len(count)) * rcw, y, R_SIZE, MONO, c["mute"]))
        if lit:
            a.fade("lit", T_READ, 1)
            a.fade("unlit", T_READ, 0)
            run.append(f'<g class="unlit">{text(name, x, y, R_SIZE, MONO, c[face])}</g>')
            run.append(f'<g class="lit">{text(name, x, y, R_SIZE, MONO_B, c["ember"])}'
                       f'{text(":Pb " + NAME, x + (len(name) + 2) * rcw, y, R_SIZE, MONO, c["mute"])}</g>')
        else:
            run.append(text(name, x, y, R_SIZE, MONO, c[face]))

    a.base.append(".run{opacity:1}")
    a.css.append(f"@keyframes run{{0%{{opacity:1}}{pct(OUT_AT)}{{opacity:1;animation-timing-function:{EASE}}}"
                 f"{pct(OUT_AT + 0.5)}{{opacity:0}}100%{{opacity:0}}}}")
    a.rules.append(f".run{{animation:run {CYCLE}s linear infinite}}")

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">']
    o.append(a.style())
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{c["plate"]}" stroke="{c["line"]}"/>')
    o.append(f'<rect x="0" y="0" width="{W}" height="3" fill="url(#rfs-bar)" clip-path="url(#card-clip)"/>')
    o.append(text("notes.md", LX, 50, 14.5, MONO_B, c["mute"]))
    o.append(text("pwn-playbooks/", RX, 50, 14.5, MONO, c["mute"]))
    o.append(f'<rect x="{LX}" y="{TOP}" width="{RX - 18 - LX}" height="{BOTTOM - TOP}" rx="8" fill="{c["glass"]}" stroke="{c["line"]}"/>')
    o.append(f'<rect x="{RX}" y="{TOP}" width="{W - 28 - RX}" height="{BOTTOM - TOP}" rx="8" fill="none" stroke="{c["line"]}"/>')
    o.append(f'<g class="run">{"".join(run)}</g>')
    card_clip = f'<clipPath id="card-clip"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10"/></clipPath>'
    bar_grad = (
        f'<linearGradient id="rfs-bar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{c["steel"]}"/>'
        f'<stop offset="55%" stop-color="{c["steel"]}"/>'
        f'<stop offset="100%" stop-color="{c["beacon"]}"/>'
        f'</linearGradient>'
    )
    defs = card_clip + bar_grad + "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in _glyphs.values() if d)
    o.insert(1, f"<defs>{defs}</defs>")
    o.append("</svg>")
    return "".join(o)


check_layout()
for theme in THEMES:
    _glyphs.clear()
    path = os.path.join(OUT, f"panel-{theme}.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(draw(theme) + "\n")
    print(f"wrote {os.path.relpath(path)} ({os.path.getsize(path) // 1024} KB)")
