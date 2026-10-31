import sys, json, pathlib
from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).resolve().parent
F = D / "node_modules/@fontsource"
INK = "#1F3B4D"
EL = {  # muted element accents that sit with the parchment + navy brand
    "fire":  "#C4572E",
    "earth": "#6E7B3B",
    "air":   "#4F86B0",
    "water": "#1E7A78",
}
SYM = {
    "fire":  '<path d="M20 4 L36 34 L4 34 Z"/>',
    "air":   '<path d="M20 4 L36 34 L4 34 Z"/><line x1="9" y1="22" x2="31" y2="22"/>',
    "water": '<path d="M4 6 L36 6 L20 36 Z"/>',
    "earth": '<path d="M4 6 L36 6 L20 36 Z"/><line x1="9" y1="18" x2="31" y2="18"/>',
}

def stars():
    import random
    random.seed(7)
    out = []
    for _ in range(140):
        x, y = random.randint(0, 1080), random.randint(0, 1350)
        r = random.choice([1, 1, 1, 1.5, 2, 2.5])
        o = random.uniform(.35, .95)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFF3D6" opacity="{o:.2f}"/>')
    for x, y, s in [(70, 70, 26), (1000, 1280, 22), (1010, 90, 14), (60, 1290, 12)]:
        out.append(f'<text x="{x}" y="{y}" font-size="{s}" fill="#F2C76B" opacity=".9">✦</text>')
    return "".join(out)

def html(c):
    acc = EL[c["element"]]
    practice = c["kind"] == "practice"
    label = "TRY THIS" if practice else "ASK YOURSELF"
    check = ('<div class="check"><span class="box"></span>tried it</div>' if practice
             else '<div class="check">save it for the day you need it</div>')
    return f"""<!DOCTYPE html><html><head><style>
@font-face{{font-family:Mc;src:url(file://{F}/marcellus/files/marcellus-latin-400-normal.woff2)}}
@font-face{{font-family:Sm;src:url(file://{F}/space-mono/files/space-mono-latin-700-normal.woff2);font-weight:700}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;position:relative;
 background:radial-gradient(90% 70% at 30% 15%,#2A3F63 0%,#141B33 55%,#0B0F1F 100%)}}
.sky{{position:absolute;inset:0}}
.card{{position:absolute;left:96px;top:120px;width:888px;height:1110px;border-radius:40px;transform:rotate(-1.5deg);
 background:url(file://{D}/parchment.jpg) center/cover;box-shadow:0 34px 70px rgba(0,0,0,.55);padding:68px 74px}}
.card:before{{content:"";position:absolute;inset:0;border-radius:40px;background:rgba(255,246,228,.35)}}
.card:after{{content:"";position:absolute;inset:22px;border:2px solid {INK};border-radius:28px;opacity:.45}}
.top{{position:relative;display:flex;justify-content:space-between;align-items:center;font-family:Sm;font-weight:700;font-size:30px;color:{INK};letter-spacing:2px;z-index:2}}
.pill{{background:{acc};color:#FFF4E4;padding:12px 26px;border-radius:999px;font-family:Mc;font-size:28px;letter-spacing:5px}}
.line{{position:absolute;left:74px;right:74px;top:290px;bottom:340px;display:flex;align-items:center;z-index:2;
 font-family:Mc;font-size:{c.get('size',94)}px;line-height:1.12;color:{INK}}}
.line em{{font-style:normal;color:{acc}}}
.check{{position:absolute;left:74px;bottom:200px;font-family:Mc;font-size:40px;color:{INK};display:flex;align-items:center;gap:22px;z-index:2}}
.box{{width:46px;height:46px;border:4px solid {INK};border-radius:10px;display:inline-block}}
.foot{{position:absolute;left:74px;right:74px;bottom:70px;display:flex;justify-content:space-between;align-items:center;z-index:2;
 font-family:Mc;font-size:26px;letter-spacing:6px;color:{INK}}}
.el{{display:flex;align-items:center;gap:14px}}
.el svg{{width:40px;height:40px;fill:none;stroke:{acc};stroke-width:4;stroke-linejoin:round}}
.logo{{height:66px}}
.sticker{{position:absolute;right:44px;bottom:270px;width:240px;height:240px;transform:rotate(14deg);filter:drop-shadow(0 12px 16px rgba(0,0,0,.45));z-index:3}}
</style></head><body>
<svg class="sky" viewBox="0 0 1080 1350">{stars()}</svg>
<div class="card">
 <div class="top"><span>No. {c['num']:02d}</span><span class="pill">{label}</span></div>
 <div class="line"><div>{c['line']}</div></div>
 {check}
 <div class="foot"><span class="el"><svg viewBox="0 0 40 40">{SYM[c['element']]}</svg>{c['element'].upper()}</span><img class="logo" src="file://{D}/logo_navy.png"></div>
</div>
<svg class="sticker" viewBox="0 0 240 240">
 <circle cx="120" cy="120" r="114" fill="#FFF1D8"/>
 <circle cx="120" cy="120" r="108" fill="none" stroke="{INK}" stroke-width="3" opacity=".5"/>
 <circle cx="120" cy="120" r="58" fill="{acc}"/>
 <ellipse cx="120" cy="120" rx="102" ry="28" fill="none" stroke="{INK}" stroke-width="8" transform="rotate(-20 120 120)"/>
 <path d="M62 120 a58 58 0 0 1 116 0" fill="{acc}" transform="rotate(-20 120 120)"/>
 <circle cx="100" cy="100" r="11" fill="#FFF1D8" opacity=".5"/>
</svg>
</body></html>"""

cards = json.loads(sys.argv[1])
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for c in cards:
        (D / "t.html").write_text(html(c)); pg.goto(f"file://{D}/t.html"); pg.wait_for_timeout(600)
        pg.screenshot(path=str(D / c["out"]))
    b.close()
print("ok")
