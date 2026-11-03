# """Builds every graphic in the Shehnaz-R GitHub profile README  (WHITE + BLUE edition).

# Each SVG is self-contained: fonts are subset and embedded, images are inlined,
# so nothing breaks when GitHub proxies the file. Run: python build_annotated.py
# Outputs go to assets/dark and assets/light (hero, CTA and social badges are shared).

# Design language
#   * light theme : crisp white cards on an ice-blue canvas, royal-blue accents
#   * dark theme  : deep midnight-blue cards, soft sky-blue accents
#   * hero / CTA  : airy white-to-sky hero, saturated blue gradient call-to-action
# """
# import base64
# import io
# import logging
# import os
# import re
# from html import escape

# from fontTools import subset
# from fontTools.ttLib import TTFont
# from fontTools.varLib import instancer
# from PIL import Image

# logging.getLogger("fontTools").setLevel(logging.ERROR)

# # --------------------------------------------------------------------------
# # PROJECT PATHS
# # Supported layouts:
# #   New/build_annotated.py     + New/assets/Profile svg.svg
# #   project/tools/build_annotated.py + project/assets/Profile svg.svg
# # --------------------------------------------------------------------------
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# if os.path.basename(SCRIPT_DIR).lower() == "tools":
#     ROOT = PARENT_DIR
# elif os.path.isdir(os.path.join(SCRIPT_DIR, "assets")):
#     ROOT = SCRIPT_DIR
# elif os.path.isdir(os.path.join(PARENT_DIR, "assets")):
#     ROOT = PARENT_DIR
# else:
#     ROOT = SCRIPT_DIR

# OUT = os.path.join(ROOT, "assets")
# DOCS = ROOT
# CP = ROOT

# _TOOL_CANDIDATES = [
#     os.path.join(ROOT, "tools"),
#     SCRIPT_DIR,
#     os.path.join(PARENT_DIR, "tools"),
#     os.path.join(PARENT_DIR, "Tools"),
# ]
# TOOLS = next(
#     (c for c in _TOOL_CANDIDATES
#      if os.path.isdir(os.path.join(c, "fonts")) or os.path.isdir(os.path.join(c, "icons"))),
#     os.path.join(ROOT, "tools"),
# )

# # --------------------------------------------------------------------------
# # COLOR PALETTE  (white + blue)
# # --------------------------------------------------------------------------
# WHITE = "#ffffff"
# ICE = "#eef6ff"          # page tint
# MIST = "#f5f9ff"
# SKY_100 = "#e0f0ff"
# SKY_200 = "#bae6fd"
# SKY = "#38bdf8"          # light accent
# AZURE = "#3b82f6"        # mid accent
# BLUE = "#2563eb"         # primary accent
# BLUE_DEEP = "#1d4ed8"
# NAVY = "#0b1b3f"         # main text on light
# NAVY_SOFT = "#1e3a8a"
# SLATE = "#5b6b8c"        # muted text on light
# INDIGO = "#6366f1"       # tiny pop of violet-blue for variety
# GREEN = "#25d366"        # availability dot

# # CONTACT LINKS: replace these three placeholders with your real profile details.
# # The Gmail link automatically becomes a mailto: link.
# LINKEDIN_URL = "https://www.linkedin.com/in/YOUR-LINKEDIN-USERNAME/"
# GMAIL_ADDRESS = "YOUR-GMAIL-ADDRESS@gmail.com"
# GITHUB_URL = "https://github.com/YOUR-GITHUB-USERNAME"

# # Theme tokens. Every themed component reads colors from this dictionary.
# THEMES = {
#     "dark": dict(
#         bg="#0a1226", card="#0f1b36", card2="#142347",
#         line="rgba(147,197,253,0.16)", text="#eaf3ff", muted="#8fa6cc",
#         chip="#17284d", chiptext="#cfe2ff", tile="#13223f",
#         accent="#60a5fa", accent_text="#ffffff",
#     ),
#     "light": dict(
#         bg=ICE, card=WHITE, card2=SKY_100,
#         line="rgba(37,99,235,0.14)", text=NAVY, muted=SLATE,
#         chip="#e6f0ff", chiptext=NAVY_SOFT, tile=MIST,
#         accent=BLUE, accent_text="#ffffff",
#     ),
# }

# # --------------------------------------------------------------------------
# # FONT HANDLING
# # Load, measure, subset and embed fonts so the SVGs stay self-contained.
# # --------------------------------------------------------------------------
# def _find_font(candidates):
#     for candidate in candidates:
#         if candidate and os.path.isfile(candidate):
#             return candidate
#     return None


# _WINDOWS_FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
# _SAFE_FALLBACKS = [
#     os.path.join(_WINDOWS_FONTS, "arial.ttf"),
#     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
# ]

# FONT_SRC = {
#     "geist": _find_font([os.path.join(TOOLS, "fonts", "Geist.ttf"),
#                          os.path.join(ROOT, "fonts", "Geist.ttf")] + _SAFE_FALLBACKS),
#     "mono": _find_font([os.path.join(TOOLS, "fonts", "GeistMono.ttf"),
#                         os.path.join(ROOT, "fonts", "GeistMono.ttf"),
#                         os.path.join(_WINDOWS_FONTS, "consola.ttf"),
#                         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]),
#     "oxanium": _find_font([os.path.join(TOOLS, "fonts", "Oxanium.ttf"),
#                            os.path.join(ROOT, "fonts", "Oxanium.ttf")] + _SAFE_FALLBACKS),
# }
# for _k, _p in list(FONT_SRC.items()):
#     if _p is None:
#         FONT_SRC[_k] = _find_font(_SAFE_FALLBACKS)

# _static = {}


# def static_font(key, weight):
#     """Variable font -> cached static instance at the requested weight."""
#     k = (key, weight)
#     if k not in _static:
#         path = FONT_SRC.get(key)
#         if not path or not os.path.isfile(path):
#             raise FileNotFoundError(
#                 f"No usable font for '{key}'. Install a system font or put the "
#                 "original font files in tools/fonts."
#             )
#         f = TTFont(path)
#         # System fallbacks are static fonts and must skip the variable-font instancer.
#         _static[k] = instancer.instantiateVariableFont(f, {"wght": weight}) if "fvar" in f else f
#     return _static[k]


# def text_width(s, key, weight, size, spacing=0.0):
#     """Measure text with the real font so SVG text can be placed precisely."""
#     f = static_font(key, weight)
#     cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
#     w = 0
#     for ch in s:
#         g = cmap.get(ord(ch))
#         w += hmtx[g][0] if g else upm * 0.5
#     return w * size / upm + spacing * len(s)


# def font_face(key, weight, family, chars):
#     """Subset the font to the used characters and embed it as base64 WOFF."""
#     f = static_font(key, weight)
#     buf = io.BytesIO()
#     f.save(buf)
#     buf.seek(0)
#     sub = TTFont(buf)
#     opts = subset.Options()
#     opts.flavor = "woff"
#     opts.layout_features = ["kern", "liga"]
#     sb = subset.Subsetter(opts)
#     sb.populate(text="".join(sorted(set(chars))) + " ")
#     sb.subset(sub)
#     out = io.BytesIO()
#     sub.flavor = "woff"
#     sub.save(out)
#     b64 = base64.b64encode(out.getvalue()).decode()
#     return f"@font-face{{font-family:'{family}';src:url(data:font/woff;base64,{b64}) format('woff');}}"


# # Short labels used by Svg.text() -> (font file key, weight)
# FAMILIES = {
#     "G4": ("geist", 400), "G5": ("geist", 500), "G6": ("geist", 600), "G8": ("geist", 800),
#     "M5": ("mono", 500), "X7": ("oxanium", 700),
# }


# class Svg:
#     """Collects shapes, text, CSS and defs; embeds only the glyphs actually used."""

#     def __init__(self, w, h):
#         self.w, self.h = w, h
#         self.parts, self.defs, self.css = [], [], []
#         self.used = {}

#     def add(self, s):
#         self.parts.append(s)

#     def text(self, x, y, s, fam, size, fill, anchor="start", spacing=0, extra="", cls=""):
#         self.used.setdefault(fam, set()).update(s)
#         ls = f' letter-spacing="{spacing}"' if spacing else ""
#         c = f' class="{cls}"' if cls else ""
#         self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" '
#                  f'text-anchor="{anchor}"{ls}{c} {extra}>{escape(s)}</text>')

#     def render(self):
#         faces = "".join(font_face(*FAMILIES[f], f, chars) for f, chars in self.used.items())
#         return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
#                 f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
#                 f'<defs><style>{faces}{"".join(self.css)}</style>{"".join(self.defs)}</defs>'
#                 f'{"".join(self.parts)}</svg>')


# def save(svg, *path):
#     """Write one SVG under assets/ and return its size in bytes."""
#     p = os.path.join(OUT, *path)
#     os.makedirs(os.path.dirname(p), exist_ok=True)
#     data = svg.render() if isinstance(svg, Svg) else svg
#     with open(p, "w", encoding="utf-8") as fh:
#         fh.write(data)
#     return len(data)


# # --------------------------------------------------------------------------
# # IMAGE AND ICON HELPERS
# # --------------------------------------------------------------------------
# def img_uri(path, w, h=None, crop=None, fmt="JPEG", q=82, cover=True):
#     """Crop/resize/compress an image and return it as a base64 data URI."""
#     im = Image.open(path)
#     im = im.convert("RGBA" if fmt in ("PNG", "WEBP") else "RGB")
#     if crop:
#         im = im.crop(crop)
#     if h:
#         if cover:
#             sc = max(w / im.width, h / im.height)
#             im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
#             left, top = (im.width - w) // 2, 0
#             im = im.crop((left, top, left + w, top + h))
#         else:
#             im.thumbnail((w, h), Image.LANCZOS)
#     else:
#         im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
#     buf = io.BytesIO()
#     if fmt == "WEBP":
#         im.save(buf, fmt, quality=q, method=6)
#     else:
#         im.save(buf, fmt, quality=q, optimize=True)
#     mime = {"JPEG": "jpeg", "PNG": "png", "WEBP": "webp"}[fmt]
#     return f"data:image/{mime};base64,{base64.b64encode(buf.getvalue()).decode()}", im.size


# def icon_path(name):
#     """Read a supplied SVG icon from tools/icons, or fall back to a sparkle."""
#     icon_file = os.path.join(TOOLS, "icons", f"{name}.svg")
#     if os.path.isfile(icon_file):
#         with open(icon_file, "r", encoding="utf-8") as f:
#             match = re.search(r'<path[^>]*\bd="([^"]+)"', f.read())
#         if match:
#             return match.group(1)
#     return "M12 2.5 14.2 9.8 21.5 12 14.2 14.2 12 21.5 9.8 14.2 2.5 12 9.8 9.8Z"


# _OPENAI_PATH = (
#     "M14.949 6.547a3.94 3.94 0 0 0-.348-3.273 4.11 4.11 0 0 0-4.4-1.934 "
#     "A4.1 4.1 0 0 0 8.423.2 4.15 4.15 0 0 0 6.305.086a4.1 4.1 0 0 0-1.891.948 "
#     "4.04 4.04 0 0 0-1.158 1.753 4.1 4.1 0 0 0-1.563.679A4 4 0 0 0 .554 4.72a3.99 "
#     "3.99 0 0 0 .502 4.731 3.94 3.94 0 0 0 .346 3.274 4.11 4.11 0 0 0 4.402 "
#     "1.933c.382.425.852.764 1.377.995.526.231 1.095.35 1.67.346 1.78.002 "
#     "3.358-1.132 3.901-2.804a4.1 4.1 0 0 0 1.563-.68 4 4 0 0 0 1.14-1.253 "
#     "3.99 3.99 0 0 0-.506-4.716m-6.097 8.406a3.05 3.05 0 0 1-1.945-.694l.096-.054 "
#     "3.23-1.838a.53.53 0 0 0 .265-.455v-4.49l1.366.778q.02.011.025.035v3.722c-.003 "
#     "1.653-1.361 2.992-3.037 2.996m-6.53-2.75a2.95 2.95 0 0 1-.36-2.01l.095.057 "
#     "3.233 1.84a.53.53 0 0 0 .527 0l3.949-2.246v1.555a.05.05 0 0 1-.022.041L6.473 "
#     "13.3c-1.454.826-3.311.335-4.15-1.098m-.85-6.94A3.02 3.02 0 0 1 3.07 3.949v3.785a.51.51 "
#     "0 0 0 .262.451l3.93 2.237-1.366.779a.05.05 0 0 1-.048 0L2.585 9.342a2.98 2.98 "
#     "0 0 1-1.113-4.094zm11.216 2.571L8.747 5.576l1.362-.776a.05.05 0 0 1 .048 0l3.265 "
#     "1.86a3 3 0 0 1 1.173 1.207 2.96 2.96 0 0 1-.27 3.2 3.05 3.05 0 0 1-1.36.997V8.279a.52.52 "
#     "0 0 0-.276-.445m1.36-2.015-.097-.057-3.226-1.855a.53.53 0 0 0-.53 0L6.249 "
#     "6.153V4.598a.04.04 0 0 1 .019-.04L9.533 2.7a3.07 3.07 0 0 1 3.257.139c.474.325.843.778 "
#     "1.066 1.303.223.526.289 1.103.191 1.664zM5.503 8.575 4.139 7.8a.05.05 0 0 1-.026-.037V4.049"
#     "c0-.57.166-1.127.476-1.607.31-.48.752-.864 1.275-1.105a3.08 3.08 0 0 1 3.234.41l-.096.054"
#     "-3.23 1.838a.53.53 0 0 0-.265.455zm.742-1.577 1.758-1 1.762 1v2l-1.755 1-1.762-1z"
# )

# _GITHUB_PATH = (
#     "M12 2.5a9.6 9.6 0 0 0-3.04 18.7c.48.09.65-.2.65-.46v-1.7c-2.66.58-3.22-1.13-3.22-1.13"
#     "-.44-1.1-1.07-1.4-1.07-1.4-.87-.6.07-.59.07-.59.96.07 1.46.99 1.46.99.85 1.45 2.22 1.03 "
#     "2.76.79.08-.62.33-1.03.6-1.27-2.12-.24-4.35-1.06-4.35-4.72 0-1.04.37-1.89.98-2.56-.1-.24"
#     "-.43-1.21.09-2.52 0 0 .8-.26 2.64.98a9.2 9.2 0 0 1 4.8 0c1.84-1.24 2.64-.98 2.64-.98.52 "
#     "1.31.19 2.28.09 2.52.61.67.98 1.52.98 2.56 0 3.67-2.23 4.48-4.36 4.72.34.3.64.87.64 1.76"
#     "v2.55c0 .26.17.56.66.46A9.6 9.6 0 0 0 12 2.5Z"
# )


# def icon(name, x, y, size, fill):
#     """Return a self-contained vector icon. Key portfolio skills use custom marks."""
#     scale = size / 24
#     tf = f"translate({x} {y}) scale({scale})"
#     stroke = (f'fill="none" stroke="{fill}" stroke-linecap="round" stroke-linejoin="round"')

#     if name == "figma":  # single-colour Figma mark, follows the fill
#         return (f'<g transform="{tf}" fill="{fill}">'
#                 '<rect x="3" y="1" width="9" height="7" rx="3.5"/>'
#                 '<rect x="12" y="1" width="9" height="7" rx="3.5"/>'
#                 '<rect x="3" y="8" width="9" height="7" rx="3.5"/>'
#                 '<circle cx="16.5" cy="11.5" r="3.5"/>'
#                 '<rect x="3" y="15" width="9" height="8" rx="4"/></g>')

#     if name == "uiux":  # pen nib over an interface frame
#         return (f'<g transform="{tf}" {stroke} stroke-width="1.8">'
#                 '<rect x="2.5" y="3" width="19" height="18" rx="3.2" opacity=".65"/>'
#                 '<path d="M7 16.8 8.4 12l6.9-6.9 3.6 3.6L12 15.6 7 16.8Z"/>'
#                 '<path d="m13.9 6.5 3.6 3.6M7 16.8l3.4-.8"/></g>')

#     if name == "chatgpt":  # OpenAI mark (16x16 path)
#         return (f'<path transform="translate({x} {y}) scale({size / 16})" d="{_OPENAI_PATH}" '
#                 f'fill="{fill}" fill-rule="evenodd"/>')

#     if name == "dataanalysis":  # axes, bars and a sky-blue trend line
#         return (f'<g transform="{tf}" {stroke} stroke-width="1.8">'
#                 '<path d="M3 3.5v17h18"/>'
#                 f'<rect x="6" y="12" width="3.2" height="5.5" rx=".7" fill="{fill}" stroke="none"/>'
#                 f'<rect x="11.2" y="8.5" width="3.2" height="9" rx=".7" fill="{fill}" stroke="none"/>'
#                 f'<rect x="16.4" y="5" width="3.2" height="12.5" rx=".7" fill="{fill}" stroke="none"/>'
#                 f'<path d="m5.5 9.5 4-3 4 1 5-4" stroke="{SKY}" stroke-width="1.5"/></g>')

#     if name == "webdev":  # code brackets and slash
#         return (f'<g transform="{tf}" {stroke} stroke-width="2.1">'
#                 '<path d="m8.2 6-5.2 6 5.2 6M15.8 6l5.2 6-5.2 6M14 3.8 10 20.2"/></g>')

#     if name == "linkedin":
#         return (f'<g transform="{tf}" {stroke} stroke-width="2">'
#                 '<path d="M5 9v10M5 5.5v.2M10 19v-6.2a3 3 0 0 1 6 0V19M10 10v9"/></g>')

#     if name == "gmail":
#         return (f'<g transform="{tf}" {stroke} stroke-width="1.8">'
#                 '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/>'
#                 '<path d="m4 6 8 6 8-6"/></g>')

#     if name == "github":
#         return f'<g transform="{tf}" fill="{fill}" stroke="none"><path d="{_GITHUB_PATH}"/></g>'

#     return f'<path transform="{tf}" d="{icon_path(name)}" fill="{fill}"/>'


# GLOBE = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 6h-2.95a15.7 15.7 0 0 0-1.38-3.56A8.03 8.03 0 0 1 "
#          "18.9 8ZM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96ZM4.26 14a8.2 8.2 0 0 1 "
#          "0-4h3.38a16.5 16.5 0 0 0 0 4H4.26Zm.84 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 0 1 5.1 16Zm2.95-8"
#          "H5.1a7.99 7.99 0 0 1 4.33-3.56A15.7 15.7 0 0 0 8.05 8ZM12 19.96A14.1 14.1 0 0 1 10.09 16h3.82A14.1 14.1 0 "
#          "0 1 12 19.96ZM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4Zm.25 5.56c.6-1.11 1.06-2.31 1.38"
#          "-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56ZM16.36 14a16.5 16.5 0 0 0 0-4h3.38a8.2 8.2 0 0 1 0 4h-3.38Z")
# PEN = "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25ZM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z"


# def raw_icon(d, x, y, size, fill):
#     """Place a 24x24 icon straight from path data."""
#     return f'<path transform="translate({x} {y}) scale({size / 24})" d="{d}" fill="{fill}"/>'


# def wrap(s, key, weight, size, maxw):
#     """Split a sentence into lines that fit within maxw pixels."""
#     lines, cur = [], ""
#     for w in s.split():
#         t = (cur + " " + w).strip()
#         if text_width(t, key, weight, size) > maxw and cur:
#             lines.append(cur)
#             cur = w
#         else:
#             cur = t
#     if cur:
#         lines.append(cur)
#     return lines


# # --------------------------------------------------------------------------
# # HERO BANNER  (shared by dark and light READMEs; light, airy, blue)
# # --------------------------------------------------------------------------
# def hero():
#     W, H = 1280, 560
#     s = Svg(W, H)

#     s.defs.append(f'''
# <clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
# <linearGradient id="gBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WHITE}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
# <radialGradient id="gSky" cx="0.14" cy="0.02" r="0.78"><stop offset="0" stop-color="{SKY}" stop-opacity="0.50"/>
#  <stop offset="0.5" stop-color="{SKY_200}" stop-opacity="0.30"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
# <radialGradient id="gBlue" cx="0.88" cy="1.05" r="0.62"><stop offset="0" stop-color="{AZURE}" stop-opacity="0.42"/>
#  <stop offset="0.55" stop-color="{AZURE}" stop-opacity="0.12"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
# <radialGradient id="gHalo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{AZURE}" stop-opacity="0.38"/>
#  <stop offset="0.6" stop-color="{SKY}" stop-opacity="0.12"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></radialGradient>
# <linearGradient id="gName" x1="0" x2="1"><stop offset="0" stop-color="{BLUE_DEEP}"/><stop offset="0.55" stop-color="{AZURE}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>
# <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="{BLUE}" stroke-opacity="0.07"/></pattern>
# <linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0.72" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
# <mask id="photoMask"><rect width="{W}" height="{H}" fill="url(#fadeBottom)"/></mask>''')

#     # Entrance, float, pulse and blink animations.
#     s.css.append('''
# .up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}
# @keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
# .float{animation:float 6s ease-in-out infinite}
# @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
# .drift{animation:drift 14s ease-in-out infinite}
# @keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(14px,-10px)}}
# .pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}
# @keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}
# ''')

#     s.add('<g clip-path="url(#frame)">')
#     s.add(f'<rect width="{W}" height="{H}" fill="url(#gBg)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')
#     s.add(f'<rect width="{W}" height="{H}" fill="url(#gSky)"/><rect width="{W}" height="{H}" fill="url(#gBlue)"/>')

#     # Decorative rings + halo behind the portrait.
#     s.add(f'<g class="drift"><circle cx="1010" cy="330" r="260" fill="url(#gHalo)"/>'
#           f'<circle cx="1010" cy="330" r="210" fill="none" stroke="{AZURE}" stroke-opacity="0.18" stroke-dasharray="3 9"/>'
#           f'<circle cx="1010" cy="330" r="300" fill="none" stroke="{SKY}" stroke-opacity="0.16"/></g>')

#     # Portrait (SVG file inlined as a data URI).
#     hero_image_path = os.path.join(OUT, "Profile svg.svg")
#     if not os.path.isfile(hero_image_path):
#         candidates = [os.path.join(OUT, "Profile.svg"), os.path.join(OUT, "profile svg.svg")]
#         hero_image_path = next((p for p in candidates if os.path.isfile(p)), hero_image_path)
#     if not os.path.isfile(hero_image_path):
#         raise FileNotFoundError(
#             "Portrait SVG not found. Put 'Profile svg.svg' inside this project's assets folder: " + OUT
#         )
#     with open(hero_image_path, "r", encoding="utf-8") as f:
#         uri = "data:image/svg+xml;base64," + base64.b64encode(f.read().encode("utf-8")).decode("utf-8")
#     pw, ph = 470, 470
#     s.add(f'<image href="{uri}" x="{1240 - pw}" y="{H - ph + 40}" width="{pw}" height="{ph}" mask="url(#photoMask)"/>')

#     # Floating skill chips: frosted white pills with a blue icon.
#     chips = [
#         ("Figma", "figma", 600, 155, 0),
#         ("UI/UX", "uiux", 1100, 145, 1),
#         ("AI Agent", "chatgpt", 600, 350, 2),
#         ("Data Analysis", "dataanalysis", 1030, 405, 3),
#         ("Web Development", "webdev", 520, 465, 4),
#     ]
#     for label, ic, x, y, d in chips:
#         w = text_width(label, "geist", 600, 17) + 58
#         s.add(f'<g class="float" style="animation-delay:-{d}s">'
#               f'<rect x="{x}" y="{y + 5}" width="{w}" height="44" rx="22" fill="{BLUE}" fill-opacity="0.08"/>'
#               f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="{WHITE}" fill-opacity="0.88" '
#               f'stroke="{AZURE}" stroke-opacity="0.28"/>'
#               + icon(ic, x + 16, y + 12, 20, BLUE))
#         s.text(x + 44, y + 28, label, "G6", 17, NAVY)
#         s.add('</g>')

#     # Header: name + availability pill.
#     s.text(56, 68, "SHEHNAZ RANGREZ", "M5", 17, NAVY_SOFT, spacing=2)
#     s.add(f'<g><rect x="936" y="44" width="296" height="40" rx="20" fill="{WHITE}" fill-opacity="0.9" '
#           f'stroke="{AZURE}" stroke-opacity="0.28"/>'
#           f'<circle cx="960" cy="64" r="5" fill="{GREEN}"/><circle class="pulse" cx="960" cy="64" r="5" fill="{GREEN}"/></g>')
#     s.text(976, 69, "Available for new projects", "G5", 15, NAVY)

#     # Headline.
#     s.add('<g class="up" style="animation-delay:.1s">')
#     s.text(56, 158, "DESIGN + ENGINEERING STUDIO", "M5", 15, BLUE, spacing=3)
#     s.add('</g><g class="up" style="animation-delay:.25s">')
#     s.text(52, 262, "Meet", "G8", 104, NAVY, spacing=-3)
#     mx = 52 + text_width("Meet ", "geist", 800, 104, -3)
#     s.text(mx, 262, "Shehnaz", "G8", 104, "url(#gName)", spacing=-3)
#     s.add('</g>')

#     # Typewriter line: phrases cycle by animating clip-path widths.
#     prefix = "I design & build "
#     s.text(56, 322, prefix, "G5", 32, "#3d4f75")
#     px = 56 + text_width(prefix, "geist", 500, 32)
#     phrases = ["websites Designs ", "Graphic &  Visual Designs",
#                "full AI web & mobile apps", "Corporate Dashboards & Reports"]
#     period, slot = 16, 4
#     for i, phrase in enumerate(phrases):
#         widths = [text_width(phrase[:k], "geist", 600, 32) for k in range(len(phrase) + 1)]
#         n = len(phrase)
#         t_type, t_hold, t_del = 1.6, 3.0, 3.6  # seconds inside the 4s slot
#         vals, keys = [], []
#         for k in range(n + 1):
#             vals.append(widths[k]); keys.append(t_type * k / n)
#         vals.append(widths[n]); keys.append(t_hold)
#         for k in range(n, -1, -1):
#             vals.append(widths[k]); keys.append(t_hold + (t_del - t_hold) * (n - k) / n)
#         vals.append(0); keys.append(period)
#         kt = ";".join(f"{k / period:.4f}" for k in keys)
#         vv = ";".join(f"{v:.1f}" for v in vals)
#         s.defs.append(f'<clipPath id="tw{i}"><rect x="{px}" y="290" height="44" width="0">'
#                       f'<animate attributeName="width" values="{vv}" keyTimes="{kt}" calcMode="discrete" '
#                       f'dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect></clipPath>')
#         s.add(f'<g clip-path="url(#tw{i})">')
#         s.text(px, 322, phrase, "G6", 32, BLUE)
#         s.add('</g>')
#         cx = ";".join(f"{px + v + 3:.1f}" for v in vals)
#         s.add(f'<rect x="-20" y="296" width="3" height="34" fill="{BLUE}" opacity="0">'
#               f'<animate attributeName="x" values="{cx}" keyTimes="{kt}" calcMode="discrete" '
#               f'dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/>'
#               f'<animate attributeName="opacity" values="1;1;0;0" '
#               f'keyTimes="0;{t_del / period:.4f};{t_del / period + 0.001:.4f};1" calcMode="discrete" '
#               f'dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect>')

#     # Intro copy.
#     for j, ln in enumerate(["2+ years designing and shipping websites, AI products",
#                             "and Web platforms for startups and brands worldwide."]):
#         s.text(56, 374 + j * 30, ln, "G4", 20, SLATE)

#     # Stat cards.
#     stats = [("2+", "YEARS"), ("15+", "PROJECTS"), ("12+", "HACKATHONS PARTICIPATED"), ("40+", "TEAMS")]
#     for k, (n, lab) in enumerate(stats):
#         x = 56 + k * 168
#         s.add(f'<g class="up" style="animation-delay:{.5 + k * .12:.2f}s">')
#         s.add(f'<rect x="{x}" y="452" width="152" height="80" rx="16" fill="{BLUE}" fill-opacity="0.07"/>')
#         s.add(f'<rect x="{x}" y="446" width="152" height="80" rx="16" fill="{WHITE}" fill-opacity="0.92" '
#               f'stroke="{AZURE}" stroke-opacity="0.22"/>')
#         s.add(f'<rect x="{x + 18}" y="446" width="28" height="3" rx="1.5" fill="{BLUE}"/>')
#         s.text(x + 18, 488, n, "X7", 34, NAVY_SOFT)
#         if lab == "HACKATHONS PARTICIPATED":
#             # Two short lines stay inside the 152px card.
#             s.text(x + 18, 506, "HACKATHONS", "M5", 8.5, SLATE, spacing=1.0)
#             s.text(x + 18, 519, "PARTICIPATED", "M5", 8.5, SLATE, spacing=0.7)
#         else:
#             s.text(x + 18, 512, lab, "M5", 11, SLATE, spacing=1.5)
#         s.add('</g>')

#     s.add('</g>')
#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" '
#           f'stroke="{AZURE}" stroke-opacity="0.25"/>')
#     return s


# # --------------------------------------------------------------------------
# # THEMED PROFILE COMPONENTS
# # --------------------------------------------------------------------------
# def section(t, num, label, title, note):
#     """Numbered section heading."""
#     W, H = 1280, 116
#     s = Svg(W, H)
#     s.defs.append(f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}"/>'
#                   f'<stop offset="0.35" stop-color="{SKY}" stop-opacity="0.35"/>'
#                   f'<stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>')
#     s.text(4, 34, f"{num} / {label}", "M5", 15, t["accent"], spacing=3)
#     s.text(0, 86, title, "G8", 44, t["text"], spacing=-1)
#     s.text(W - 4, 86, note, "G4", 18, t["muted"], anchor="end")
#     s.add(f'<rect x="0" y="108" width="{W}" height="2" fill="url(#ln)"/>')
#     return s


# def card_frame(s, t, w, h, r=24):
#     """Rounded card background + hairline border."""
#     s.defs.append(f'<clipPath id="cf"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>')
#     s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["line"]}"/>')


# def chip_row(s, t, x, y, items, size=13):
#     """Row of small label chips."""
#     for it in items:
#         w = text_width(it, "mono", 500, size) + 22
#         s.add(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="14" fill="{t["chip"]}"/>')
#         s.text(x + 11, y + 19, it, "M5", size, t["chiptext"])
#         x += w + 8
#     return x


# def _placeholder_art(t, w, h, accent, label, label_font, label_size, label_y, spacing):
#     """Soft blue gradient artwork used when a cover image is missing."""
#     return (f'<g clip-path="url(#cf)">'
#             f'<rect width="{w}" height="{h}" fill="{t["card2"]}"/>'
#             f'<circle cx="{w * 0.76:.0f}" cy="{h * 0.26:.0f}" r="{h * 0.47:.0f}" fill="{accent}" fill-opacity="0.18"/>'
#             f'<circle cx="{w * 0.18:.0f}" cy="{h * 0.84:.0f}" r="{h * 0.36:.0f}" fill="{SKY}" fill-opacity="0.16"/>'
#             f'<path d="M0 {h * 0.79:.0f} C{w * 0.25:.0f} {h * 0.58:.0f} {w * 0.5:.0f} {h * 1.02:.0f} {w} {h * 0.6:.0f}" '
#             f'fill="none" stroke="{accent}" stroke-opacity="0.5" stroke-width="3"/>'
#             f'<path d="M0 {h * 0.87:.0f} C{w * 0.3:.0f} {h * 0.65:.0f} {w * 0.63:.0f} {h * 1.07:.0f} {w} {h * 0.71:.0f}" '
#             f'fill="none" stroke="{accent}" stroke-opacity="0.25" stroke-width="2"/></g>')


# def product_card(t, name, img, tagline, chips, url_label, accent):
#     """Product card: cover image, name, blurb, tags and link label."""
#     W, H = 412, 560
#     s = Svg(W, H)
#     card_frame(s, t, W, H)

#     if os.path.isfile(img):
#         uri, _ = img_uri(img, 618, 464)
#         s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="309" '
#               f'preserveAspectRatio="xMidYMid slice"/></g>')
#     else:
#         s.add(_placeholder_art(t, W, 309, accent, name, "X7", 42, 165, 2))
#         s.text(W / 2, 165, name, "X7", 42, t["muted"], anchor="middle", spacing=2)

#     s.add(f'<rect x="0" y="309" width="{W}" height="1" fill="{t["line"]}"/>')
#     s.add(f'<rect x="28" y="336" width="8" height="30" rx="4" fill="{accent}"/>')
#     s.text(48, 362, name, "X7", 32, t["text"], spacing=1)
#     for j, ln in enumerate(wrap(tagline, "geist", 400, 17, W - 56)[:3]):
#         s.text(28, 398 + j * 25, ln, "G4", 17, t["muted"])
#     chip_row(s, t, 28, 470, chips)
#     s.text(28, 532, url_label, "G6", 17, t["accent"])
#     s.add(f'<path d="M{W - 50} 520 l12 0 m0 0 l0 12 m0 -12 l-14 14" stroke="{t["accent"]}" '
#           f'stroke-width="2.4" fill="none" stroke-linecap="round"/>')
#     return s


# def service_card(t, title, desc, icons, foot):
#     """Service card: icon tiles, title, description, footer link."""
#     W, H = 412, 236
#     s = Svg(W, H)
#     card_frame(s, t, W, H, 22)
#     x = 26
#     for ic in icons:
#         s.add(f'<rect x="{x}" y="26" width="52" height="52" rx="14" fill="{t["tile"]}" stroke="{t["line"]}"/>')
#         if ic == "pen":
#             s.add(raw_icon(PEN, x + 14, 40, 24, t["accent"]))
#         elif ic == "coin":
#             s.add(f'<circle cx="{x + 26}" cy="52" r="12" fill="none" stroke="{t["accent"]}" stroke-width="2.4"/>')
#             s.text(x + 26, 58, "$", "G8", 16, t["accent"], anchor="middle")
#         else:
#             s.add(icon(ic, x + 14, 40, 24, t["accent"]))
#         x += 62
#     s.text(26, 116, title, "G6", 22, t["text"])
#     for j, ln in enumerate(wrap(desc, "geist", 400, 16, W - 52)[:2]):
#         s.text(26, 146 + j * 23, ln, "G4", 16, t["muted"])
#     s.add(f'<rect x="26" y="188" width="{W - 52}" height="1" fill="{t["line"]}"/>')
#     s.text(26, 216, foot, "M5", 13, t["accent"], spacing=1)
#     s.add(f'<path d="M{W - 42} 202 l9 0 m0 0 l0 9 m0 -9 l-11 11" stroke="{t["accent"]}" '
#           f'stroke-width="2" fill="none" stroke-linecap="round"/>')
#     return s


# def work_card(t, title, kind, img):
#     """Portfolio card: preview image, title and category."""
#     W, H = 412, 336
#     s = Svg(W, H)
#     card_frame(s, t, W, H, 22)
#     if os.path.isfile(img):
#         uri, _ = img_uri(img, 618, 400, crop=None)
#         s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="266" '
#               f'preserveAspectRatio="xMidYMin slice"/></g>')
#     else:
#         s.add(_placeholder_art(t, W, 266, t["accent"], kind, "M5", 16, 145, 2))
#         s.text(W / 2, 145, kind.upper(), "M5", 16, t["muted"], anchor="middle", spacing=2)
#     s.add(f'<rect x="0" y="266" width="{W}" height="1" fill="{t["line"]}"/>')
#     s.text(24, 306, title, "G6", 20, t["text"])
#     s.text(W - 24, 306, kind, "M5", 12, t["muted"], anchor="end", spacing=1)
#     return s


# def pill(t, label, ic):
#     """Small social/platform link badge."""
#     w = int(text_width(label, "geist", 600, 16) + 66)
#     s = Svg(w, 46)
#     s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="45" rx="23" fill="{t["card"]}" stroke="{t["line"]}"/>')
#     if ic == "globe":
#         s.add(raw_icon(GLOBE, 18, 13, 20, t["accent"]))
#     elif ic == "contra":
#         s.add(f'<circle cx="28" cy="23" r="10" fill="{t["accent"]}"/>')
#         s.text(28, 28, "C", "G8", 13, t["accent_text"], anchor="middle")
#     else:
#         s.add(icon(ic, 18, 13, 20, t["accent"]))
#     s.text(46, 29, label, "G6", 16, t["text"])
#     return s


# def now_strip(t):
#     """'Now' availability strip."""
#     W, H = 1280, 76
#     s = Svg(W, H)
#     s.css.append('.pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}'
#                  '@keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}')
#     s.defs.append(f'<linearGradient id="nb" x1="0" x2="1"><stop offset="0" stop-color="{BLUE_DEEP}"/>'
#                   f'<stop offset="1" stop-color="{AZURE}"/></linearGradient>')
#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="38" fill="{t["card"]}" stroke="{t["line"]}"/>')
#     s.add('<rect x="14" y="14" width="96" height="48" rx="24" fill="url(#nb)"/>')
#     s.text(62, 44, "NOW", "M5", 16, "#ffffff", anchor="middle", spacing=3)
#     s.add(f'<circle cx="140" cy="38" r="5" fill="{GREEN}"/><circle class="pulse" cx="140" cy="38" r="5" fill="{GREEN}"/>')
#     msg = "Shipping SYVO, a personal AI agent, in private pilot. Open for Framer, AI and Web3 projects."
#     s.text(160, 44, msg, "G5", 18, t["text"])
#     return s


# def stack(t):
#     """Scrolling technology-stack strip."""
#     W, H = 1280, 150
#     names = [("figma", "Figma"), ("framer", "Framer"), ("react", "React"), ("nextdotjs", "Next.js"),
#              ("typescript", "TypeScript"), ("tailwindcss", "Tailwind"), ("flutter", "Flutter"),
#              ("nodedotjs", "Node.js"), ("python", "Python"), ("supabase", "Supabase"), ("firebase", "Firebase"),
#              ("openai", "OpenAI"), ("claude", "Claude"), ("n8n", "n8n"), ("solidity", "Solidity"),
#              ("ethereum", "Ethereum"), ("solana", "Solana"), ("wordpress", "WordPress"), ("shopify", "Shopify")]
#     step = 132
#     span = step * len(names)
#     s = Svg(W, H)
#     s.defs.append(f'<clipPath id="sc"><rect width="{W}" height="{H}" rx="24"/></clipPath>'
#                   f'<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{t["card"]}"/>'
#                   f'<stop offset="0.07" stop-color="{t["card"]}" stop-opacity="0"/>'
#                   f'<stop offset="0.93" stop-color="{t["card"]}" stop-opacity="0"/>'
#                   f'<stop offset="1" stop-color="{t["card"]}"/></linearGradient>')
#     s.css.append(f'.mq{{animation:mq 38s linear infinite}}'
#                  f'@keyframes mq{{from{{transform:translateX(0)}}to{{transform:translateX(-{span}px)}}}}')
#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="{t["card"]}" stroke="{t["line"]}"/>')
#     s.add('<g clip-path="url(#sc)"><g class="mq">')
#     for rep in range(2):
#         for k, (ic, lab) in enumerate(names):
#             x = 30 + rep * span + k * step
#             s.add(f'<rect x="{x}" y="26" width="64" height="64" rx="18" fill="{t["tile"]}" stroke="{t["line"]}"/>')
#             s.add(icon(ic, x + 18, 44, 28, t["text"]))
#             s.text(x + 32, 120, lab, "M5", 13, t["muted"], anchor="middle")
#     s.add('</g></g>')
#     s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#edge)"/>')
#     return s


# # --------------------------------------------------------------------------
# # CALL-TO-ACTION BANNER  (shared; saturated blue gradient with white type)
# # --------------------------------------------------------------------------
# def cta():
#     W, H = 1280, 300
#     s = Svg(W, H)
#     s.defs.append(f'''<clipPath id="cc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
# <linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY_SOFT}"/>
#  <stop offset="0.55" stop-color="{BLUE}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>
# <radialGradient id="ca" cx="0.12" cy="0" r="0.7"><stop offset="0" stop-color="#ffffff" stop-opacity="0.34"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
# <radialGradient id="cb" cx="0.92" cy="1.05" r="0.6"><stop offset="0" stop-color="{SKY_200}" stop-opacity="0.55"/><stop offset="1" stop-color="{SKY_200}" stop-opacity="0"/></radialGradient>
# <pattern id="cg" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#fff" stroke-opacity="0.09"/></pattern>
# <linearGradient id="cn" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{SKY_200}"/></linearGradient>''')

#     s.add(f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="url(#cbg)"/>'
#           f'<rect width="{W}" height="{H}" fill="url(#cg)"/><rect width="{W}" height="{H}" fill="url(#ca)"/>'
#           f'<rect width="{W}" height="{H}" fill="url(#cb)"/>'
#           f'<circle cx="1120" cy="60" r="150" fill="none" stroke="#fff" stroke-opacity="0.14" stroke-dasharray="3 9"/>'
#           f'<circle cx="1120" cy="60" r="210" fill="none" stroke="#fff" stroke-opacity="0.10"/></g>')

#     s.text(64, 92, "HAVE A PROJECT IN MIND?", "M5", 16, SKY_200, spacing=3)
#     s.text(60, 168, "Let's build it", "G8", 72, WHITE, spacing=-2)
#     s.text(60 + text_width("Let's build it ", "geist", 800, 72, -2), 168, "together.", "G8", 72,
#            "url(#cn)", spacing=-2)
#     s.text(64, 222, "Web design  \u2022  UI/UX  \u2022  AI agents  \u2022  Data analysis  \u2022  Web development",
#            "G4", 18, "#dbeafe")
#     s.text(1216, 92, "SHEHNAZ RANGREZ", "M5", 15, "#dbeafe", anchor="end")

#     contacts = [
#         ("LinkedIn", "linkedin", LINKEDIN_URL, 770),
#         ("Gmail", "gmail", f"mailto:{GMAIL_ADDRESS}", 925),
#         ("GitHub", "github", GITHUB_URL, 1080),
#     ]
#     for label, ic, href, x in contacts:
#         # Anchors work when cta.svg is opened directly; see social-links.md for
#         # clickable Markdown wrappers when the SVG is embedded in a GitHub README.
#         s.add(f'<a href="{escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">')
#         s.add(f'<rect x="{x}" y="194" width="140" height="58" rx="29" fill="#ffffff" fill-opacity="0.16" '
#               f'stroke="#ffffff" stroke-opacity="0.55"/>')
#         s.add(icon(ic, x + 17, 212, 22, WHITE))
#         s.text(x + 49, 230, label, "G6", 17, WHITE)
#         s.add('</a>')

#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" '
#           f'stroke="#fff" stroke-opacity="0.25"/>')
#     return s


# def social_badge(label, icon_name):
#     """Individual contact badge (white with blue accents); Markdown wraps it in a real link."""
#     w, h = 160, 48
#     b = Svg(w, h)
#     b.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="24" fill="{WHITE}" '
#           f'stroke="{AZURE}" stroke-opacity="0.35"/>')
#     b.add(icon(icon_name, 15, 13, 22, BLUE))
#     b.text(48, 30, label, "G6", 15, NAVY)
#     return b


# def write_social_markdown():
#     """Write README-ready links using paths relative to the detected README."""
#     readme_candidates = [os.path.join(ROOT, "README.md"), os.path.join(PARENT_DIR, "README.md")]
#     readme_path = next((p for p in readme_candidates if os.path.isfile(p)), None)
#     readme_dir = os.path.dirname(readme_path) if readme_path else ROOT
#     asset_prefix = os.path.relpath(OUT, readme_dir).replace(os.sep, "/").rstrip("/")
#     if asset_prefix == ".":
#         asset_prefix = "assets"

#     rows = [
#         f'[![LinkedIn]({asset_prefix}/social/linkedin.svg)]({LINKEDIN_URL})',
#         f'[![Gmail]({asset_prefix}/social/gmail.svg)](mailto:{GMAIL_ADDRESS})',
#         f'[![GitHub]({asset_prefix}/social/github.svg)]({GITHUB_URL})',
#     ]
#     path = os.path.join(OUT, "social-links.md")
#     with open(path, "w", encoding="utf-8") as f:
#         f.write("\n".join(rows) + "\n")
#     return path


# # --------------------------------------------------------------------------
# # PROFILE CONTENT DATA: edit these lists to change what appears in the README
# # --------------------------------------------------------------------------
# LK = f"{DOCS}/launch-kit"
# BH = f"{CP}/behance"

# # (slug, display name, image path, description, tags, link text, accent colour)
# PRODUCTS = [
#     ("xoxi", "XOXI", f"{CP}/products/xoxi-cover.jpg",
#      "Your CV becomes a verified portfolio you can apply with. AI match scores for the teams hiring.",
#      ["Web", "iOS", "Android", "AI"], "Visit xoxi.me", BLUE),
#     ("syvo", "SYVO", f"{CP}/products/syvo-cover.jpg",
#      "A personal AI agent. Ask in plain words and it finds, books or sells for you, then waits for your OK.",
#      ["AI agent", "Flutter", "Web"], "Visit syvo.si", "#0ea5e9"),
#     ("lovii", "LOVII", f"{CP}/products/lovii-cover.jpg",
#      "A private journal for couples. One short note a day, drawn by AI as an illustrated card.",
#      ["iOS", "Android", "AI art"], "Visit lovii.app", INDIGO),
# ]

# # (slug, title, description, icon names)
# SERVICES = [
#     ("framer", "Framer websites", "Responsive sites with real scroll motion, CMS and SEO, from Figma or from scratch.", ["framer"]),
#     ("agents", "AI agents & automations", "Chatbots, n8n and Make workflows and custom agents that do real work.", ["n8n", "openai"]),
#     ("aiapps", "Full AI web & mobile apps", "Website, web app and iOS + Android apps, designed and built end to end.", ["flutter", "react"]),
#     ("uiux", "UI/UX design", "Websites, dashboards and mobile apps in Figma with clickable prototypes.", ["figma"]),
#     ("wpshop", "WordPress & Shopify", "Business sites and online stores that are easy to run after launch.", ["wordpress", "shopify"]),
#     ("nftweb", "NFT & Web3 websites", "Marketplaces, mint pages and landing pages that make wallets feel simple.", ["ethereum"]),
#     ("dapp", "Smart contracts & dApps", "NFT minting dApps and contracts on Ethereum, Polygon and Solana.", ["solidity", "solana"]),
#     ("memecoin", "Meme coin websites", "Loud, fun coin sites with tokenomics, presale pages and buy flows.", ["coin", "solana"]),
#     ("brand", "Logo & brand identity", "Minimal logos and brand kits for startups, products and Web3 projects.", ["pen"]),
# ]

# # (slug, project name, category label)
# WORK = [
#     ("medelz", "Medelz", "MUSIC PLATFORM"), ("smartforum", "Smart Forum", "IT SERVICES"),
#     ("satholler", "SatHoller", "NFT AUCTIONS"), ("metaadsfirm", "MetaAdsFirm", "WEB3 AGENCY"),
#     ("blackmomento", "The Black Momento", "E-COMMERCE"), ("blckbuster", "Blckbuster", "WEB3 MARKETPLACE"),
# ]

# # (slug, visible label, icon filename)
# PILLS = [("site", "Website", "globe"), ("framer", "Framer", "framer"), ("contra", "Contra", "contra"),
#          ("fiverr", "Fiverr", "fiverr"), ("x", "X", "x"), ("youtube", "YouTube", "youtube"),
#          ("instagram", "Instagram", "instagram"), ("linkedin", "LinkedIn", "linkedin")]

# SECTIONS = [
#     ("01", "PRODUCTS", "Products I've built", "Designed, built and shipped in-house"),
#     ("02", "SERVICES", "What I can do for you", "Every card opens the matching gig"),
#     ("03", "SELECTED WORK", "Selected client work", "Full case studies on Behance"),
#     ("04", "STACK", "Tools I ship with", "Design, code, AI and Web3"),
#     ("05", "ACTIVITY", "Building in public", "Updated daily by GitHub Actions"),
# ]


# def main():
#     """Generate every shared and theme-specific SVG, then print a size summary."""
#     sizes = {}
#     sizes["hero.svg"] = save(hero(), "hero.svg")
#     sizes["cta.svg"] = save(cta(), "cta.svg")

#     for slug, label, icon_name in [("linkedin", "LinkedIn", "linkedin"),
#                                    ("gmail", "Gmail", "gmail"),
#                                    ("github", "GitHub", "github")]:
#         sizes[f"social/{slug}"] = save(social_badge(label, icon_name), "social", f"{slug}.svg")
#     write_social_markdown()

#     for name, t in THEMES.items():
#         sizes[f"{name}/now"] = save(now_strip(t), name, "now.svg")
#         for key, label, title, note in SECTIONS:
#             sizes[f"{name}/s{key}"] = save(section(t, key, label, title, note), name, f"s{key}.svg")
#         for slug, nm, img, tag, chips, url, acc in PRODUCTS:
#             sizes[f"{name}/p-{slug}"] = save(product_card(t, nm, img, tag, chips, url, acc), name, f"p-{slug}.svg")
#         for slug, title, desc, icons in SERVICES:
#             sizes[f"{name}/sv-{slug}"] = save(service_card(t, title, desc, icons, "VIEW ON FIVERR"), name, f"sv-{slug}.svg")
#         for slug, title, kind in WORK:
#             sizes[f"{name}/w-{slug}"] = save(work_card(t, title, kind, f"{BH}/{slug}/01.png"), name, f"w-{slug}.svg")
#         for slug, label, ic in PILLS:
#             sizes[f"{name}/l-{slug}"] = save(pill(t, label, ic), name, f"l-{slug}.svg")
#         sizes[f"{name}/stack"] = save(stack(t), name, "stack.svg")

#     total = sum(sizes.values())
#     big = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
#     print(f"{len(sizes)} files, {total / 1e6:.2f} MB total; largest: "
#           + ", ".join(f"{k} {v // 1024}KB" for k, v in big))


# if __name__ == "__main__":
#     main()

#-----------------------------------------------------------------------------------------------------
# (
# """Builds every graphic in the Shehnaz-R GitHub profile README.







# Each SVG is self-contained: fonts are subset and embedded, images are inlined,



# so nothing breaks when GitHub proxies the file. Run: python build_annotated.py



# Outputs go to assets/dark and assets/light (the hero and CTA are shared).



# """



# import base64



# import io



# import os



# import re



# from html import escape







# from fontTools import subset



# from fontTools.ttLib import TTFont



# from fontTools.varLib import instancer



# from PIL import Image



# import logging



# logging.getLogger('fontTools').setLevel(logging.ERROR)







# # Resolve the project folder from this script's actual location.
# # Supported layouts:
# #   New/build_annotated.py + New/assets/Profile svg.svg
# #   project/tools/build_annotated.py + project/assets/Profile svg.svg
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# if os.path.basename(SCRIPT_DIR).lower() == "tools":
#     ROOT = PARENT_DIR
# elif os.path.isdir(os.path.join(SCRIPT_DIR, "assets")):
#     ROOT = SCRIPT_DIR
# elif os.path.isdir(os.path.join(PARENT_DIR, "assets")):
#     ROOT = PARENT_DIR
# else:
#     ROOT = SCRIPT_DIR

# OUT = os.path.join(ROOT, "assets")
# DOCS = ROOT
# CP = ROOT

# # Reuse the old project's tools folder if it exists; otherwise this script
# # runs from the New folder without requiring a separate tools directory.
# _TOOL_CANDIDATES = [
#     os.path.join(ROOT, "tools"),
#     SCRIPT_DIR,
#     os.path.join(PARENT_DIR, "tools"),
#     os.path.join(PARENT_DIR, "Tools"),
# ]
# TOOLS = next(
#     (candidate for candidate in _TOOL_CANDIDATES
#      if os.path.isdir(os.path.join(candidate, "fonts"))
#      or os.path.isdir(os.path.join(candidate, "icons"))),
#     os.path.join(ROOT, "tools"),
# )







# # COLOR PALETTE

# # Centralized brand colors used by the SVG backgrounds, text, accents, and icons.



# ORANGE = "#ff6a00"



# INK = "#0b0c10"



# CREAM = "#f7f0dc"



# INDIGO = "#2a1b72"



# INDIGO_DEEP = "#1e1670"



# PINK = "#f472b6"



# VIOLET = "#a855f7"



# CYAN = "#22d3ee"

# # CONTACT LINKS — replace these three placeholders with your real profile details.
# # The Gmail link automatically becomes a mailto: link.
# LINKEDIN_URL = "https://www.linkedin.com/in/YOUR-LINKEDIN-USERNAME/"
# GMAIL_ADDRESS = "YOUR-GMAIL-ADDRESS@gmail.com"
# GITHUB_URL = "https://github.com/YOUR-GITHUB-USERNAME"







# # Theme-specific color tokens. Every themed component reads colors from this dictionary.

# THEMES = {



#     "dark": dict(bg="#0e0f14", card="#13141b", card2="#181a23", line="rgba(255,255,255,0.09)",



#                  text="#f7f0dc", muted="#9aa0ad", chip="#1d1f2a", chiptext="#d9dbe2", tile="#1b1d27"),



#     "light": dict(bg="#fbf8f1", card="#ffffff", card2="#f6f1e4", line="rgba(11,12,16,0.10)",



#                   text="#0b0c10", muted="#5d6270", chip="#f2ecdd", chiptext="#2a2d36", tile="#f4efe3"),



# }







# # FONT HANDLING

# # These helpers load, measure, subset, and embed fonts so the SVGs remain self-contained.







# # Local font files expected under tools/fonts.

# def _find_font(candidates):
#     for candidate in candidates:
#         if candidate and os.path.isfile(candidate):
#             return candidate
#     return None


# _WINDOWS_FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")

# FONT_SRC = {
#     "geist": _find_font([
#         os.path.join(TOOLS, "fonts", "Geist.ttf"),
#         os.path.join(ROOT, "fonts", "Geist.ttf"),
#         os.path.join(_WINDOWS_FONTS, "arial.ttf"),
#         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
#     ]),
#     "mono": _find_font([
#         os.path.join(TOOLS, "fonts", "GeistMono.ttf"),
#         os.path.join(ROOT, "fonts", "GeistMono.ttf"),
#         os.path.join(_WINDOWS_FONTS, "consola.ttf"),
#         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
#     ]),
#     "oxanium": _find_font([
#         os.path.join(TOOLS, "fonts", "Oxanium.ttf"),
#         os.path.join(ROOT, "fonts", "Oxanium.ttf"),
#         os.path.join(_WINDOWS_FONTS, "arial.ttf"),
#         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
#     ]),
# }

# # Use a safe installed font when the original bundled fonts are not present.
# for _font_key, _font_path in list(FONT_SRC.items()):
#     if _font_path is None:
#         fallback = _find_font([
#             os.path.join(_WINDOWS_FONTS, "arial.ttf"),
#             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
#         ])
#         FONT_SRC[_font_key] = fallback



# _static = {}











# # Load a variable font and create a cached static version at the requested weight.

# def static_font(key, weight):



#     k = (key, weight)



#     if k not in _static:



#         font_path = FONT_SRC.get(key)
#         if not font_path or not os.path.isfile(font_path):
#             raise FileNotFoundError(
#                 f"No usable font was found for '{key}'. Install a system font "
#                 "or place the original font files in tools/fonts."
#             )
#         f = TTFont(font_path)
#         # Bundled Geist/Oxanium files are variable fonts; system fallbacks may
#         # be static fonts and therefore must not be passed to the variable-font instancer.
#         _static[k] = (
#             instancer.instantiateVariableFont(f, {"wght": weight})
#             if "fvar" in f else f
#         )



#     return _static[k]











# # Measure text using the selected font so SVG text can be positioned accurately.

# def text_width(s, key, weight, size, spacing=0.0):



#     f = static_font(key, weight)



#     cmap = f.getBestCmap()



#     hmtx = f["hmtx"]



#     upm = f["head"].unitsPerEm



#     w = 0



#     for ch in s:



#         g = cmap.get(ord(ch))



#         w += hmtx[g][0] if g else upm * 0.5



#     return w * size / upm + spacing * len(s)











# # Subset the font to only the characters used, then embed it as a base64 WOFF font in the SVG.

# def font_face(key, weight, family, chars):



#     f = static_font(key, weight)



#     buf = io.BytesIO()



#     f.save(buf)



#     buf.seek(0)



#     sub = TTFont(buf)



#     opts = subset.Options()



#     opts.flavor = "woff"



#     opts.layout_features = ["kern", "liga"]



#     s = subset.Subsetter(opts)



#     s.populate(text="".join(sorted(set(chars))) + " ")



#     s.subset(sub)



#     out = io.BytesIO()



#     sub.flavor = "woff"



#     sub.save(out)



#     b64 = base64.b64encode(out.getvalue()).decode()



#     return f"@font-face{{font-family:'{family}';src:url(data:font/woff;base64,{b64}) format('woff');}}"











# # FONT FAMILY ALIASES

# # Short labels used by Svg.text() to select a font file and weight.



# FAMILIES = {



#     "G4": ("geist", 400), "G5": ("geist", 500), "G6": ("geist", 600), "G8": ("geist", 800),



#     "M5": ("mono", 500), "X7": ("oxanium", 700),



# }











# # SVG builder: collects shapes, text, styles, definitions, and used glyphs before rendering.

# class Svg:



#     """Collects text per font family so only the used glyphs get embedded."""







#     def __init__(self, w, h):



#         self.w, self.h = w, h



#         self.parts = []



#         self.defs = []



#         self.css = []



#         self.used = {}







#     def add(self, s):



#         self.parts.append(s)







#     def text(self, x, y, s, fam, size, fill, anchor="start", spacing=0, extra="", cls=""):



#         self.used.setdefault(fam, set()).update(s)



#         ls = f' letter-spacing="{spacing}"' if spacing else ""



#         c = f' class="{cls}"' if cls else ""



#         self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" '



#                  f'text-anchor="{anchor}"{ls}{c} {extra}>{escape(s)}</text>')







#     def render(self):



#         faces = "".join(font_face(*FAMILIES[f], f, chars) for f, chars in self.used.items())



#         return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '



#                 f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'



#                 f'<defs><style>{faces}{"".join(self.css)}</style>{"".join(self.defs)}</defs>'



#                 f'{"".join(self.parts)}</svg>')











# # Write one generated SVG file into the requested output folder and return its byte count.

# def save(svg, *path):



#     p = os.path.join(OUT, *path)



#     os.makedirs(os.path.dirname(p), exist_ok=True)



#     data = svg.render() if isinstance(svg, Svg) else svg



#     with open(p, "w", encoding="utf-8") as fh:



#         fh.write(data)



#     return len(data)











# # IMAGE AND ICON HELPERS

# # Functions for embedding raster images and reusable SVG icon paths.







# # Open, crop/resize, compress, and base64-encode an image for embedding directly inside an SVG.

# def img_uri(path, w, h=None, crop=None, fmt="JPEG", q=82, cover=True):



#     im = Image.open(path)



#     im = im.convert("RGBA" if fmt in ("PNG", "WEBP") else "RGB")



#     if crop:



#         im = im.crop(crop)



#     if h:



#         if cover:



#             sc = max(w / im.width, h / im.height)



#             im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)



#             l, t = (im.width - w) // 2, 0



#             im = im.crop((l, t, l + w, t + h))



#         else:



#             im.thumbnail((w, h), Image.LANCZOS)



#     else:



#         im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)



#     buf = io.BytesIO()



#     im.save(buf, fmt, quality=q, method=6) if fmt == "WEBP" else im.save(buf, fmt, quality=q, optimize=True)



#     mime = {"JPEG": "jpeg", "PNG": "png", "WEBP": "webp"}[fmt]



#     return f"data:image/{mime};base64,{base64.b64encode(buf.getvalue()).decode()}", im.size











# # Read an icon SVG from tools/icons and extract its path data.

# def icon_path(name):
#     """Read a supplied SVG icon, or return a simple built-in fallback path."""
#     icon_file = os.path.join(TOOLS, "icons", f"{name}.svg")
#     if os.path.isfile(icon_file):
#         with open(icon_file, "r", encoding="utf-8") as f:
#             src = f.read()
#         match = re.search(r'<path[^>]*\bd="([^"]+)"', src)
#         if match:
#             return match.group(1)

#     # Small neutral sparkle icon; keeps the graphic build working when the
#     # optional icon collection is not included in the New folder.
#     return "M12 2.5 14.2 9.8 21.5 12 14.2 14.2 12 21.5 9.8 14.2 2.5 12 9.8 9.8Z"











# # Place a reusable 24x24 icon path at a chosen position and size.

# def icon(name, x, y, size, fill):
#     """Return a self-contained vector icon; key portfolio skills use custom marks."""
#     scale = size / 24
#     transform = f'translate({x} {y}) scale({scale})'

#     # Figma mark drawn in a single white colour to match the monochrome chips.
#     if name == "figma":
#         return (
#             f'<g transform="{transform}" fill="#ffffff">'
#             '<rect x="3" y="1" width="9" height="7" rx="3.5"/>'
#             '<rect x="12" y="1" width="9" height="7" rx="3.5"/>'
#             '<rect x="3" y="8" width="9" height="7" rx="3.5"/>'
#             '<circle cx="16.5" cy="11.5" r="3.5"/>'
#             '<rect x="3" y="15" width="9" height="8" rx="4"/>'
#             '</g>'
#         )

#     # UI/UX: pen nib over a simple interface frame.
#     if name == "uiux":
#         return (
#             f'<g transform="{transform}" fill="none" stroke="{fill}" '
#             'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
#             '<rect x="2.5" y="3" width="19" height="18" rx="3.2" opacity=".65"/>'
#             '<path d="M7 16.8 8.4 12l6.9-6.9 3.6 3.6L12 15.6 7 16.8Z"/>'
#             '<path d="m13.9 6.5 3.6 3.6M7 16.8l3.4-.8"/>'
#             '</g>'
#         )

#     # AI Agent: OpenAI/ChatGPT mark (16x16 vector path, scaled to the icon size).
#     if name == "chatgpt":
#         openai_path = (
#             "M14.949 6.547a3.94 3.94 0 0 0-.348-3.273 4.11 4.11 0 0 0-4.4-1.934 "
#             "A4.1 4.1 0 0 0 8.423.2 4.15 4.15 0 0 0 6.305.086a4.1 4.1 0 0 0-1.891.948 "
#             "4.04 4.04 0 0 0-1.158 1.753 4.1 4.1 0 0 0-1.563.679A4 4 0 0 0 .554 4.72a3.99 "
#             "3.99 0 0 0 .502 4.731 3.94 3.94 0 0 0 .346 3.274 4.11 4.11 0 0 0 4.402 "
#             "1.933c.382.425.852.764 1.377.995.526.231 1.095.35 1.67.346 1.78.002 "
#             "3.358-1.132 3.901-2.804a4.1 4.1 0 0 0 1.563-.68 4 4 0 0 0 1.14-1.253 "
#             "3.99 3.99 0 0 0-.506-4.716m-6.097 8.406a3.05 3.05 0 0 1-1.945-.694l.096-.054 "
#             "3.23-1.838a.53.53 0 0 0 .265-.455v-4.49l1.366.778q.02.011.025.035v3.722c-.003 "
#             "1.653-1.361 2.992-3.037 2.996m-6.53-2.75a2.95 2.95 0 0 1-.36-2.01l.095.057 "
#             "3.233 1.84a.53.53 0 0 0 .527 0l3.949-2.246v1.555a.05.05 0 0 1-.022.041L6.473 "
#             "13.3c-1.454.826-3.311.335-4.15-1.098m-.85-6.94A3.02 3.02 0 0 1 3.07 3.949v3.785a.51.51 "
#             "0 0 0 .262.451l3.93 2.237-1.366.779a.05.05 0 0 1-.048 0L2.585 9.342a2.98 2.98 "
#             "0 0 1-1.113-4.094zm11.216 2.571L8.747 5.576l1.362-.776a.05.05 0 0 1 .048 0l3.265 "
#             "1.86a3 3 0 0 1 1.173 1.207 2.96 2.96 0 0 1-.27 3.2 3.05 3.05 0 0 1-1.36.997V8.279a.52.52 "
#             "0 0 0-.276-.445m1.36-2.015-.097-.057-3.226-1.855a.53.53 0 0 0-.53 0L6.249 "
#             "6.153V4.598a.04.04 0 0 1 .019-.04L9.533 2.7a3.07 3.07 0 0 1 3.257.139c.474.325.843.778 "
#             "1.066 1.303.223.526.289 1.103.191 1.664zM5.503 8.575 4.139 7.8a.05.05 0 0 1-.026-.037V4.049c0-.57.166-1.127.476-1.607.31-.48.752-.864 1.275-1.105a3.08 3.08 0 0 1 3.234.41l-.096.054-3.23 1.838a.53.53 0 0 0-.265.455zm.742-1.577 1.758-1 1.762 1v2l-1.755 1-1.762-1z"
#         )
#         return f'<path transform="translate({x} {y}) scale({size / 16})" d="{openai_path}" fill="{fill}" fill-rule="evenodd"/>'

#     # Data analysis: axes, three bars, and a rising trend line.
#     if name == "dataanalysis":
#         return (
#             f'<g transform="{transform}" fill="none" stroke="{fill}" '
#             'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
#             '<path d="M3 3.5v17h18"/>'
#             '<rect x="6" y="12" width="3.2" height="5.5" rx=".7" fill="{fill}" stroke="none"/>'
#             '<rect x="11.2" y="8.5" width="3.2" height="9" rx=".7" fill="{fill}" stroke="none"/>'
#             '<rect x="16.4" y="5" width="3.2" height="12.5" rx=".7" fill="{fill}" stroke="none"/>'
#             '<path d="m5.5 9.5 4-3 4 1 5-4" stroke="#ffad6b" stroke-width="1.5"/>'
#             '</g>'
#         ).replace('fill="{fill}"', f'fill="{fill}"')

#     # Web development: recognizable code brackets and slash.
#     if name == "webdev":
#         return (
#             f'<g transform="{transform}" fill="none" stroke="{fill}" '
#             'stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">'
#             '<path d="m8.2 6-5.2 6 5.2 6M15.8 6l5.2 6-5.2 6M14 3.8 10 20.2"/>'
#             '</g>'
#         )

#     # LinkedIn, Gmail and GitHub marks used in the CTA contact links.
#     if name == "linkedin":
#         return (
#             f'<g transform="{transform}" fill="none" stroke="{fill}" '
#             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
#             '<path d="M5 9v10M5 5.5v.2M10 19v-6.2a3 3 0 0 1 6 0V19M10 10v9"/>'
#             '</g>'
#         )
#     if name == "gmail":
#         return (
#             f'<g transform="{transform}" fill="none" stroke="{fill}" '
#             'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
#             '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/>'
#             '<path d="m4 6 8 6 8-6"/>'
#             '</g>'
#         )
#     if name == "github":
#         return (
#             f'<g transform="{transform}" fill="{fill}" stroke="none">'
#             '<path d="M12 2.5a9.6 9.6 0 0 0-3.04 18.7c.48.09.65-.2.65-.46v-1.7c-2.66.58-3.22-1.13-3.22-1.13-.44-1.1-1.07-1.4-1.07-1.4-.87-.6.07-.59.07-.59.96.07 1.46.99 1.46.99.85 1.45 2.22 1.03 2.76.79.08-.62.33-1.03.6-1.27-2.12-.24-4.35-1.06-4.35-4.72 0-1.04.37-1.89.98-2.56-.1-.24-.43-1.21.09-2.52 0 0 .8-.26 2.64.98a9.2 9.2 0 0 1 4.8 0c1.84-1.24 2.64-.98 2.64-.98.52 1.31.19 2.28.09 2.52.61.67.98 1.52.98 2.56 0 3.67-2.23 4.48-4.36 4.72.34.3.64.87.64 1.76v2.55c0 .26.17.56.66.46A9.6 9.6 0 0 0 12 2.5Z"/>'
#             '</g>'
#         )

#     return f'<path transform="{transform}" d="{icon_path(name)}" fill="{fill}"/>'










# GLOBE = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 6h-2.95a15.7 15.7 0 0 0-1.38-3.56A8.03 8.03 0 0 1 "



#          "18.9 8ZM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96ZM4.26 14a8.2 8.2 0 0 1 "



#          "0-4h3.38a16.5 16.5 0 0 0 0 4H4.26Zm.84 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 0 1 5.1 16Zm2.95-8"



#          "H5.1a7.99 7.99 0 0 1 4.33-3.56A15.7 15.7 0 0 0 8.05 8ZM12 19.96A14.1 14.1 0 0 1 10.09 16h3.82A14.1 14.1 0 "



#          "0 1 12 19.96ZM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4Zm.25 5.56c.6-1.11 1.06-2.31 1.38"



#          "-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56ZM16.36 14a16.5 16.5 0 0 0 0-4h3.38a8.2 8.2 0 0 1 0 4h-3.38Z")



# PEN = "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25ZM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z"











# # Build an icon path directly from supplied SVG path data (without reading an icon file).

# def raw_icon(d, x, y, size, fill):



#     return f'<path transform="translate({x} {y}) scale({size / 24})" d="{d}" fill="{fill}"/>'











# # Split a sentence into lines that fit within a maximum pixel width.

# def wrap(s, key, weight, size, maxw):



#     words, lines, cur = s.split(), [], ""



#     for w in words:



#         t = (cur + " " + w).strip()



#         if text_width(t, key, weight, size) > maxw and cur:



#             lines.append(cur)



#             cur = w



#         else:



#             cur = t



#     if cur:



#         lines.append(cur)



#     return lines











# # HERO BANNER (SHARED BY DARK AND LIGHT THEMES)

# # This is the large animated top section of the profile.







# # Build the shared animated profile banner (hero.svg), including background, portrait, chips, and intro text.

# def hero():



#     W, H = 1280, 560



#     s = Svg(W, H)



#     # SVG definitions: clipping, layered gradients, grid texture, and portrait fade mask.

#     s.defs.append(f'''



# <clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>



# <radialGradient id="gIndigo" cx="0.22" cy="0.05" r="0.75"><stop offset="0" stop-color="#3b22b8" stop-opacity="0.95"/>



#  <stop offset="0.45" stop-color="{INDIGO_DEEP}" stop-opacity="0.55"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>



# <radialGradient id="gOrange" cx="0.62" cy="1.05" r="0.55"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.75"/>



#  <stop offset="0.5" stop-color="#b8430a" stop-opacity="0.25"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>



# <radialGradient id="gHalo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.55"/>



#  <stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>



# <linearGradient id="gName" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="0.55" stop-color="{PINK}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>



# <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#ffffff" stroke-opacity="0.045"/></pattern>



# <linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0.72" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>



# <mask id="photoMask"><rect width="{W}" height="{H}" fill="url(#fadeBottom)"/></mask>''')



#     # CSS keyframes power the entrance, floating chips, pulsing status dot, and blinking cursor.

#     s.css.append('''



# .up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}



# @keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}



# .float{animation:float 6s ease-in-out infinite}



# @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}



# .pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}



# @keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}



# .blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}



# ''')



#     s.add('<g clip-path="url(#frame)">')



#     s.add(f'<rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')



#     s.add(f'<rect width="{W}" height="{H}" fill="url(#gIndigo)"/><rect width="{W}" height="{H}" fill="url(#gOrange)"/>')



#     # Portrait layer: add a soft halo, then embed the prepared Shehnaz WEBP image.



#     s.add(f'<circle cx="1010" cy="330" r="260" fill="url(#gHalo)"/>')



#     # uri, (pw, ph) = img_uri(f"{CP}/assets/Shehnaz-hero.webp", 470, fmt="WEBP", q=80)

#     hero_image_path = os.path.join(OUT, "Profile svg.svg")
#     if not os.path.isfile(hero_image_path):
#         # Windows is case-insensitive, but allow common filename variations too.
#         candidates = [
#             os.path.join(OUT, "Profile.svg"),
#             os.path.join(OUT, "profile svg.svg"),
#         ]
#         hero_image_path = next((p for p in candidates if os.path.isfile(p)), hero_image_path)
#     if not os.path.isfile(hero_image_path):
#         raise FileNotFoundError(
#             "Portrait SVG not found. Put 'Profile svg.svg' inside this project's assets folder: "
#             + OUT
#         )

#     with open(hero_image_path, "r", encoding="utf-8") as f:
#         svg_content = f.read()

#     uri = "data:image/svg+xml;base64," + base64.b64encode(
#         svg_content.encode("utf-8")
#     ).decode("utf-8")

#     pw, ph = 470, 470



#     s.add(f'<image href="{uri}" x="{1240 - pw}" y="{H - ph + 40}" width="{pw}" height="{ph}" mask="url(#photoMask)"/>')



#     # Floating skill chips: each chip has an icon and a staggered animation delay.



#     # Keep the five skills close to the portrait, like the supplied reference:
#     # two on the upper sides, two around the lower sides, and one near the base.
#     chips = [
#         # Keep Figma in place; nudge the other four labels outward by only
#         # 10–14 SVG units to match the small shifts marked in the reference.
#         ("Figma", "figma", 760, 185, 0),
#         ("UI/UX", "uiux", 1092, 150, 1),
#         ("AI Agent", "chatgpt", 758, 350, 2),
#         ("Data Analysis", "dataanalysis", 1052, 390, 3),
#         ("Web Development", "webdev", 808, 470, 4),
#     ]

#     for label, ic, x, y, d in chips:



#         w = text_width(label, "geist", 600, 17) + 58



#         s.add(f'<g class="float" style="animation-delay:-{d}s">'



#               f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="#ffffff" fill-opacity="0.08" stroke="#ffffff" stroke-opacity="0.18"/>'



#               + icon(ic, x + 16, y + 12, 20, CREAM))



#         s.text(x + 44, y + 28, label, "G6", 17, CREAM)



#         s.add('</g>')



#     # Header: plain text name only; no logo image or logo asset is required.



#     s.text(56, 68, "SHEHNAZ RANGREZ", "M5", 17, CREAM, spacing=2)



#     s.add(f'<g><rect x="936" y="44" width="296" height="40" rx="20" fill="#000" fill-opacity="0.35" stroke="#ffffff" stroke-opacity="0.15"/>'



#           f'<circle cx="960" cy="64" r="5" fill="#25d366"/><circle class="pulse" cx="960" cy="64" r="5" fill="#25d366"/></g>')



#     s.text(976, 69, "Available for new projects", "G5", 15, CREAM)



#     # Main headline: animate the eyebrow label and large name separately.



#     s.add('<g class="up" style="animation-delay:.1s">')



#     s.text(56, 158, "DESIGN + ENGINEERING STUDIO", "M5", 15, ORANGE, spacing=3)



#     s.add('</g><g class="up" style="animation-delay:.25s">')



#     s.text(52, 262, "Meet", "G8", 104, CREAM, spacing=-3)



#     mx = 52 + text_width("Meet ", "geist", 800, 104, -3)



#     s.text(mx, 262, "Shehnaz", "G8", 104, "url(#gName)", spacing=-3)



#     s.add('</g>')



#     # Typewriter line: cycle through phrases by animating SVG clip-path widths.



#     prefix = "I design & build "



#     s.text(56, 322, prefix, "G5", 32, "#d6d2e4")



#     px = 56 + text_width(prefix, "geist", 500, 32)



#     phrases = ["websites Designs ", "Graphic &  Visual Designs", "full AI web & mobile apps", "Corporate Dashboards & Reports"]



#     period, slot = 16, 4



#     for i, ph in enumerate(phrases):



#         widths = [text_width(ph[:k], "geist", 600, 32) for k in range(len(ph) + 1)]



#         n = len(ph)



#         t_type, t_hold, t_del = 1.6, 3.0, 3.6   # seconds inside the 4s slot



#         vals, keys = [], []



#         for k in range(n + 1):



#             vals.append(widths[k]); keys.append(t_type * k / n)



#         vals.append(widths[n]); keys.append(t_hold)



#         for k in range(n, -1, -1):



#             vals.append(widths[k]); keys.append(t_hold + (t_del - t_hold) * (n - k) / n)



#         vals.append(0); keys.append(period)



#         kt = ";".join(f"{k / period:.4f}" for k in keys)



#         vv = ";".join(f"{v:.1f}" for v in vals)



#         s.defs.append(f'<clipPath id="tw{i}"><rect x="{px}" y="290" height="44" width="0">'



#                       f'<animate attributeName="width" values="{vv}" keyTimes="{kt}" calcMode="discrete" dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect></clipPath>')



#         s.add(f'<g clip-path="url(#tw{i})">')



#         s.text(px, 322, ph, "G6", 32, ORANGE)



#         s.add('</g>')



#         cx = ";".join(f"{px + v + 3:.1f}" for v in vals)



#         s.add(f'<rect x="-20" y="296" width="3" height="34" fill="{ORANGE}" opacity="0">'



#               f'<animate attributeName="x" values="{cx}" keyTimes="{kt}" calcMode="discrete" dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/>'



#               f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{t_del / period:.4f};{t_del / period + 0.001:.4f};1" calcMode="discrete" dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect>')



#     # intro



#     for j, ln in enumerate(["2+ years designing and shipping websites, AI products",



#                             "and Web platforms for startups and brands worldwide."]):



#         s.text(56, 374 + j * 30, ln, "G4", 20, "#b9b3c9")



#     # stats



#     stats = [("2+", "YEARS"), ("15+", "PROJECTS"), ("150+", "HACKATHONS PARTICIPATED"), ("40+", "TEAMS")]

#     for k, (n, lab) in enumerate(stats):
#         x = 56 + k * 168
#         s.add(f'<g class="up" style="animation-delay:{.5 + k * .12:.2f}s">')
#         s.add(f'<rect x="{x}" y="446" width="152" height="80" rx="16" fill="#ffffff" fill-opacity="0.06" stroke="#ffffff" stroke-opacity="0.12"/>')
#         s.text(x + 18, 488, n, "X7", 34, CREAM)
#         if lab == "HACKATHONS PARTICIPATED":
#             # Two short lines stay inside the 152px card instead of touching the Teams card.
#             s.text(x + 18, 506, "HACKATHONS", "M5", 8.5, "#b9b3c9", spacing=1.0)
#             s.text(x + 18, 519, "PARTICIPATED", "M5", 8.5, "#b9b3c9", spacing=0.7)
#         else:
#             s.text(x + 18, 512, lab, "M5", 11, "#b9b3c9", spacing=1.5)
#         s.add('</g>')

#     s.add('</g>')



#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="#ffffff" stroke-opacity="0.10"/>')



#     return s











# # THEMED PROFILE COMPONENTS

# # These builders create cards and sections in both dark and light color schemes.







# # Create a numbered section-heading graphic for a selected theme (dark or light).

# def section(t, num, label, title, note):



#     W, H = 1280, 116



#     s = Svg(W, H)



#     s.defs.append(f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="0.35" stop-color="{ORANGE}" stop-opacity="0.25"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient>')



#     s.text(4, 34, f"{num} / {label}", "M5", 15, ORANGE, spacing=3)



#     s.text(0, 86, title, "G8", 44, t["text"], spacing=-1)



#     s.text(W - 4, 86, note, "G4", 18, t["muted"], anchor="end")



#     s.add(f'<rect x="0" y="108" width="{W}" height="2" fill="url(#ln)"/>')



#     return s











# # Draw the reusable rounded card background and border.

# def card_frame(s, t, w, h, r=24):



#     s.defs.append(f'<clipPath id="cf"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>')



#     s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["line"]}"/>')











# # Draw a row of small label chips inside a card.

# def chip_row(s, t, x, y, items, size=13):



#     for it in items:



#         w = text_width(it, "mono", 500, size) + 22



#         s.add(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="14" fill="{t["chip"]}"/>')



#         s.text(x + 11, y + 19, it, "M5", size, t["chiptext"])



#         x += w + 8



#     return x











# # Create a themed card describing one product, including its image, description, tags, and link label.

# def product_card(t, name, img, tagline, chips, url_label, accent):



#     W, H = 412, 560



#     s = Svg(W, H)



#     card_frame(s, t, W, H)



#     # Product cover images are optional. Use the real image when available;
#     # otherwise draw a branded SVG placeholder so a missing JPG never stops the build.
#     if os.path.isfile(img):

#         uri, _ = img_uri(img, 618, 464)

#         s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="309" preserveAspectRatio="xMidYMid slice"/></g>')

#     else:

#         s.add(f'<g clip-path="url(#cf)">'

#               f'<rect width="{W}" height="309" fill="{t["card2"]}"/>'

#               f'<circle cx="315" cy="82" r="145" fill="{accent}" fill-opacity="0.16"/>'

#               f'<circle cx="74" cy="260" r="112" fill="{accent}" fill-opacity="0.10"/>'

#               f'<path d="M0 245 C105 180 210 315 412 185" fill="none" stroke="{accent}" stroke-opacity="0.45" stroke-width="3"/>'

#               f'<path d="M0 270 C125 200 260 330 412 220" fill="none" stroke="{accent}" stroke-opacity="0.25" stroke-width="2"/>'

#               f'</g>')

#         s.text(W / 2, 165, name, "X7", 42, t["muted"], anchor="middle", spacing=2)



#     s.add(f'<rect x="0" y="309" width="{W}" height="1" fill="{t["line"]}"/>')



#     s.add(f'<rect x="28" y="336" width="8" height="30" rx="4" fill="{accent}"/>')



#     s.text(48, 362, name, "X7", 32, t["text"], spacing=1)



#     for j, ln in enumerate(wrap(tagline, "geist", 400, 17, W - 56)[:3]):



#         s.text(28, 398 + j * 25, ln, "G4", 17, t["muted"])



#     chip_row(s, t, 28, 470, chips)



#     s.text(28, 532, url_label, "G6", 17, ORANGE)



#     s.add(f'<path d="M{W - 50} 520 l12 0 m0 0 l0 12 m0 -12 l-14 14" stroke="{ORANGE}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')



#     return s











# # Create a themed service card with supporting icons and a short description.

# def service_card(t, title, desc, icons, foot):



#     W, H = 412, 236



#     s = Svg(W, H)



#     card_frame(s, t, W, H, 22)



#     x = 26



#     for ic in icons:



#         s.add(f'<rect x="{x}" y="26" width="52" height="52" rx="14" fill="{t["tile"]}" stroke="{t["line"]}"/>')



#         if ic == "pen":



#             s.add(raw_icon(PEN, x + 14, 40, 24, ORANGE))



#         elif ic == "coin":



#             s.add(f'<circle cx="{x + 26}" cy="52" r="12" fill="none" stroke="{ORANGE}" stroke-width="2.4"/>')



#             s.text(x + 26, 58, "$", "G8", 16, ORANGE, anchor="middle")



#         else:



#             s.add(icon(ic, x + 14, 40, 24, ORANGE))



#         x += 62



#     s.text(26, 116, title, "G6", 22, t["text"])



#     for j, ln in enumerate(wrap(desc, "geist", 400, 16, W - 52)[:2]):



#         s.text(26, 146 + j * 23, ln, "G4", 16, t["muted"])



#     s.add(f'<rect x="26" y="188" width="{W - 52}" height="1" fill="{t["line"]}"/>')



#     s.text(26, 216, foot, "M5", 13, ORANGE, spacing=1)



#     s.add(f'<path d="M{W - 42} 202 l9 0 m0 0 l0 9 m0 -9 l-11 11" stroke="{ORANGE}" stroke-width="2" fill="none" stroke-linecap="round"/>')



#     return s











# # Create a themed portfolio/client-work card with its preview image and category.

# def work_card(t, title, kind, img):



#     W, H = 412, 336



#     s = Svg(W, H)



#     card_frame(s, t, W, H, 22)



#     # Portfolio preview images are optional; draw a subtle placeholder when absent.
#     if os.path.isfile(img):

#         uri, _ = img_uri(img, 618, 400, crop=None)

#         s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="266" preserveAspectRatio="xMidYMin slice"/></g>')

#     else:

#         s.add(f'<g clip-path="url(#cf)">'

#               f'<rect width="{W}" height="266" fill="{t["card2"]}"/>'

#               f'<circle cx="320" cy="40" r="130" fill="{ORANGE}" fill-opacity="0.13"/>'

#               f'<circle cx="75" cy="230" r="105" fill="{INDIGO}" fill-opacity="0.13"/>'

#               f'<path d="M0 208 L145 90 L250 170 L412 38" fill="none" stroke="{t["muted"]}" stroke-opacity="0.32" stroke-width="3"/>'

#               f'</g>')

#         s.text(W / 2, 145, kind.upper(), "M5", 16, t["muted"], anchor="middle", spacing=2)



#     s.add(f'<rect x="0" y="266" width="{W}" height="1" fill="{t["line"]}"/>')



#     s.text(24, 306, title, "G6", 20, t["text"])



#     s.text(W - 24, 306, kind, "M5", 12, t["muted"], anchor="end", spacing=1)



#     return s











# # Create a small social/platform link badge.

# def pill(t, label, ic):



#     w = int(text_width(label, "geist", 600, 16) + 66)



#     s = Svg(w, 46)



#     s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="45" rx="23" fill="{t["card"]}" stroke="{t["line"]}"/>')



#     if ic == "globe":



#         s.add(raw_icon(GLOBE, 18, 13, 20, ORANGE))



#     elif ic == "contra":



#         s.add(f'<circle cx="28" cy="23" r="10" fill="{ORANGE}"/>')



#         s.text(28, 28, "C", "G8", 13, "#ffffff", anchor="middle")



#     else:



#         s.add(icon(ic, 18, 13, 20, ORANGE))



#     s.text(46, 29, label, "G6", 16, t["text"])



#     return s











# # Create the small currently-working / availability status strip.

# def now_strip(t):



#     W, H = 1280, 76



#     s = Svg(W, H)



#     s.css.append('.pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}'



#                  '@keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}')



#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="38" fill="{t["card"]}" stroke="{t["line"]}"/>')



#     s.add(f'<rect x="14" y="14" width="96" height="48" rx="24" fill="{ORANGE}"/>')



#     s.text(62, 44, "NOW", "M5", 16, "#ffffff", anchor="middle", spacing=3)



#     s.add(f'<circle cx="140" cy="38" r="5" fill="#25d366"/><circle class="pulse" cx="140" cy="38" r="5" fill="#25d366"/>')



#     msg = "Shipping SYVO, a personal AI agent, in private pilot. Open for Framer, AI and Web3 projects."



#     s.text(160, 44, msg, "G5", 18, t["text"])



#     return s











# # Create the animated scrolling technology-stack strip.

# def stack(t):



#     W, H = 1280, 150



#     names = [("figma", "Figma"), ("framer", "Framer"), ("react", "React"), ("nextdotjs", "Next.js"),



#              ("typescript", "TypeScript"), ("tailwindcss", "Tailwind"), ("flutter", "Flutter"),



#              ("nodedotjs", "Node.js"), ("python", "Python"), ("supabase", "Supabase"), ("firebase", "Firebase"),



#              ("openai", "OpenAI"), ("claude", "Claude"), ("n8n", "n8n"), ("solidity", "Solidity"),



#              ("ethereum", "Ethereum"), ("solana", "Solana"), ("wordpress", "WordPress"), ("shopify", "Shopify")]



#     step = 132



#     span = step * len(names)



#     s = Svg(W, H)



#     s.defs.append(f'<clipPath id="sc"><rect width="{W}" height="{H}" rx="24"/></clipPath>'



#                   f'<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{t["card"]}"/><stop offset="0.07" stop-color="{t["card"]}" stop-opacity="0"/>'



#                   f'<stop offset="0.93" stop-color="{t["card"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["card"]}"/></linearGradient>')



#     s.css.append(f'.mq{{animation:mq 38s linear infinite}}@keyframes mq{{from{{transform:translateX(0)}}to{{transform:translateX(-{span}px)}}}}')



#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="{t["card"]}" stroke="{t["line"]}"/>')



#     s.add('<g clip-path="url(#sc)"><g class="mq">')



#     for rep in range(2):



#         for k, (ic, lab) in enumerate(names):



#             x = 30 + rep * span + k * step



#             s.add(f'<rect x="{x}" y="26" width="64" height="64" rx="18" fill="{t["tile"]}" stroke="{t["line"]}"/>')



#             s.add(icon(ic, x + 18, 44, 28, t["text"]))



#             s.text(x + 32, 120, lab, "M5", 13, t["muted"], anchor="middle")



#     s.add('</g></g>')



#     s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#edge)"/>')



#     return s











# # Build the shared call-to-action banner shown near the end of the profile.

# def cta():
#     W, H = 1280, 300
#     s = Svg(W, H)

#     s.defs.append(f'''<clipPath id="cc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
# <radialGradient id="ca" cx="0.15" cy="0" r="0.8"><stop offset="0" stop-color="#3b22b8" stop-opacity="0.9"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
# <radialGradient id="cb" cx="0.85" cy="1.1" r="0.7"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.8"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
# <pattern id="cg" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#fff" stroke-opacity="0.045"/></pattern>
# <linearGradient id="cn" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="0.55" stop-color="{PINK}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>''')

#     # A short, subtle bob on each contact button, plus a one-time typewriter
#     # reveal for the CTA headline when the SVG first appears.
#     s.css.append('''
# .contact-float{transform-box:fill-box;transform-origin:center;animation:contactFloat 4.8s ease-in-out infinite}
# @keyframes contactFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
# .type-char{opacity:0;animation:typeReveal .01s steps(1,end) forwards}
# @keyframes typeReveal{to{opacity:1}}
# ''')

#     s.add(f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#cg)"/><rect width="{W}" height="{H}" fill="url(#ca)"/><rect width="{W}" height="{H}" fill="url(#cb)"/></g>')
#     s.text(64, 92, "HAVE A PROJECT IN MIND?", "M5", 16, ORANGE, spacing=3)

#     # Build the headline as individually revealed characters. The first part
#     # stays cream and the final word keeps the orange-pink-violet gradient.
#     title_plain = "Let's build it "
#     title_gradient = "together."
#     s.used.setdefault("G8", set()).update(title_plain + title_gradient)
#     title_spans = []
#     typing_step = 0.052
#     for i, ch in enumerate(title_plain):
#         title_spans.append(
#             f'<tspan class="type-char" style="animation-delay:{i * typing_step:.3f}s">{escape(ch)}</tspan>'
#         )
#     title_spans.append('<tspan fill="url(#cn)">')
#     for i, ch in enumerate(title_gradient, start=len(title_plain)):
#         title_spans.append(
#             f'<tspan class="type-char" style="animation-delay:{i * typing_step:.3f}s">{escape(ch)}</tspan>'
#         )
#     title_spans.append('</tspan>')
#     s.add(
#         '<text x="60" y="168" font-family="G8" font-size="72" '
#         f'letter-spacing="-2" fill="{CREAM}" xml:space="preserve">'
#         + ''.join(title_spans) + '</text>'
#     )

#     s.text(64, 222, "Web design  •  UI/UX  •  AI agents  •  Data analysis  •  Web development", "G4", 18, "#c9c3d8")
#     s.text(1216, 92, "SHEHNAZ RANGREZ", "M5", 15, "#c9c3d8", anchor="end")

#     contacts = [
#         ("LinkedIn", "linkedin", LINKEDIN_URL, 770, 0.0),
#         ("Gmail", "gmail", f"mailto:{GMAIL_ADDRESS}", 925, 1.1),
#         ("GitHub", "github", GITHUB_URL, 1080, 2.2),
#     ]
#     for label, ic, href, x, delay in contacts:
#         # Anchors work when cta.svg is opened directly; use social-links.md for
#         # clickable Markdown wrappers when the SVG is embedded in a README.
#         s.add(f'<a href="{escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">')
#         s.add(f'<g class="contact-float" style="animation-delay:-{delay}s">')
#         s.add(f'<rect x="{x}" y="194" width="140" height="58" rx="29" fill="#ffffff" fill-opacity="0.09" stroke="#ffffff" stroke-opacity="0.22"/>')
#         s.add(icon(ic, x + 17, 212, 22, CREAM))
#         s.text(x + 49, 230, label, "G6", 17, CREAM)
#         s.add('</g></a>')

#     s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="#fff" stroke-opacity="0.1"/>')
#     return s


# # Render an individual contact badge. Markdown can wrap each badge in a real link.
# def social_badge(label, icon_name):
#     w, h = 160, 48
#     badge = Svg(w, h)
#     badge.css.append('''
# .badge-float{transform-box:fill-box;transform-origin:center;animation:badgeFloat 4.8s ease-in-out infinite}
# @keyframes badgeFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
# ''')
#     badge.add('<g class="badge-float">')
#     badge.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="24" fill="#181a23" stroke="rgba(255,255,255,0.18)"/>')
#     badge.add(icon(icon_name, 15, 13, 22, CREAM))
#     badge.text(48, 30, label, "G6", 15, CREAM)
#     badge.add('</g>')
#     return badge


# def write_social_markdown():
#     """Write README-ready links using paths relative to the detected README."""
#     readme_candidates = [
#         os.path.join(ROOT, "README.md"),
#         os.path.join(PARENT_DIR, "README.md"),
#     ]
#     readme_path = next((p for p in readme_candidates if os.path.isfile(p)), None)
#     readme_dir = os.path.dirname(readme_path) if readme_path else ROOT
#     asset_prefix = os.path.relpath(OUT, readme_dir).replace(os.sep, "/")
#     if asset_prefix == ".":
#         asset_prefix = "assets"
#     else:
#         asset_prefix = asset_prefix.rstrip("/")

#     rows = [
#         f'[![LinkedIn]({asset_prefix}/social/linkedin.svg)]({LINKEDIN_URL})',
#         f'[![Gmail]({asset_prefix}/social/gmail.svg)](mailto:{GMAIL_ADDRESS})',
#         f'[![GitHub]({asset_prefix}/social/github.svg)]({GITHUB_URL})',
#     ]
#     path = os.path.join(OUT, "social-links.md")
#     with open(path, "w", encoding="utf-8") as f:
#         f.write("\n".join(rows) + "\n")
#     return path










# # PROFILE CONTENT DATA

# # Edit these lists to change the products, services, portfolio items, and social links.







# LK = f"{DOCS}/launch-kit"



# BH = f"{CP}/behance"







# # Product cards: (slug, display name, image path, description, tags, link text, accent color).

# PRODUCTS = [



#     ("xoxi", "XOXI", f"{CP}/products/xoxi-cover.jpg",



#      "Your CV becomes a verified portfolio you can apply with. AI match scores for the teams hiring.",



#      ["Web", "iOS", "Android", "AI"], "Visit xoxi.me", "#3b82f6"),



#     ("syvo", "SYVO", f"{CP}/products/syvo-cover.jpg",



#      "A personal AI agent. Ask in plain words and it finds, books or sells for you, then waits for your OK.",



#      ["AI agent", "Flutter", "Web"], "Visit syvo.si", "#4ade80"),



#     ("lovii", "LOVII", f"{CP}/products/lovii-cover.jpg",



#      "A private journal for couples. One short note a day, drawn by AI as an illustrated card.",



#      ["iOS", "Android", "AI art"], "Visit lovii.app", PINK),



# ]







# # Service cards: (slug, title, description, icon names).

# SERVICES = [



#     ("framer", "Framer websites", "Responsive sites with real scroll motion, CMS and SEO, from Figma or from scratch.", ["framer"]),



#     ("agents", "AI agents & automations", "Chatbots, n8n and Make workflows and custom agents that do real work.", ["n8n", "openai"]),



#     ("aiapps", "Full AI web & mobile apps", "Website, web app and iOS + Android apps, designed and built end to end.", ["flutter", "react"]),



#     ("uiux", "UI/UX design", "Websites, dashboards and mobile apps in Figma with clickable prototypes.", ["figma"]),



#     ("wpshop", "WordPress & Shopify", "Business sites and online stores that are easy to run after launch.", ["wordpress", "shopify"]),



#     ("nftweb", "NFT & Web3 websites", "Marketplaces, mint pages and landing pages that make wallets feel simple.", ["ethereum"]),



#     ("dapp", "Smart contracts & dApps", "NFT minting dApps and contracts on Ethereum, Polygon and Solana.", ["solidity", "solana"]),



#     ("memecoin", "Meme coin websites", "Loud, fun coin sites with tokenomics, presale pages and buy flows.", ["coin", "solana"]),



#     ("brand", "Logo & brand identity", "Minimal logos and brand kits for startups, products and Web3 projects.", ["pen"]),



# ]







# # Selected work cards: (slug, project name, category label).

# WORK = [



#     ("medelz", "Medelz", "MUSIC PLATFORM"), ("smartforum", "Smart Forum", "IT SERVICES"),



#     ("satholler", "SatHoller", "NFT AUCTIONS"), ("metaadsfirm", "MetaAdsFirm", "WEB3 AGENCY"),



#     ("blackmomento", "The Black Momento", "E-COMMERCE"), ("blckbuster", "Blckbuster", "WEB3 MARKETPLACE"),



# ]







# # Social/platform badges: (slug, visible label, icon filename).

# PILLS = [("site", "Website", "globe"), ("framer", "Framer", "framer"), ("contra", "Contra", "contra"),



#          ("fiverr", "Fiverr", "fiverr"), ("x", "X", "x"), ("youtube", "YouTube", "youtube"),



#          ("instagram", "Instagram", "instagram"), ("linkedin", "LinkedIn", "linkedin")]











# # Generate all shared and theme-specific SVG assets, then print a summary of output sizes.

# def main():



#     sizes = {}



#     sizes["hero.svg"] = save(hero(), "hero.svg")

#     sizes["cta.svg"] = save(cta(), "cta.svg")

#     for slug, label, icon_name in [
#         ("linkedin", "LinkedIn", "linkedin"),
#         ("gmail", "Gmail", "gmail"),
#         ("github", "GitHub", "github"),
#     ]:
#         sizes[f"social/{slug}"] = save(social_badge(label, icon_name), "social", f"{slug}.svg")

#     write_social_markdown()



#     for name, t in THEMES.items():



#         sizes[f"{name}/now"] = save(now_strip(t), name, "now.svg")



#         for key, label, title, note in [("01", "PRODUCTS", "Products I've built", "Designed, built and shipped in-house"),



#                                         ("02", "SERVICES", "What I can do for you", "Every card opens the matching gig"),



#                                         ("03", "SELECTED WORK", "Selected client work", "Full case studies on Behance"),



#                                         ("04", "STACK", "Tools I ship with", "Design, code, AI and Web3"),



#                                         ("05", "ACTIVITY", "Building in public", "Updated daily by GitHub Actions")]:



#             sizes[f"{name}/s{key}"] = save(section(t, key, label, title, note), name, f"s{key}.svg")



#         for slug, nm, img, tag, chips, url, acc in PRODUCTS:



#             sizes[f"{name}/p-{slug}"] = save(product_card(t, nm, img, tag, chips, url, acc), name, f"p-{slug}.svg")

#         for slug, title, desc, icons in SERVICES:

#             sizes[f"{name}/sv-{slug}"] = save(service_card(t, title, desc, icons, "VIEW ON FIVERR"), name, f"sv-{slug}.svg")

#         for slug, title, kind in WORK:

#             sizes[f"{name}/w-{slug}"] = save(work_card(t, title, kind, f"{BH}/{slug}/01.png"), name, f"w-{slug}.svg")

#         for slug, label, ic in PILLS:

#             sizes[f"{name}/l-{slug}"] = save(pill(t, label, ic), name, f"l-{slug}.svg")

#         sizes[f"{name}/stack"] = save(stack(t), name, "stack.svg")

#     total = sum(sizes.values())

#     big = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]

#     print(f"{len(sizes)} files, {total / 1e6:.2f} MB total; largest: " + ", ".join(f"{k} {v // 1024}KB" for k, v in big))

# if __name__ == "__main__":



#     main()
# )

"""Builds every graphic in the Shehnaz-R GitHub profile README  (WHITE + BLUE edition).

Each SVG is self-contained: fonts are subset and embedded, images are inlined,
so nothing breaks when GitHub proxies the file. Run: python build_annotated.py
Outputs go to assets/dark and assets/light (hero, CTA and social badges are shared).

Design language
  * light theme : crisp white cards on an ice-blue canvas, royal-blue accents
  * dark theme  : deep midnight-blue cards, soft sky-blue accents
  * hero / CTA  : matching airy white-to-sky banners with navy type and blue gradients
"""
import base64
import io
import logging
import os
import re
from html import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

logging.getLogger("fontTools").setLevel(logging.ERROR)

# --------------------------------------------------------------------------
# PROJECT PATHS
# Supported layouts:
#   New/build_annotated.py     + New/assets/Profile svg.svg
#   project/tools/build_annotated.py + project/assets/Profile svg.svg
# --------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

if os.path.basename(SCRIPT_DIR).lower() == "tools":
    ROOT = PARENT_DIR
elif os.path.isdir(os.path.join(SCRIPT_DIR, "assets")):
    ROOT = SCRIPT_DIR
elif os.path.isdir(os.path.join(PARENT_DIR, "assets")):
    ROOT = PARENT_DIR
else:
    ROOT = SCRIPT_DIR

OUT = os.path.join(ROOT, "assets")
DOCS = ROOT
CP = ROOT

_TOOL_CANDIDATES = [
    os.path.join(ROOT, "tools"),
    SCRIPT_DIR,
    os.path.join(PARENT_DIR, "tools"),
    os.path.join(PARENT_DIR, "Tools"),
]
TOOLS = next(
    (c for c in _TOOL_CANDIDATES
     if os.path.isdir(os.path.join(c, "fonts")) or os.path.isdir(os.path.join(c, "icons"))),
    os.path.join(ROOT, "tools"),
)

# --------------------------------------------------------------------------
# COLOR PALETTE  (white + blue)
# --------------------------------------------------------------------------
WHITE = "#ffffff"
ICE = "#eef6ff"          # page tint
MIST = "#f5f9ff"
SKY_100 = "#e0f0ff"
SKY_200 = "#bae6fd"
SKY = "#38bdf8"          # light accent
AZURE = "#3b82f6"        # mid accent
BLUE = "#2563eb"         # primary accent
BLUE_DEEP = "#1d4ed8"
NAVY = "#0b1b3f"         # main text on light
NAVY_SOFT = "#1e3a8a"
SLATE = "#5b6b8c"        # muted text on light
INDIGO = "#6366f1"       # tiny pop of violet-blue for variety
GREEN = "#25d366"        # availability dot

# CONTACT LINKS: replace these three placeholders with your real profile details.
# The Gmail link automatically becomes a mailto: link.
LINKEDIN_URL = "https://www.linkedin.com/in/YOUR-LINKEDIN-USERNAME/"
GMAIL_ADDRESS = "YOUR-GMAIL-ADDRESS@gmail.com"
GITHUB_URL = "https://github.com/YOUR-GITHUB-USERNAME"

# Theme tokens. Every themed component reads colors from this dictionary.
THEMES = {
    "dark": dict(
        bg="#0a1226", card="#0f1b36", card2="#142347",
        line="rgba(147,197,253,0.16)", text="#eaf3ff", muted="#8fa6cc",
        chip="#17284d", chiptext="#cfe2ff", tile="#13223f",
        accent="#60a5fa", accent_text="#ffffff",
    ),
    "light": dict(
        bg=ICE, card=WHITE, card2=SKY_100,
        line="rgba(37,99,235,0.14)", text=NAVY, muted=SLATE,
        chip="#e6f0ff", chiptext=NAVY_SOFT, tile=MIST,
        accent=BLUE, accent_text="#ffffff",
    ),
}

# --------------------------------------------------------------------------
# FONT HANDLING
# Load, measure, subset and embed fonts so the SVGs stay self-contained.
# --------------------------------------------------------------------------
def _find_font(candidates):
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


_WINDOWS_FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
_SAFE_FALLBACKS = [
    os.path.join(_WINDOWS_FONTS, "arial.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

FONT_SRC = {
    "geist": _find_font([os.path.join(TOOLS, "fonts", "Geist.ttf"),
                         os.path.join(ROOT, "fonts", "Geist.ttf")] + _SAFE_FALLBACKS),
    "mono": _find_font([os.path.join(TOOLS, "fonts", "GeistMono.ttf"),
                        os.path.join(ROOT, "fonts", "GeistMono.ttf"),
                        os.path.join(_WINDOWS_FONTS, "consola.ttf"),
                        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]),
    "oxanium": _find_font([os.path.join(TOOLS, "fonts", "Oxanium.ttf"),
                           os.path.join(ROOT, "fonts", "Oxanium.ttf")] + _SAFE_FALLBACKS),
}
for _k, _p in list(FONT_SRC.items()):
    if _p is None:
        FONT_SRC[_k] = _find_font(_SAFE_FALLBACKS)

_static = {}


def static_font(key, weight):
    """Variable font -> cached static instance at the requested weight."""
    k = (key, weight)
    if k not in _static:
        path = FONT_SRC.get(key)
        if not path or not os.path.isfile(path):
            raise FileNotFoundError(
                f"No usable font for '{key}'. Install a system font or put the "
                "original font files in tools/fonts."
            )
        f = TTFont(path)
        # System fallbacks are static fonts and must skip the variable-font instancer.
        _static[k] = instancer.instantiateVariableFont(f, {"wght": weight}) if "fvar" in f else f
    return _static[k]


def text_width(s, key, weight, size, spacing=0.0):
    """Measure text with the real font so SVG text can be placed precisely."""
    f = static_font(key, weight)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    w = 0
    for ch in s:
        g = cmap.get(ord(ch))
        w += hmtx[g][0] if g else upm * 0.5
    return w * size / upm + spacing * len(s)


def font_face(key, weight, family, chars):
    """Subset the font to the used characters and embed it as base64 WOFF."""
    f = static_font(key, weight)
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    sub = TTFont(buf)
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga"]
    sb = subset.Subsetter(opts)
    sb.populate(text="".join(sorted(set(chars))) + " ")
    sb.subset(sub)
    out = io.BytesIO()
    sub.flavor = "woff"
    sub.save(out)
    b64 = base64.b64encode(out.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff;base64,{b64}) format('woff');}}"


# Short labels used by Svg.text() -> (font file key, weight)
FAMILIES = {
    "G4": ("geist", 400), "G5": ("geist", 500), "G6": ("geist", 600), "G8": ("geist", 800),
    "M5": ("mono", 500), "X7": ("oxanium", 700),
}


class Svg:
    """Collects shapes, text, CSS and defs; embeds only the glyphs actually used."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts, self.defs, self.css = [], [], []
        self.used = {}

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, fam, size, fill, anchor="start", spacing=0, extra="", cls=""):
        self.used.setdefault(fam, set()).update(s)
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        c = f' class="{cls}"' if cls else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}"{ls}{c} {extra}>{escape(s)}</text>')

    def render(self):
        faces = "".join(font_face(*FAMILIES[f], f, chars) for f, chars in self.used.items())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<defs><style>{faces}{"".join(self.css)}</style>{"".join(self.defs)}</defs>'
                f'{"".join(self.parts)}</svg>')


def save(svg, *path):
    """Write one SVG under assets/ and return its size in bytes."""
    p = os.path.join(OUT, *path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    data = svg.render() if isinstance(svg, Svg) else svg
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(data)
    return len(data)


# --------------------------------------------------------------------------
# IMAGE AND ICON HELPERS
# --------------------------------------------------------------------------
def img_uri(path, w, h=None, crop=None, fmt="JPEG", q=82, cover=True):
    """Crop/resize/compress an image and return it as a base64 data URI."""
    im = Image.open(path)
    im = im.convert("RGBA" if fmt in ("PNG", "WEBP") else "RGB")
    if crop:
        im = im.crop(crop)
    if h:
        if cover:
            sc = max(w / im.width, h / im.height)
            im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
            left, top = (im.width - w) // 2, 0
            im = im.crop((left, top, left + w, top + h))
        else:
            im.thumbnail((w, h), Image.LANCZOS)
    else:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "WEBP":
        im.save(buf, fmt, quality=q, method=6)
    else:
        im.save(buf, fmt, quality=q, optimize=True)
    mime = {"JPEG": "jpeg", "PNG": "png", "WEBP": "webp"}[fmt]
    return f"data:image/{mime};base64,{base64.b64encode(buf.getvalue()).decode()}", im.size


def icon_path(name):
    """Read a supplied SVG icon from tools/icons, or fall back to a sparkle."""
    icon_file = os.path.join(TOOLS, "icons", f"{name}.svg")
    if os.path.isfile(icon_file):
        with open(icon_file, "r", encoding="utf-8") as f:
            match = re.search(r'<path[^>]*\bd="([^"]+)"', f.read())
        if match:
            return match.group(1)
    return "M12 2.5 14.2 9.8 21.5 12 14.2 14.2 12 21.5 9.8 14.2 2.5 12 9.8 9.8Z"


_OPENAI_PATH = (
    "M14.949 6.547a3.94 3.94 0 0 0-.348-3.273 4.11 4.11 0 0 0-4.4-1.934 "
    "A4.1 4.1 0 0 0 8.423.2 4.15 4.15 0 0 0 6.305.086a4.1 4.1 0 0 0-1.891.948 "
    "4.04 4.04 0 0 0-1.158 1.753 4.1 4.1 0 0 0-1.563.679A4 4 0 0 0 .554 4.72a3.99 "
    "3.99 0 0 0 .502 4.731 3.94 3.94 0 0 0 .346 3.274 4.11 4.11 0 0 0 4.402 "
    "1.933c.382.425.852.764 1.377.995.526.231 1.095.35 1.67.346 1.78.002 "
    "3.358-1.132 3.901-2.804a4.1 4.1 0 0 0 1.563-.68 4 4 0 0 0 1.14-1.253 "
    "3.99 3.99 0 0 0-.506-4.716m-6.097 8.406a3.05 3.05 0 0 1-1.945-.694l.096-.054 "
    "3.23-1.838a.53.53 0 0 0 .265-.455v-4.49l1.366.778q.02.011.025.035v3.722c-.003 "
    "1.653-1.361 2.992-3.037 2.996m-6.53-2.75a2.95 2.95 0 0 1-.36-2.01l.095.057 "
    "3.233 1.84a.53.53 0 0 0 .527 0l3.949-2.246v1.555a.05.05 0 0 1-.022.041L6.473 "
    "13.3c-1.454.826-3.311.335-4.15-1.098m-.85-6.94A3.02 3.02 0 0 1 3.07 3.949v3.785a.51.51 "
    "0 0 0 .262.451l3.93 2.237-1.366.779a.05.05 0 0 1-.048 0L2.585 9.342a2.98 2.98 "
    "0 0 1-1.113-4.094zm11.216 2.571L8.747 5.576l1.362-.776a.05.05 0 0 1 .048 0l3.265 "
    "1.86a3 3 0 0 1 1.173 1.207 2.96 2.96 0 0 1-.27 3.2 3.05 3.05 0 0 1-1.36.997V8.279a.52.52 "
    "0 0 0-.276-.445m1.36-2.015-.097-.057-3.226-1.855a.53.53 0 0 0-.53 0L6.249 "
    "6.153V4.598a.04.04 0 0 1 .019-.04L9.533 2.7a3.07 3.07 0 0 1 3.257.139c.474.325.843.778 "
    "1.066 1.303.223.526.289 1.103.191 1.664zM5.503 8.575 4.139 7.8a.05.05 0 0 1-.026-.037V4.049"
    "c0-.57.166-1.127.476-1.607.31-.48.752-.864 1.275-1.105a3.08 3.08 0 0 1 3.234.41l-.096.054"
    "-3.23 1.838a.53.53 0 0 0-.265.455zm.742-1.577 1.758-1 1.762 1v2l-1.755 1-1.762-1z"
)

_GITHUB_PATH = (
    "M12 2.5a9.6 9.6 0 0 0-3.04 18.7c.48.09.65-.2.65-.46v-1.7c-2.66.58-3.22-1.13-3.22-1.13"
    "-.44-1.1-1.07-1.4-1.07-1.4-.87-.6.07-.59.07-.59.96.07 1.46.99 1.46.99.85 1.45 2.22 1.03 "
    "2.76.79.08-.62.33-1.03.6-1.27-2.12-.24-4.35-1.06-4.35-4.72 0-1.04.37-1.89.98-2.56-.1-.24"
    "-.43-1.21.09-2.52 0 0 .8-.26 2.64.98a9.2 9.2 0 0 1 4.8 0c1.84-1.24 2.64-.98 2.64-.98.52 "
    "1.31.19 2.28.09 2.52.61.67.98 1.52.98 2.56 0 3.67-2.23 4.48-4.36 4.72.34.3.64.87.64 1.76"
    "v2.55c0 .26.17.56.66.46A9.6 9.6 0 0 0 12 2.5Z"
)


def icon(name, x, y, size, fill):
    """Return a self-contained vector icon. Key portfolio skills use custom marks."""
    scale = size / 24
    tf = f"translate({x} {y}) scale({scale})"
    stroke = (f'fill="none" stroke="{fill}" stroke-linecap="round" stroke-linejoin="round"')

    if name == "figma":  # single-colour Figma mark, follows the fill
        return (f'<g transform="{tf}" fill="{fill}">'
                '<rect x="3" y="1" width="9" height="7" rx="3.5"/>'
                '<rect x="12" y="1" width="9" height="7" rx="3.5"/>'
                '<rect x="3" y="8" width="9" height="7" rx="3.5"/>'
                '<circle cx="16.5" cy="11.5" r="3.5"/>'
                '<rect x="3" y="15" width="9" height="8" rx="4"/></g>')

    if name == "uiux":  # pen nib over an interface frame
        return (f'<g transform="{tf}" {stroke} stroke-width="1.8">'
                '<rect x="2.5" y="3" width="19" height="18" rx="3.2" opacity=".65"/>'
                '<path d="M7 16.8 8.4 12l6.9-6.9 3.6 3.6L12 15.6 7 16.8Z"/>'
                '<path d="m13.9 6.5 3.6 3.6M7 16.8l3.4-.8"/></g>')

    if name == "chatgpt":  # OpenAI mark (16x16 path)
        return (f'<path transform="translate({x} {y}) scale({size / 16})" d="{_OPENAI_PATH}" '
                f'fill="{fill}" fill-rule="evenodd"/>')

    if name == "dataanalysis":  # axes, bars and a sky-blue trend line
        return (f'<g transform="{tf}" {stroke} stroke-width="1.8">'
                '<path d="M3 3.5v17h18"/>'
                f'<rect x="6" y="12" width="3.2" height="5.5" rx=".7" fill="{fill}" stroke="none"/>'
                f'<rect x="11.2" y="8.5" width="3.2" height="9" rx=".7" fill="{fill}" stroke="none"/>'
                f'<rect x="16.4" y="5" width="3.2" height="12.5" rx=".7" fill="{fill}" stroke="none"/>'
                f'<path d="m5.5 9.5 4-3 4 1 5-4" stroke="{SKY}" stroke-width="1.5"/></g>')

    if name == "webdev":  # code brackets and slash
        return (f'<g transform="{tf}" {stroke} stroke-width="2.1">'
                '<path d="m8.2 6-5.2 6 5.2 6M15.8 6l5.2 6-5.2 6M14 3.8 10 20.2"/></g>')

    if name == "linkedin":
        return (f'<g transform="{tf}" {stroke} stroke-width="2">'
                '<path d="M5 9v10M5 5.5v.2M10 19v-6.2a3 3 0 0 1 6 0V19M10 10v9"/></g>')

    if name == "gmail":
        return (f'<g transform="{tf}" {stroke} stroke-width="1.8">'
                '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/>'
                '<path d="m4 6 8 6 8-6"/></g>')

    if name == "github":
        return f'<g transform="{tf}" fill="{fill}" stroke="none"><path d="{_GITHUB_PATH}"/></g>'

    return f'<path transform="{tf}" d="{icon_path(name)}" fill="{fill}"/>'


GLOBE = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 6h-2.95a15.7 15.7 0 0 0-1.38-3.56A8.03 8.03 0 0 1 "
         "18.9 8ZM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96ZM4.26 14a8.2 8.2 0 0 1 "
         "0-4h3.38a16.5 16.5 0 0 0 0 4H4.26Zm.84 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 0 1 5.1 16Zm2.95-8"
         "H5.1a7.99 7.99 0 0 1 4.33-3.56A15.7 15.7 0 0 0 8.05 8ZM12 19.96A14.1 14.1 0 0 1 10.09 16h3.82A14.1 14.1 0 "
         "0 1 12 19.96ZM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4Zm.25 5.56c.6-1.11 1.06-2.31 1.38"
         "-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56ZM16.36 14a16.5 16.5 0 0 0 0-4h3.38a8.2 8.2 0 0 1 0 4h-3.38Z")
PEN = "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25ZM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z"


def raw_icon(d, x, y, size, fill):
    """Place a 24x24 icon straight from path data."""
    return f'<path transform="translate({x} {y}) scale({size / 24})" d="{d}" fill="{fill}"/>'


def wrap(s, key, weight, size, maxw):
    """Split a sentence into lines that fit within maxw pixels."""
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if text_width(t, key, weight, size) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# HERO BANNER  (shared by dark and light READMEs; light, airy, blue)
# --------------------------------------------------------------------------
def hero():
    W, H = 1280, 560
    s = Svg(W, H)

    s.defs.append(f'''
<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<linearGradient id="gBg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WHITE}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
<radialGradient id="gSky" cx="0.14" cy="0.02" r="0.78"><stop offset="0" stop-color="{SKY}" stop-opacity="0.50"/>
 <stop offset="0.5" stop-color="{SKY_200}" stop-opacity="0.30"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
<radialGradient id="gBlue" cx="0.88" cy="1.05" r="0.62"><stop offset="0" stop-color="{AZURE}" stop-opacity="0.42"/>
 <stop offset="0.55" stop-color="{AZURE}" stop-opacity="0.12"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
<radialGradient id="gHalo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{AZURE}" stop-opacity="0.38"/>
 <stop offset="0.6" stop-color="{SKY}" stop-opacity="0.12"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></radialGradient>
<linearGradient id="gName" x1="0" x2="1"><stop offset="0" stop-color="{BLUE_DEEP}"/><stop offset="0.55" stop-color="{AZURE}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="{BLUE}" stroke-opacity="0.07"/></pattern>
<linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0.72" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="photoMask"><rect width="{W}" height="{H}" fill="url(#fadeBottom)"/></mask>''')

    # Entrance, float, pulse and blink animations.
    s.css.append('''
.up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.float{animation:float 6s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.drift{animation:drift 14s ease-in-out infinite}
@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(14px,-10px)}}
.pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}
@keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}
''')

    s.add('<g clip-path="url(#frame)">')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#gBg)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#gSky)"/><rect width="{W}" height="{H}" fill="url(#gBlue)"/>')

    # Decorative rings + halo behind the portrait.
    s.add(f'<g class="drift"><circle cx="1010" cy="330" r="260" fill="url(#gHalo)"/>'
          f'<circle cx="1010" cy="330" r="210" fill="none" stroke="{AZURE}" stroke-opacity="0.18" stroke-dasharray="3 9"/>'
          f'<circle cx="1010" cy="330" r="300" fill="none" stroke="{SKY}" stroke-opacity="0.16"/></g>')

    # Portrait (SVG file inlined as a data URI).
    hero_image_path = os.path.join(OUT, "Profile svg.svg")
    if not os.path.isfile(hero_image_path):
        candidates = [os.path.join(OUT, "Profile.svg"), os.path.join(OUT, "profile svg.svg")]
        hero_image_path = next((p for p in candidates if os.path.isfile(p)), hero_image_path)
    if not os.path.isfile(hero_image_path):
        raise FileNotFoundError(
            "Portrait SVG not found. Put 'Profile svg.svg' inside this project's assets folder: " + OUT
        )
    with open(hero_image_path, "r", encoding="utf-8") as f:
        uri = "data:image/svg+xml;base64," + base64.b64encode(f.read().encode("utf-8")).decode("utf-8")
    pw, ph = 470, 470
    s.add(f'<image href="{uri}" x="{1240 - pw}" y="{H - ph + 40}" width="{pw}" height="{ph}" mask="url(#photoMask)"/>')

    # Floating skill chips: frosted white pills with a blue icon.
    # Layout notes (hero is 1280 x 560):
    #   * the headline/typewriter text reaches ~x 860 at y 290-335, the stat cards
    #     fill x 56-712 at y 446-526, and the face sits at roughly x 880+, y 130-420,
    #     so every chip below lives in a gap that none of those cover.
    #   * Web Development sits at the bottom, just right of the 40+ stat card (cards end
    #     at x 712), so the cards can no longer cover it.
    chips = [
        ("Figma", "figma", 745, 150, 0),                # right of the headline, left of the hair
        ("UI/UX", "uiux", 1100, 145, 1),
        ("AI Agent", "chatgpt", 685, 348, 2),           # below the typewriter line
        ("Data Analysis", "dataanalysis", 1070, 385, 3),  # right of the portrait
        ("Web Development", "webdev", 735, 478, 4),     # bottom row, just right of the stat cards
    ]
    for label, ic, x, y, d in chips:
        w = text_width(label, "geist", 600, 17) + 58
        s.add(f'<g class="float" style="animation-delay:-{d}s">'
              f'<rect x="{x}" y="{y + 5}" width="{w}" height="44" rx="22" fill="{BLUE}" fill-opacity="0.08"/>'
              f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="{WHITE}" fill-opacity="0.88" '
              f'stroke="{AZURE}" stroke-opacity="0.28"/>'
              + icon(ic, x + 16, y + 12, 20, BLUE))
        s.text(x + 44, y + 28, label, "G6", 17, NAVY)
        s.add('</g>')

    # Header: name + availability pill.
    s.text(56, 68, "SHEHNAZ RANGREZ", "M5", 17, NAVY_SOFT, spacing=2)
    s.add(f'<g><rect x="936" y="44" width="296" height="40" rx="20" fill="{WHITE}" fill-opacity="0.9" '
          f'stroke="{AZURE}" stroke-opacity="0.28"/>'
          f'<circle cx="960" cy="64" r="5" fill="{GREEN}"/><circle class="pulse" cx="960" cy="64" r="5" fill="{GREEN}"/></g>')
    s.text(976, 69, "Available for new projects", "G5", 15, NAVY)

    # Headline.
    s.add('<g class="up" style="animation-delay:.1s">')
    s.text(56, 158, "DESIGN + ENGINEERING STUDIO", "M5", 15, BLUE, spacing=3)
    s.add('</g><g class="up" style="animation-delay:.25s">')
    s.text(52, 262, "Meet", "G8", 104, NAVY, spacing=-3)
    mx = 52 + text_width("Meet ", "geist", 800, 104, -3)
    s.text(mx, 262, "Shehnaz", "G8", 104, "url(#gName)", spacing=-3)
    s.add('</g>')

    # Typewriter line: phrases cycle by animating clip-path widths.
    prefix = "I design & build "
    s.text(56, 322, prefix, "G5", 32, "#3d4f75")
    px = 56 + text_width(prefix, "geist", 500, 32)
    phrases = ["websites Designs ", "Graphic &  Visual Designs",
               "full AI web & mobile apps", "Corporate Dashboards & Reports"]
    period, slot = 16, 4
    for i, phrase in enumerate(phrases):
        widths = [text_width(phrase[:k], "geist", 600, 32) for k in range(len(phrase) + 1)]
        n = len(phrase)
        t_type, t_hold, t_del = 1.6, 3.0, 3.6  # seconds inside the 4s slot
        vals, keys = [], []
        for k in range(n + 1):
            vals.append(widths[k]); keys.append(t_type * k / n)
        vals.append(widths[n]); keys.append(t_hold)
        for k in range(n, -1, -1):
            vals.append(widths[k]); keys.append(t_hold + (t_del - t_hold) * (n - k) / n)
        vals.append(0); keys.append(period)
        kt = ";".join(f"{k / period:.4f}" for k in keys)
        vv = ";".join(f"{v:.1f}" for v in vals)
        s.defs.append(f'<clipPath id="tw{i}"><rect x="{px}" y="290" height="44" width="0">'
                      f'<animate attributeName="width" values="{vv}" keyTimes="{kt}" calcMode="discrete" '
                      f'dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect></clipPath>')
        s.add(f'<g clip-path="url(#tw{i})">')
        s.text(px, 322, phrase, "G6", 32, BLUE)
        s.add('</g>')
        cx = ";".join(f"{px + v + 3:.1f}" for v in vals)
        s.add(f'<rect x="-20" y="296" width="3" height="34" fill="{BLUE}" opacity="0">'
              f'<animate attributeName="x" values="{cx}" keyTimes="{kt}" calcMode="discrete" '
              f'dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="1;1;0;0" '
              f'keyTimes="0;{t_del / period:.4f};{t_del / period + 0.001:.4f};1" calcMode="discrete" '
              f'dur="{period}s" begin="{i * slot}s" repeatCount="indefinite"/></rect>')

    # Intro copy.
    for j, ln in enumerate(["2+ years designing and shipping websites, AI products",
                            "and Web platforms for startups and brands worldwide."]):
        s.text(56, 374 + j * 30, ln, "G4", 20, SLATE)

    # Stat cards.
    stats = [("2+", "YEARS"), ("15+", "PROJECTS"), ("12+", "HACKATHONS PARTICIPATED"), ("40+", "TEAMS")]
    for k, (n, lab) in enumerate(stats):
        x = 56 + k * 168
        s.add(f'<g class="up" style="animation-delay:{.5 + k * .12:.2f}s">')
        s.add(f'<rect x="{x}" y="452" width="152" height="80" rx="16" fill="{BLUE}" fill-opacity="0.07"/>')
        s.add(f'<rect x="{x}" y="446" width="152" height="80" rx="16" fill="{WHITE}" fill-opacity="0.92" '
              f'stroke="{AZURE}" stroke-opacity="0.22"/>')
        s.add(f'<rect x="{x + 18}" y="446" width="28" height="3" rx="1.5" fill="{BLUE}"/>')
        s.text(x + 18, 488, n, "X7", 34, NAVY_SOFT)
        if lab == "HACKATHONS PARTICIPATED":
            # Two short lines stay inside the 152px card.
            s.text(x + 18, 506, "HACKATHONS", "M5", 8.5, SLATE, spacing=1.0)
            s.text(x + 18, 519, "PARTICIPATED", "M5", 8.5, SLATE, spacing=0.7)
        else:
            s.text(x + 18, 512, lab, "M5", 11, SLATE, spacing=1.5)
        s.add('</g>')

    s.add('</g>')
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" '
          f'stroke="{AZURE}" stroke-opacity="0.25"/>')
    return s


# --------------------------------------------------------------------------
# THEMED PROFILE COMPONENTS
# --------------------------------------------------------------------------
def section(t, num, label, title, note):
    """Numbered section heading."""
    W, H = 1280, 116
    s = Svg(W, H)
    s.defs.append(f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}"/>'
                  f'<stop offset="0.35" stop-color="{SKY}" stop-opacity="0.35"/>'
                  f'<stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>')
    s.text(4, 34, f"{num} / {label}", "M5", 15, t["accent"], spacing=3)
    s.text(0, 86, title, "G8", 44, t["text"], spacing=-1)
    s.text(W - 4, 86, note, "G4", 18, t["muted"], anchor="end")
    s.add(f'<rect x="0" y="108" width="{W}" height="2" fill="url(#ln)"/>')
    return s


def card_frame(s, t, w, h, r=24):
    """Rounded card background + hairline border."""
    s.defs.append(f'<clipPath id="cf"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>')
    s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["line"]}"/>')


def chip_row(s, t, x, y, items, size=13):
    """Row of small label chips."""
    for it in items:
        w = text_width(it, "mono", 500, size) + 22
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="14" fill="{t["chip"]}"/>')
        s.text(x + 11, y + 19, it, "M5", size, t["chiptext"])
        x += w + 8
    return x


def _placeholder_art(t, w, h, accent, label, label_font, label_size, label_y, spacing):
    """Soft blue gradient artwork used when a cover image is missing."""
    return (f'<g clip-path="url(#cf)">'
            f'<rect width="{w}" height="{h}" fill="{t["card2"]}"/>'
            f'<circle cx="{w * 0.76:.0f}" cy="{h * 0.26:.0f}" r="{h * 0.47:.0f}" fill="{accent}" fill-opacity="0.18"/>'
            f'<circle cx="{w * 0.18:.0f}" cy="{h * 0.84:.0f}" r="{h * 0.36:.0f}" fill="{SKY}" fill-opacity="0.16"/>'
            f'<path d="M0 {h * 0.79:.0f} C{w * 0.25:.0f} {h * 0.58:.0f} {w * 0.5:.0f} {h * 1.02:.0f} {w} {h * 0.6:.0f}" '
            f'fill="none" stroke="{accent}" stroke-opacity="0.5" stroke-width="3"/>'
            f'<path d="M0 {h * 0.87:.0f} C{w * 0.3:.0f} {h * 0.65:.0f} {w * 0.63:.0f} {h * 1.07:.0f} {w} {h * 0.71:.0f}" '
            f'fill="none" stroke="{accent}" stroke-opacity="0.25" stroke-width="2"/></g>')


def product_card(t, name, img, tagline, chips, url_label, accent):
    """Product card: cover image, name, blurb, tags and link label."""
    W, H = 412, 560
    s = Svg(W, H)
    card_frame(s, t, W, H)

    if os.path.isfile(img):
        uri, _ = img_uri(img, 618, 464)
        s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="309" '
              f'preserveAspectRatio="xMidYMid slice"/></g>')
    else:
        s.add(_placeholder_art(t, W, 309, accent, name, "X7", 42, 165, 2))
        s.text(W / 2, 165, name, "X7", 42, t["muted"], anchor="middle", spacing=2)

    s.add(f'<rect x="0" y="309" width="{W}" height="1" fill="{t["line"]}"/>')
    s.add(f'<rect x="28" y="336" width="8" height="30" rx="4" fill="{accent}"/>')
    s.text(48, 362, name, "X7", 32, t["text"], spacing=1)
    for j, ln in enumerate(wrap(tagline, "geist", 400, 17, W - 56)[:3]):
        s.text(28, 398 + j * 25, ln, "G4", 17, t["muted"])
    chip_row(s, t, 28, 470, chips)
    s.text(28, 532, url_label, "G6", 17, t["accent"])
    s.add(f'<path d="M{W - 50} 520 l12 0 m0 0 l0 12 m0 -12 l-14 14" stroke="{t["accent"]}" '
          f'stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    return s


def service_card(t, title, desc, icons, foot):
    """Service card: icon tiles, title, description, footer link."""
    W, H = 412, 236
    s = Svg(W, H)
    card_frame(s, t, W, H, 22)
    x = 26
    for ic in icons:
        s.add(f'<rect x="{x}" y="26" width="52" height="52" rx="14" fill="{t["tile"]}" stroke="{t["line"]}"/>')
        if ic == "pen":
            s.add(raw_icon(PEN, x + 14, 40, 24, t["accent"]))
        elif ic == "coin":
            s.add(f'<circle cx="{x + 26}" cy="52" r="12" fill="none" stroke="{t["accent"]}" stroke-width="2.4"/>')
            s.text(x + 26, 58, "$", "G8", 16, t["accent"], anchor="middle")
        else:
            s.add(icon(ic, x + 14, 40, 24, t["accent"]))
        x += 62
    s.text(26, 116, title, "G6", 22, t["text"])
    for j, ln in enumerate(wrap(desc, "geist", 400, 16, W - 52)[:2]):
        s.text(26, 146 + j * 23, ln, "G4", 16, t["muted"])
    s.add(f'<rect x="26" y="188" width="{W - 52}" height="1" fill="{t["line"]}"/>')
    s.text(26, 216, foot, "M5", 13, t["accent"], spacing=1)
    s.add(f'<path d="M{W - 42} 202 l9 0 m0 0 l0 9 m0 -9 l-11 11" stroke="{t["accent"]}" '
          f'stroke-width="2" fill="none" stroke-linecap="round"/>')
    return s


def work_card(t, title, kind, img):
    """Portfolio card: preview image, title and category."""
    W, H = 412, 336
    s = Svg(W, H)
    card_frame(s, t, W, H, 22)
    if os.path.isfile(img):
        uri, _ = img_uri(img, 618, 400, crop=None)
        s.add(f'<g clip-path="url(#cf)"><image href="{uri}" x="0" y="0" width="{W}" height="266" '
              f'preserveAspectRatio="xMidYMin slice"/></g>')
    else:
        s.add(_placeholder_art(t, W, 266, t["accent"], kind, "M5", 16, 145, 2))
        s.text(W / 2, 145, kind.upper(), "M5", 16, t["muted"], anchor="middle", spacing=2)
    s.add(f'<rect x="0" y="266" width="{W}" height="1" fill="{t["line"]}"/>')
    s.text(24, 306, title, "G6", 20, t["text"])
    s.text(W - 24, 306, kind, "M5", 12, t["muted"], anchor="end", spacing=1)
    return s


def pill(t, label, ic):
    """Small social/platform link badge."""
    w = int(text_width(label, "geist", 600, 16) + 66)
    s = Svg(w, 46)
    s.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="45" rx="23" fill="{t["card"]}" stroke="{t["line"]}"/>')
    if ic == "globe":
        s.add(raw_icon(GLOBE, 18, 13, 20, t["accent"]))
    elif ic == "contra":
        s.add(f'<circle cx="28" cy="23" r="10" fill="{t["accent"]}"/>')
        s.text(28, 28, "C", "G8", 13, t["accent_text"], anchor="middle")
    else:
        s.add(icon(ic, 18, 13, 20, t["accent"]))
    s.text(46, 29, label, "G6", 16, t["text"])
    return s


def now_strip(t):
    """'Now' availability strip."""
    W, H = 1280, 76
    s = Svg(W, H)
    s.css.append('.pulse{animation:pulse 2s ease-out infinite;transform-origin:center;transform-box:fill-box}'
                 '@keyframes pulse{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}')
    s.defs.append(f'<linearGradient id="nb" x1="0" x2="1"><stop offset="0" stop-color="{BLUE_DEEP}"/>'
                  f'<stop offset="1" stop-color="{AZURE}"/></linearGradient>')
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="38" fill="{t["card"]}" stroke="{t["line"]}"/>')
    s.add('<rect x="14" y="14" width="96" height="48" rx="24" fill="url(#nb)"/>')
    s.text(62, 44, "NOW", "M5", 16, "#ffffff", anchor="middle", spacing=3)
    s.add(f'<circle cx="140" cy="38" r="5" fill="{GREEN}"/><circle class="pulse" cx="140" cy="38" r="5" fill="{GREEN}"/>')
    msg = "Shipping SYVO, a personal AI agent, in private pilot. Open for Framer, AI and Web3 projects."
    s.text(160, 44, msg, "G5", 18, t["text"])
    return s


def stack(t):
    """Scrolling technology-stack strip."""
    W, H = 1280, 150
    names = [("figma", "Figma"), ("framer", "Framer"), ("react", "React"), ("nextdotjs", "Next.js"),
             ("typescript", "TypeScript"), ("tailwindcss", "Tailwind"), ("flutter", "Flutter"),
             ("nodedotjs", "Node.js"), ("python", "Python"), ("supabase", "Supabase"), ("firebase", "Firebase"),
             ("openai", "OpenAI"), ("claude", "Claude"), ("n8n", "n8n"), ("solidity", "Solidity"),
             ("ethereum", "Ethereum"), ("solana", "Solana"), ("wordpress", "WordPress"), ("shopify", "Shopify")]
    step = 132
    span = step * len(names)
    s = Svg(W, H)
    s.defs.append(f'<clipPath id="sc"><rect width="{W}" height="{H}" rx="24"/></clipPath>'
                  f'<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{t["card"]}"/>'
                  f'<stop offset="0.07" stop-color="{t["card"]}" stop-opacity="0"/>'
                  f'<stop offset="0.93" stop-color="{t["card"]}" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="{t["card"]}"/></linearGradient>')
    s.css.append(f'.mq{{animation:mq 38s linear infinite}}'
                 f'@keyframes mq{{from{{transform:translateX(0)}}to{{transform:translateX(-{span}px)}}}}')
    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="{t["card"]}" stroke="{t["line"]}"/>')
    s.add('<g clip-path="url(#sc)"><g class="mq">')
    for rep in range(2):
        for k, (ic, lab) in enumerate(names):
            x = 30 + rep * span + k * step
            s.add(f'<rect x="{x}" y="26" width="64" height="64" rx="18" fill="{t["tile"]}" stroke="{t["line"]}"/>')
            s.add(icon(ic, x + 18, 44, 28, t["text"]))
            s.text(x + 32, 120, lab, "M5", 13, t["muted"], anchor="middle")
    s.add('</g></g>')
    s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#edge)"/>')
    return s


# --------------------------------------------------------------------------
# CALL-TO-ACTION BANNER  (shared; same airy white + blue look as the hero)
# Animation timeline:
#   0.0s  eyebrow + name fade up
#   0.5s  "Let's build it together." types out with a cursor (about 2s)
#   2.5s  services line fades up, contact buttons pop in one by one
#   after the buttons float gently, pulse a soft ring and get a shine sweep
# --------------------------------------------------------------------------
def cta():
    W, H = 1280, 300
    s = Svg(W, H)
    s.defs.append(f'''<clipPath id="cc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WHITE}"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
<radialGradient id="ca" cx="0.14" cy="0.02" r="0.78"><stop offset="0" stop-color="{SKY}" stop-opacity="0.50"/>
 <stop offset="0.5" stop-color="{SKY_200}" stop-opacity="0.30"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
<radialGradient id="cb" cx="0.88" cy="1.05" r="0.62"><stop offset="0" stop-color="{AZURE}" stop-opacity="0.42"/>
 <stop offset="0.55" stop-color="{AZURE}" stop-opacity="0.12"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
<pattern id="cg" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="{BLUE}" stroke-opacity="0.07"/></pattern>
<linearGradient id="cn" x1="0" x2="1"><stop offset="0" stop-color="{BLUE_DEEP}"/><stop offset="0.55" stop-color="{AZURE}"/><stop offset="1" stop-color="{SKY}"/></linearGradient>
<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{SKY}" stop-opacity="0"/><stop offset="0.5" stop-color="{SKY}" stop-opacity="0.5"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>''')

    s.css.append('''
.up{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.pop{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .85s cubic-bezier(.2,.9,.3,1.2) forwards}
@keyframes pop{from{opacity:0;transform:translateY(24px) scale(.88)}to{opacity:1;transform:none}}
.bob{animation:bob 5s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.ring{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 3.4s ease-out infinite}
@keyframes ring{0%{opacity:.6;transform:scale(1)}70%,100%{opacity:0;transform:scale(1.26,1.7)}}
.shine{animation:shine 5.5s ease-in-out infinite}
@keyframes shine{0%{transform:translateX(0)}26%,100%{transform:translateX(260px)}}
''')

    # Background, grid, glows and rings (identical to the hero).
    s.add(f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="url(#cbg)"/>'
          f'<rect width="{W}" height="{H}" fill="url(#cg)"/><rect width="{W}" height="{H}" fill="url(#ca)"/>'
          f'<rect width="{W}" height="{H}" fill="url(#cb)"/>'
          f'<circle cx="1120" cy="60" r="150" fill="none" stroke="{AZURE}" stroke-opacity="0.18" stroke-dasharray="3 9"/>'
          f'<circle cx="1120" cy="60" r="210" fill="none" stroke="{SKY}" stroke-opacity="0.16"/></g>')

    s.add('<g class="up" style="animation-delay:.05s">')
    s.text(64, 92, "HAVE A PROJECT IN MIND?", "M5", 16, BLUE, spacing=3)
    s.add('</g><g class="up" style="animation-delay:.25s">')
    s.text(1216, 92, "SHEHNAZ RANGREZ", "M5", 15, NAVY_SOFT, anchor="end")
    s.add('</g>')

    # ---- Typing effect for the headline ---------------------------------
    # A clip rectangle grows one character at a time (discrete steps) and a
    # cursor follows its edge, then blinks a few times and disappears.
    part_a, part_b = "Let's build it ", "together."
    hf = ("geist", 800, 72, -2)
    full = part_a + part_b
    n = len(full)

    def reach(k):  # pixel width of the first k characters of the headline
        if k <= len(part_a):
            return text_width(part_a[:k], *hf)
        return text_width(part_a, *hf) + text_width(part_b[:k - len(part_a)], *hf)

    widths = [reach(k) for k in range(n + 1)]
    # Human-looking rhythm: slight speed variation, longer pause after each word.
    steps = [1 + 0.5 * ((k * 5) % 7) / 6 + (0.9 if full[k] == " " else 0) for k in range(n)]
    total = sum(steps) + 1.0
    keys, acc = [0.0], 0.0
    for st in steps:
        acc += st
        keys.append(acc / total)
    keys.append(1.0)
    kt = ";".join(f"{k:.4f}" for k in keys)

    T0, DUR = 0.5, 2.0   # start delay and typing duration (seconds)
    clip_vals = [0.0] + [w + 6 for w in widths[1:]] + [widths[n] + 6]
    cur_vals = [60 + w + 5 for w in widths] + [60 + widths[n] + 5]
    s.defs.append(
        f'<clipPath id="ctw"><rect x="60" y="96" width="0" height="116">'
        f'<animate attributeName="width" values="{";".join(f"{v:.1f}" for v in clip_vals)}" keyTimes="{kt}" '
        f'calcMode="discrete" dur="{DUR}s" begin="{T0}s" fill="freeze"/></rect></clipPath>')

    s.add('<g clip-path="url(#ctw)">')
    s.text(60, 168, part_a.rstrip() + " ", "G8", 72, NAVY, spacing=-2)
    s.text(60 + text_width(part_a, *hf), 168, part_b, "G8", 72, "url(#cn)", spacing=-2)
    s.add('</g>')

    s.add(f'<rect x="60" y="114" width="4" height="62" rx="2" fill="{BLUE}" opacity="0">'
          f'<set attributeName="opacity" to="1" begin="{T0}s" fill="freeze"/>'
          f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cur_vals)}" keyTimes="{kt}" '
          f'calcMode="discrete" dur="{DUR}s" begin="{T0}s" fill="freeze"/>'
          f'<animate attributeName="opacity" values="1;0" keyTimes="0;0.5" calcMode="discrete" '
          f'dur="0.9s" begin="{T0 + DUR}s" repeatCount="5" fill="freeze"/></rect>')

    # Services line fades in once the headline is typed.
    d0 = T0 + DUR + 0.1
    s.add(f'<g class="up" style="animation-delay:{d0:.2f}s">')
    s.text(64, 222, "Web design  \u2022  UI/UX  \u2022  AI agents  \u2022  Data analysis  \u2022  Web development",
           "G4", 18, SLATE)
    s.add('</g>')

    # ---- Animated contact buttons ---------------------------------------
    contacts = [
        ("LinkedIn", "linkedin", LINKEDIN_URL, 770),
        ("Gmail", "gmail", f"mailto:{GMAIL_ADDRESS}", 925),
        ("GitHub", "github", GITHUB_URL, 1080),
    ]
    for i, (label, ic, href, x) in enumerate(contacts):
        d = d0 + i * 0.18          # staggered pop-in
        bx = x - 80                # shine bar starts off the left edge of the pill
        s.defs.append(f'<clipPath id="pc{i}"><rect x="{x}" y="194" width="140" height="58" rx="29"/></clipPath>')
        s.add(f'<g class="pop" style="animation-delay:{d:.2f}s"><g class="bob" style="animation-delay:-{i * 1.4:.1f}s">')
        # Anchors work when cta.svg is opened directly; see social-links.md for
        # clickable Markdown wrappers when the SVG is embedded in a GitHub README.
        s.add(f'<a href="{escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">')
        s.add(f'<rect class="ring" x="{x}" y="194" width="140" height="58" rx="29" fill="none" '
              f'stroke="{AZURE}" stroke-width="1.5" style="animation-delay:{d + 0.9:.2f}s"/>')
        s.add(f'<rect x="{x}" y="199" width="140" height="58" rx="29" fill="{BLUE}" fill-opacity="0.08"/>')
        s.add(f'<rect x="{x}" y="194" width="140" height="58" rx="29" fill="{WHITE}" fill-opacity="0.92" '
              f'stroke="{AZURE}" stroke-opacity="0.28"/>')
        s.add(f'<g clip-path="url(#pc{i})"><polygon class="shine" fill="url(#sh)" '
              f'points="{bx + 24},194 {bx + 60},194 {bx + 36},252 {bx},252" '
              f'style="animation-delay:{d + 1.4 + i * 0.45:.2f}s"/></g>')
        s.add(icon(ic, x + 17, 212, 22, BLUE))
        s.text(x + 49, 230, label, "G6", 17, NAVY)
        s.add('</a></g></g>')

    s.add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" '
          f'stroke="{AZURE}" stroke-opacity="0.25"/>')
    return s


def social_badge(label, icon_name):
    """Individual contact badge (white with blue accents); Markdown wraps it in a real link."""
    w, h = 160, 48
    b = Svg(w, h)
    b.add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="24" fill="{WHITE}" '
          f'stroke="{AZURE}" stroke-opacity="0.35"/>')
    b.add(icon(icon_name, 15, 13, 22, BLUE))
    b.text(48, 30, label, "G6", 15, NAVY)
    return b


def write_social_markdown():
    """Write README-ready links using paths relative to the detected README."""
    readme_candidates = [os.path.join(ROOT, "README.md"), os.path.join(PARENT_DIR, "README.md")]
    readme_path = next((p for p in readme_candidates if os.path.isfile(p)), None)
    readme_dir = os.path.dirname(readme_path) if readme_path else ROOT
    asset_prefix = os.path.relpath(OUT, readme_dir).replace(os.sep, "/").rstrip("/")
    if asset_prefix == ".":
        asset_prefix = "assets"

    rows = [
        f'[![LinkedIn]({asset_prefix}/social/linkedin.svg)]({https://www.linkedin.com/in/shehnazrangrez/})',
        f'[![Gmail]({asset_prefix}/social/gmail.svg)](mailto:{mailto:shehnazrangrez2006@gmail.com})',
        f'[![GitHub]({asset_prefix}/social/github.svg)]({https://github.com/Shehnaz-R})',
    ]
    path = os.path.join(OUT, "social-links.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    return path


# --------------------------------------------------------------------------
# PROFILE CONTENT DATA: edit these lists to change what appears in the README
# --------------------------------------------------------------------------
LK = f"{DOCS}/launch-kit"
BH = f"{CP}/behance"

# (slug, display name, image path, description, tags, link text, accent colour)
PRODUCTS = [
    ("xoxi", "XOXI", f"{CP}/products/xoxi-cover.jpg",
     "Your CV becomes a verified portfolio you can apply with. AI match scores for the teams hiring.",
     ["Web", "iOS", "Android", "AI"], "Visit xoxi.me", BLUE),
    ("syvo", "SYVO", f"{CP}/products/syvo-cover.jpg",
     "A personal AI agent. Ask in plain words and it finds, books or sells for you, then waits for your OK.",
     ["AI agent", "Flutter", "Web"], "Visit syvo.si", "#0ea5e9"),
    ("lovii", "LOVII", f"{CP}/products/lovii-cover.jpg",
     "A private journal for couples. One short note a day, drawn by AI as an illustrated card.",
     ["iOS", "Android", "AI art"], "Visit lovii.app", INDIGO),
]

# (slug, title, description, icon names)
SERVICES = [
    ("framer", "Framer websites", "Responsive sites with real scroll motion, CMS and SEO, from Figma or from scratch.", ["framer"]),
    ("agents", "AI agents & automations", "Chatbots, n8n and Make workflows and custom agents that do real work.", ["n8n", "openai"]),
    ("aiapps", "Full AI web & mobile apps", "Website, web app and iOS + Android apps, designed and built end to end.", ["flutter", "react"]),
    ("uiux", "UI/UX design", "Websites, dashboards and mobile apps in Figma with clickable prototypes.", ["figma"]),
    ("wpshop", "WordPress & Shopify", "Business sites and online stores that are easy to run after launch.", ["wordpress", "shopify"]),
    ("nftweb", "NFT & Web3 websites", "Marketplaces, mint pages and landing pages that make wallets feel simple.", ["ethereum"]),
    ("dapp", "Smart contracts & dApps", "NFT minting dApps and contracts on Ethereum, Polygon and Solana.", ["solidity", "solana"]),
    ("memecoin", "Meme coin websites", "Loud, fun coin sites with tokenomics, presale pages and buy flows.", ["coin", "solana"]),
    ("brand", "Logo & brand identity", "Minimal logos and brand kits for startups, products and Web3 projects.", ["pen"]),
]

# (slug, project name, category label)
WORK = [
    ("medelz", "Medelz", "MUSIC PLATFORM"), ("smartforum", "Smart Forum", "IT SERVICES"),
    ("satholler", "SatHoller", "NFT AUCTIONS"), ("metaadsfirm", "MetaAdsFirm", "WEB3 AGENCY"),
    ("blackmomento", "The Black Momento", "E-COMMERCE"), ("blckbuster", "Blckbuster", "WEB3 MARKETPLACE"),
]

# (slug, visible label, icon filename)
PILLS = [("site", "Website", "globe"), ("framer", "Framer", "framer"), ("contra", "Contra", "contra"),
         ("fiverr", "Fiverr", "fiverr"), ("x", "X", "x"), ("youtube", "YouTube", "youtube"),
         ("instagram", "Instagram", "instagram"), ("linkedin", "LinkedIn", "linkedin")]

SECTIONS = [
    ("01", "PRODUCTS", "Products I've built", "Designed, built and shipped in-house"),
    ("02", "SERVICES", "What I can do for you", "Every card opens the matching gig"),
    ("03", "SELECTED WORK", "Selected client work", "Full case studies on Behance"),
    ("04", "STACK", "Tools I ship with", "Design, code, AI and Web3"),
    ("05", "ACTIVITY", "Building in public", "Updated daily by GitHub Actions"),
]


def main():
    """Generate every shared and theme-specific SVG, then print a size summary."""
    sizes = {}
    sizes["hero.svg"] = save(hero(), "hero.svg")
    sizes["cta.svg"] = save(cta(), "cta.svg")

    for slug, label, icon_name in [("linkedin", "LinkedIn", "linkedin"),
                                   ("gmail", "Gmail", "gmail"),
                                   ("github", "GitHub", "github")]:
        sizes[f"social/{slug}"] = save(social_badge(label, icon_name), "social", f"{slug}.svg")
    write_social_markdown()

    for name, t in THEMES.items():
        sizes[f"{name}/now"] = save(now_strip(t), name, "now.svg")
        for key, label, title, note in SECTIONS:
            sizes[f"{name}/s{key}"] = save(section(t, key, label, title, note), name, f"s{key}.svg")
        for slug, nm, img, tag, chips, url, acc in PRODUCTS:
            sizes[f"{name}/p-{slug}"] = save(product_card(t, nm, img, tag, chips, url, acc), name, f"p-{slug}.svg")
        for slug, title, desc, icons in SERVICES:
            sizes[f"{name}/sv-{slug}"] = save(service_card(t, title, desc, icons, "VIEW ON FIVERR"), name, f"sv-{slug}.svg")
        for slug, title, kind in WORK:
            sizes[f"{name}/w-{slug}"] = save(work_card(t, title, kind, f"{BH}/{slug}/01.png"), name, f"w-{slug}.svg")
        for slug, label, ic in PILLS:
            sizes[f"{name}/l-{slug}"] = save(pill(t, label, ic), name, f"l-{slug}.svg")
        sizes[f"{name}/stack"] = save(stack(t), name, "stack.svg")

    total = sum(sizes.values())
    big = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    print(f"{len(sizes)} files, {total / 1e6:.2f} MB total; largest: "
          + ", ".join(f"{k} {v // 1024}KB" for k, v in big))


if __name__ == "__main__":
    main()