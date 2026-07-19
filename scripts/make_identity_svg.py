from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "identity-ascii.svg"
WIDTH, HEIGHT = 350, 300


def main() -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Animated YFA identity mark</title>
<desc id="desc">A crisp geometric YFA mark assembles inside a terminal window.</desc>
<defs>
  <linearGradient id="violet" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#d39be8"/>
    <stop offset="1" stop-color="#a85cc7"/>
  </linearGradient>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="grid" width="18" height="18" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#6d4c7d" opacity=".2"/>
  </pattern>
</defs>
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .piece {{ opacity:0; transform-box:fill-box; transform-origin:center; animation:assemble .52s cubic-bezier(.2,.9,.2,1.15) forwards; }}
  .top {{ animation-delay:.2s }} .stem {{ animation-delay:.42s }} .cross {{ animation-delay:.64s }}
  .left {{ animation-delay:.82s }} .center {{ animation-delay:.94s }} .right {{ animation-delay:1.06s }}
  .scan {{ animation:scan 2.8s ease-in-out 1.2s infinite; }}
  @keyframes assemble {{ from {{ opacity:0; transform:scale(.68) translateY(7px); }} to {{ opacity:1; transform:scale(1) translateY(0); }} }}
  @keyframes scan {{ 0%,100% {{ opacity:0; transform:translateY(0); }} 15% {{ opacity:.48; }} 70% {{ opacity:.18; }} 90% {{ opacity:0; transform:translateY(202px); }} }}
  @media (prefers-reduced-motion:reduce) {{ .piece {{ opacity:1; animation:none; }} .scan {{ display:none; }} }}
</style>
<rect width="348" height="298" x="1" y="1" rx="16" fill="#100b16" stroke="#3d2a49"/>
<rect x="12" y="38" width="326" height="248" rx="11" fill="url(#grid)"/>
<circle cx="20" cy="20" r="4.5" fill="#ff6b81"/><circle cx="36" cy="20" r="4.5" fill="#f6c85f"/><circle cx="52" cy="20" r="4.5" fill="#65d6a6"/>
<text x="67" y="24" font-size="10" fill="#a993b8">identity.svg</text>
<g filter="url(#glow)">
  <rect class="piece top" x="81" y="54" width="188" height="38" rx="3" fill="url(#violet)"/>
  <rect class="piece stem" x="145" y="119" width="60" height="66" rx="3" fill="url(#violet)"/>
  <rect class="piece cross" x="81" y="184" width="188" height="48" rx="3" fill="url(#violet)"/>
  <rect class="piece left" x="29" y="231" width="52" height="49" rx="3" fill="url(#violet)"/>
  <rect class="piece center" x="145" y="231" width="60" height="49" rx="3" fill="url(#violet)"/>
  <rect class="piece right" x="269" y="231" width="52" height="49" rx="3" fill="url(#violet)"/>
</g>
<rect class="scan" x="29" y="51" width="292" height="2" rx="1" fill="#f4dfff" opacity="0"/>
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
