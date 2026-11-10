import glob, os, subprocess, sys, numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw
from rembg import remove, new_session
from playwright.sync_api import sync_playwright

def sky_bg(W,H,cx,top,el='air',seed=7):
    rng=np.random.default_rng(seed)
    P={'fire':((70,18,12),(210,95,35)),'water':((6,42,64),(40,150,170)),'air':((62,52,110),(175,150,215)),'earth':((22,46,30),(185,140,60))}
    tc,hc=P[el]
    y=np.clip(np.arange(H)/1000,0,1)[:,None,None]
    sky=np.array(tc)*(1-y)+np.array([11,15,31])*y; sky=np.broadcast_to(sky,(H,W,3)).copy()
    yy,xx=np.mgrid[0:H,0:W]; halo=np.exp(-((np.sqrt((xx-cx)**2+(yy-top-260)**2))/430)**2)[...,None]*np.array(hc)*0.9
    def noise(sc):
        a=rng.random((H//sc+2,W//sc+2)).astype(np.float32); return np.asarray(Image.fromarray((a*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255
    L=np.zeros((H,W),np.float32); col=np.array([255,250,235])
    if el=='air':
        cl=np.clip(noise(160)*0.6+noise(60)*0.4-0.55,0,1)*2.2; sky=sky+cl[...,None]*np.array([120,110,160])*0.5
        n=900; L[rng.integers(0,1000,n),rng.integers(0,W,n)]=rng.uniform(.3,1,n)**3
    if el=='water':
        img=Image.new('L',(W,H)); d=ImageDraw.Draw(img)
        for _ in range(28):
            x,y0,r=rng.integers(0,W),rng.integers(0,1000),rng.integers(20,90); d.ellipse((x-r,y0-r,x+r,y0+r),fill=int(rng.integers(25,70)))
        L=np.asarray(img.filter(ImageFilter.GaussianBlur(6)),np.float32)/255; col=np.array([160,230,240])
        wv=(np.sin(yy/38+np.sin(xx/170)*2.2)*0.5+0.5)**8*0.18*(yy<1000); sky=sky+wv[...,None]*np.array([90,190,210])
    if el=='fire':
        img=Image.new('L',(W,H)); d=ImageDraw.Draw(img)
        for _ in range(160):
            x,y0=rng.integers(0,W),rng.integers(150,1050); l=rng.integers(6,26); d.line((x,y0,x+rng.integers(-4,5),y0-l),fill=int(rng.integers(120,255)),width=int(rng.integers(2,4)))
        L=np.asarray(img.filter(ImageFilter.GaussianBlur(1.3)),np.float32)/255*1.5; col=np.array([255,170,70])
        sm=np.clip(noise(140)-0.5,0,1)*1.6*(yy<1000); sky=sky+sm[...,None]*np.array([120,40,10])
    if el=='earth':
        img=Image.new('L',(W,H)); d=ImageDraw.Draw(img)
        for _ in range(5):
            pts=[(int(rng.integers(0,W)),int(rng.integers(0,950)))]
            for _ in range(rng.integers(3,6)): pts.append((int(np.clip(pts[-1][0]+rng.integers(-220,220),0,W)),int(np.clip(pts[-1][1]+rng.integers(-160,160),0,950))))
            d.line(pts,fill=70,width=2)
            for p_ in pts: d.ellipse((p_[0]-5,p_[1]-5,p_[0]+5,p_[1]+5),fill=230)
        L=np.asarray(img.filter(ImageFilter.GaussianBlur(1.2)),np.float32)/255; col=np.array([245,215,150])
        gr=(noise(3)-0.5)*14; sky=sky+gr[...,None]
        n=500; st=np.zeros((H,W),np.float32); st[rng.integers(0,1000,n),rng.integers(0,W,n)]=rng.uniform(.3,1,n)**3; L=np.maximum(L,np.asarray(Image.fromarray((st*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1)),np.float32)/255*3)
    if el=='air': L=np.asarray(Image.fromarray((np.clip(L,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1)),np.float32)/255*3
    fadeL=1-np.clip(halo.mean(-1,keepdims=True)/110,0,0.8)
    out=sky+halo+np.clip(L,0,1.5)[...,None]*col*fadeL
    w=np.clip((yy-720)/300,0,1)[...,None]**1.5
    return np.clip(out*(1-w)+np.array([11,15,31])*w,0,255)

C="/home/claude/astroloca-media/tools/cards"; F=C+"/node_modules/@fontsource"
V={7:("water","Why do you feel lonely in your <em>relationship?</em>"),
8:("earth","Why do you dismiss what you're <em>naturally good at?</em>"),
9:("fire","Fight, flight or freeze: what does <em>your Mars</em> say?"),
10:("air","Is zodiac sign compatibility <em>a myth?</em>"),
11:("earth","Burnout or the wrong path: <em>how can you tell?</em>"),
12:("water","Why are you always <em>the strong one?</em>"),
13:("fire","Why can't you relax, even <em>on holiday?</em>"),
14:("earth","Is fear a sign you're on <em>the right path?</em>"),
15:("water","Are you using spirituality to <em>avoid your feelings?</em>"),
16:("air","Why do you always feel <em>misunderstood?</em>")}
d='/home/claude/haar/'
FC=cv2.CascadeClassifier(d+'haarcascade_frontalface_default.xml');E=cv2.CascadeClassifier(d+'haarcascade_eye_tree_eyeglasses.xml');S=cv2.CascadeClassifier(d+'haarcascade_smile.xml')
def best(n):
    os.makedirs(f'f{n:02d}',exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'v{n:02d}.mp4','-vf','fps=3','-q:v','2',f'f{n:02d}/%04d.jpg'],stdin=subprocess.DEVNULL)
    res=[]
    for f in sorted(glob.glob(f'f{n:02d}/*.jpg'))[3:]:
        g=cv2.cvtColor(cv2.imread(f),cv2.COLOR_BGR2GRAY); fs=FC.detectMultiScale(g,1.1,6,minSize=(200,200))
        if len(fs)!=1: continue
        x,y,w,h=fs[0]; face=g[y:y+h,x:x+w]
        e=min(len(E.detectMultiScale(face[:h//2],1.1,8,minSize=(w//10,w//10))),2); s=int(len(S.detectMultiScale(face[h//2:],1.7,25,minSize=(w//4,h//10)))>0)
        res.append((f,e,s,cv2.Laplacian(face,cv2.CV_64F).var(),1-abs((x+w/2)/g.shape[1]-0.5)*2))
    m=np.percentile([r[3] for r in res],90)
    return max(res,key=lambda r:r[1]+r[2]*0.8+min(r[3]/m,1)+r[4]*0.5)[0]
os.chdir('/home/claude/b4')
sess=new_session('u2net_human_seg'); os.makedirs('out',exist_ok=True)
with sync_playwright() as p:
    br=p.chromium.launch();pg=br.new_page(viewport={'width':1080,'height':1920})
    for n,(el,txt) in V.items():
        f=best(n)
        fr=Image.open(f).convert('RGB').resize((1620,2880),Image.LANCZOS).crop((270,778,1350,2698))
        m=np.asarray(remove(fr,session=sess,only_mask=True).filter(ImageFilter.GaussianBlur(1.5)),np.float32)/255
        ys,xs=np.where(m[:950]>0.5)
        sky=sky_bg(1080,1920,xs.mean(),ys.min(),el,seed=n)
        comp=np.asarray(fr,np.float32)*m[...,None]+sky*(1-m[...,None])
        Image.fromarray(comp.astype(np.uint8)).save(f'out/ph{n:02d}.jpg',quality=95)
        size=104 if len(txt)<60 else 92
        html=f'''<!DOCTYPE html><html><head><style>
@font-face{{font-family:Mc;src:url(file://{F}/marcellus/files/marcellus-latin-400-normal.woff2)}}
*{{margin:0;box-sizing:border-box}}body{{width:1080px;height:1920px;position:relative;overflow:hidden;background:#0B0F1F}}
.ph{{position:absolute;inset:0;background:url(file:///home/claude/b4/out/ph{n:02d}.jpg) 0 0/1080px 1920px}}
.fade{{position:absolute;left:0;right:0;bottom:0;height:970px;background:linear-gradient(to bottom,rgba(11,15,31,0) 0%,rgba(11,15,31,.85) 18%,#0B0F1F 25%)}}
.band{{position:absolute;left:70px;right:70px;top:1130px;padding:56px 60px;border-radius:36px;transform:rotate(-1.5deg);background:url(file://{C}/parchment.jpg) center/cover;box-shadow:0 30px 60px rgba(0,0,0,.6)}}
.band:before{{content:"";position:absolute;inset:0;border-radius:36px;background:rgba(255,246,228,.35)}}
.t{{position:relative;font-family:Mc;font-size:{size}px;line-height:1.08;color:#1F3B4D}}.t em{{font-style:normal;color:#C4572E}}
.logo{{position:absolute;bottom:80px;left:50%;transform:translateX(-50%);height:100px}}
</style></head><body><div class="ph"></div><div class="fade"></div><div class="band"><div class="t">{txt}</div></div><img class="logo" src="file://{C}/logo_cream.png"></body></html>'''
        open('c.html','w').write(html); pg.goto('file:///home/claude/b4/c.html'); pg.wait_for_timeout(400)
        pg.screenshot(path=f'out/V{n:02d}_cover.jpg',type='jpeg',quality=90); print(n,f,flush=True)
    br.close()
w,h=270,480; s=Image.new('RGB',(w*5+40,h*2+10),'white')
for i,n in enumerate(V):
    im=Image.open(f'out/V{n:02d}_cover.jpg').resize((w,h)); ImageDraw.Draw(im).text((8,8),str(n),fill='white'); s.paste(im,((i%5)*(w+10),(i//5)*(h+10)))
s.save('/home/claude/covers_b4_v7-16.jpg',quality=86)
