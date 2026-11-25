#!/usr/bin/env python3
"""Procedural MYSTERY VERSE renderer: SVG scene art + Edge TTS + FFmpeg."""
import argparse, asyncio, html, math, re, subprocess
from pathlib import Path
import edge_tts

W,H=1920,1080
STYLE={"sky":"#202b36","far":"#263b3b","mid":"#172a2c","ground":"#10191c","warm":"#e7a64c","fog":"#82929a"}
def run(cmd):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if p.returncode: raise RuntimeError(p.stderr[-2200:])
    return p.stdout.strip()
def split_sentences(s):
    s=re.sub(r"\s+"," ",s).strip()
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Þ“\"'])",s) if x.strip()]
def svg_scene(sentence,idx):
    t=sentence.lower()
    bus=any(k in t for k in ["bus","terminal","kendaraan"])
    motor=any(k in t for k in ["motor","melaju","mengikuti","jalan"])
    tree=any(k in t for k in ["pohon","beringin","hutan","akar","daun"])
    person=any(k in t for k in ["gue","dia","nenek","pria","nita","basir","berdiri","sosok"])
    house=any(k in t for k in ["desa","rumah","kampung","jalan","terminal"])
    monster=any(k in t for k in ["makhluk","hitam","berbulu","sosok","kaki"])
    # Scene variation is deterministic; the same locked palette and art direction remain.
    shift=(idx*137)%420
    buildings=""
    if house or not tree:
        for j in range(5):
            x=(j*390-120+shift)%2100-100
            h=230+(j*47%130)
            buildings+=f'<g opacity="{0.55+(j%3)*0.12}"><path d="M{x} {690-h} l150 -120 150 120 v{h} h-300z" fill="#263033"/><path d="M{x-18} {690-h} l168 -150 168 150" fill="none" stroke="#11191d" stroke-width="32"/><rect x="{x+65}" y="{690-h+100}" width="55" height="100" fill="#c48a43" opacity=".38"/><rect x="{x+190}" y="{690-h+90}" width="58" height="85" fill="#d59a4d" opacity=".25"/></g>'
    trees=""
    for j in range(12):
        x=(j*215+shift*2)%2200-120
        trees+=f'<g><path d="M{x} 780 Q{x-35} 460 {x+4} 210 Q{x+36} 480 {x+22} 780" fill="#101b1b"/><circle cx="{x}" cy="{330+(j*71)%170}" r="{130+(j*19)%65}" fill="#142522"/><circle cx="{x+60}" cy="{390+(j*43)%120}" r="105" fill="#1a302b"/></g>'
    fog=''.join(f'<ellipse cx="{(i*470+shift)%2200-120}" cy="{570+i*58}" rx="390" ry="48" fill="#aab8bd" opacity=".055"/>' for i in range(5))
    figure=""
    if person:
        x=1050+(idx%4)*95
        figure=f'<g transform="translate({x},570)"><ellipse cx="0" cy="365" rx="120" ry="24" fill="#05090b" opacity=".65"/><circle cx="0" cy="30" r="53" fill="#090d10"/><path d="M-65 88 Q0 48 65 88 L95 340 L-95 340Z" fill="#080d11"/><path d="M-40 338 L-55 480 M40 338 L55 480" stroke="#080d11" stroke-width="42"/></g>'
    if monster:
        figure+=f'<g transform="translate({1330-(idx%3)*90},490)" opacity=".94"><ellipse cx="0" cy="430" rx="145" ry="30" fill="#030607"/><path d="M-95 90 Q-170 160 -115 390 L-65 420 L-35 210 L5 210 L50 425 L110 405 Q165 150 70 70Z" fill="#050809"/><circle cx="0" cy="35" r="75" fill="#06090a"/><path d="M-50 95 L-145 280 M50 95 L150 280" stroke="#050809" stroke-width="48"/><path d="M-30 32 l18 0 M22 32 l18 0" stroke="#d59b55" stroke-width="10"/></g>'
    vehicle=""
    if bus:
        vehicle='<g transform="translate(300,590)"><rect x="0" y="0" width="690" height="250" rx="35" fill="#172329" stroke="#59656a" stroke-width="12"/><rect x="45" y="35" width="175" height="105" fill="#8fa0a5" opacity=".32"/><rect x="250" y="35" width="175" height="105" fill="#8fa0a5" opacity=".28"/><rect x="455" y="35" width="175" height="105" fill="#8fa0a5" opacity=".25"/><circle cx="145" cy="255" r="65" fill="#080c0f"/><circle cx="555" cy="255" r="65" fill="#080c0f"/></g>'
    elif motor:
        vehicle='<g transform="translate(600,730)" fill="none" stroke="#080d10" stroke-width="24"><circle cx="0" cy="100" r="62"/><circle cx="280" cy="100" r="62"/><path d="M0 100 L90 0 L185 100 L280 100 L210 0 L130 0" /></g>'
    lamp='<g><path d="M1620 520 V850" stroke="#090e10" stroke-width="18"/><path d="M1620 520 q0 -60 70 -60" stroke="#090e10" stroke-width="16" fill="none"/><circle cx="1690" cy="465" r="24" fill="#ffbd68"/><circle cx="1690" cy="465" r="110" fill="#e6a34f" opacity=".09"/></g>'
    title=html.escape(sentence[:115])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#182431"/><stop offset="1" stop-color="#45535a"/></linearGradient><linearGradient id="road" x2="0" y2="1"><stop stop-color="#273334"/><stop offset="1" stop-color="#090f12"/></linearGradient><filter id="blur"><feGaussianBlur stdDeviation="22"/></filter></defs>
<rect width="1920" height="1080" fill="url(#sky)"/><circle cx="1480" cy="230" r="170" fill="#a6adb0" opacity=".08" filter="url(#blur)"/>
<path d="M0 610 Q300 440 600 610 T1200 590 T1920 560 V1080 H0Z" fill="#1b292b"/>{buildings}{trees}
<path d="M700 1080 Q880 820 920 730 L1080 730 Q1190 880 1510 1080Z" fill="url(#road)"/>{vehicle}{figure}{lamp}{fog}
<rect width="1920" height="1080" fill="#07121a" opacity=".23"/><rect x="20" y="20" width="1880" height="1040" fill="none" stroke="#a9b6bb" opacity=".12" stroke-width="3"/>
<text x="70" y="1000" font-family="sans-serif" font-size="27" fill="#d6dcde" opacity=".78" letter-spacing="4">MYSTERY VERSE  •  {idx+1:03d}</text></svg>'''
async def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    src=Path(a.input).read_text(encoding="utf-8")
    lines=[x.strip() for x in src.splitlines() if x.strip() and not x.lstrip().startswith("#")]
    ss=split_sentences(" ".join(lines))
    if not ss: raise SystemExit("Naskah kosong.")
    out=Path(a.output); art=out/"art"; aud=out/"audio"; clips=out/"clips"
    for d in (art,aud,clips): d.mkdir(parents=True,exist_ok=True)
    concat=[]
    voice="id-ID-ArdiNeural"
    for i,s in enumerate(ss):
        n=i+1; svg=art/f"scene_{n:04d}.svg"; png=art/f"scene_{n:04d}.png"; mp3=aud/f"scene_{n:04d}.mp3"; clip=clips/f"clip_{n:04d}.mp4"
        svg.write_text(svg_scene(s,i),encoding="utf-8")
        run(["ffmpeg","-y","-loglevel","error","-i",str(svg),str(png)])
        await edge_tts.Communicate(s,voice,rate="-12%",pitch="-12Hz").save(str(mp3))
        dur=float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(mp3)]))
        # Gentle Ken Burns movement over each individually illustrated shot.
        vf=f"scale=1920:1080,zoompan=z='min(zoom+0.00018,1.035)':d=1:s=1920x1080:fps=25,format=yuv420p"
        run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(png),"-i",str(mp3),"-t",f"{dur:.3f}","-vf",vf,"-r","25","-c:v","libx264","-preset","ultrafast","-crf","22","-c:a","aac","-b:a","128k","-shortest",str(clip)])
        concat.append(f"file '{clip.resolve()}'")
        print(f"Rendered scene {n}/{len(ss)}",flush=True)
    (out/"concat.txt").write_text("\n".join(concat)+"\n",encoding="utf-8")
    final=out/"MYSTERY_VERSE_Kampung_Jabang_Mayit.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(out/"concat.txt"),"-c","copy","-movflags","+faststart",str(final)])
    print(f"FINAL_MP4={final}",flush=True)
if __name__=="__main__": asyncio.run(main())
