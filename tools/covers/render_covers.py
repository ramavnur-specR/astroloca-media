import subprocess, json
from playwright.sync_api import sync_playwright
C="/home/claude/astroloca-media/tools/cards"; F=C+"/node_modules/@fontsource"
V={5:(9,"Why can't you decide without <em>being sure?</em>"),
6:(13,"Why do you always fall for the <em>wrong type?</em>"),
7:(9,"Why do you feel lonely in your <em>relationship?</em>"),
8:(2,"Why do you dismiss what you're <em>naturally good at?</em>"),
9:(13,"Fight, flight or freeze: what does <em>your Mars</em> say?"),
10:(9,"Is zodiac sign compatibility <em>a myth?</em>"),
11:(9,"Burnout or the wrong path: <em>how can you tell?</em>"),
12:(5,"Why are you always <em>the strong one?</em>"),
13:(2,"Why can't you relax, even <em>on holiday?</em>"),
14:(13,"Is fear a sign you're on <em>the right path?</em>"),
15:(13,"Are you using spirituality to <em>avoid your feelings?</em>"),
16:(5,"Why do you always feel <em>misunderstood?</em>")}
def page(n,txt):
    size=104 if len(txt)<60 else 92
    return f'''<!DOCTYPE html><html><head><style>
@font-face{{font-family:Mc;src:url(file://{F}/marcellus/files/marcellus-latin-400-normal.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;position:relative;overflow:hidden;background:#0B0F1F}}
.ph{{position:absolute;inset:0;background:url(file:///home/claude/cover/face{n:02d}.jpg) 50% 81%/auto 150%}}
.fade{{position:absolute;left:0;right:0;bottom:0;height:970px;background:linear-gradient(to bottom,rgba(11,15,31,0) 0%,rgba(11,15,31,.85) 18%,#0B0F1F 25%)}}
.band{{position:absolute;left:70px;right:70px;top:1130px;padding:56px 60px;border-radius:36px;transform:rotate(-1.5deg);background:url(file://{C}/parchment.jpg) center/cover;box-shadow:0 30px 60px rgba(0,0,0,.6)}}
.band:before{{content:"";position:absolute;inset:0;border-radius:36px;background:rgba(255,246,228,.35)}}
.t{{position:relative;font-family:Mc;font-size:{size}px;line-height:1.08;color:#1F3B4D}}
.t em{{font-style:normal;color:#C4572E}}
.logo{{position:absolute;bottom:90px;left:50%;transform:translateX(-50%);height:70px}}
</style></head><body><div class="ph"></div><div class="fade"></div><div class="band"><div class="t">{txt}</div></div><img class="logo" src="file://{C}/logo_cream.png"></body></html>'''
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1920})
    for n,(t,txt) in V.items():
        subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t),"-i",f"v{n:02d}.mp4","-frames:v","1","-q:v","2",f"face{n:02d}.jpg"],stdin=subprocess.DEVNULL)
        open('c.html','w').write(page(n,txt)); pg.goto('file:///home/claude/cover/c.html'); pg.wait_for_timeout(500)
        pg.screenshot(path=f'V{n:02d}_cover.jpg',type='jpeg',quality=90)
    b.close()
