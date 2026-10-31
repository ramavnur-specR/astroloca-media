import json, re, subprocess, sys
src, toks_f, out = sys.argv[1], sys.argv[2], sys.argv[3]
fixes = json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
PAD=0.12; MINSIL=0.35
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",src]))
toks=json.load(open(toks_f)); words=[]
for t,ts in toks:
    if t.startswith(" ") or not words: words.append([ts,t.strip()])
    else: words[-1][1]+=t
for i,w in enumerate(words):
    nxt = words[i+1][0] if i+1<len(words) else w[0]+0.5
    w.append(min(nxt, w[0]+0.6))
log=subprocess.run(["ffmpeg","-hide_banner","-i",src,"-af",f"silencedetect=noise=-35dB:d={MINSIL}","-f","null","-"],capture_output=True,text=True).stderr
ss=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",log)]; se=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",log)]
sil=list(zip(ss,se+[dur]*(len(ss)-len(se))))
first=words[0][0]; last=words[-1][2]
keep=[]; cur=max(0,first-PAD)
for a,b in sil:
    if b<=cur or a>=last: continue
    if a-cur>0: keep.append((cur,a+PAD))
    cur=b-PAD
keep.append((cur,min(dur,last+0.4)))
keep=[(round(a*30)/30+0.0005,round(b*30)/30-0.0005) for a,b in keep if b-a>0.05]
def remap(t):
    acc=0
    for a,b in keep:
        if t<a: return acc
        if t<=b: return acc+t-a
        acc+=b-a
    return acc
newdur=sum(b-a for a,b in keep)
caps=[];cur=[]
for w in words:
    cur.append(w)
    if len(cur)>=4 or re.search(r"[.,?!]$",w[1]): caps.append(cur);cur=[]
if cur: caps.append(cur)
def ts(t): h=int(t//3600);m=int(t%3600//60);s=t%60;return f"{h}:{m:02d}:{s:05.2f}"
ev=[]
for i,c in enumerate(caps):
    s=remap(c[0][0]); e=remap(caps[i+1][0][0]) if i+1<len(caps) else min(newdur,remap(c[-1][2])+0.3)
    if e-s>2.5: e=remap(c[-1][2])+0.25
    txt=" ".join(w[1] for w in c)
    for k,v in fixes.items(): txt=re.sub(r"\b"+re.escape(k)+r"\b",v,txt)
    txt=txt.rstrip(".,")
    ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{txt}")
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,4,2,2,60,60,330,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""+"\n".join(ev)+"\n"
assf=out.replace(".mp4",".ass"); open(assf,"w").write(ass)
expr="+".join(f"between(t,{a:.3f},{b:.3f})" for a,b in keep)
fc=f"[0:v]select='{expr}',setpts=N/FRAME_RATE/TB,ass={assf}[ov];[0:a]aselect='{expr}',asetpts=N/SR/TB[ca]"
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",fc,"-map","[ov]","-map","[ca]","-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out],check=True)
print(f"orig {dur:.1f}s -> {newdur:.1f}s, {len(keep)} segments, {len(caps)} captions")
