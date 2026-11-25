#!/usr/bin/env python3
"""MYSTERY VERSE still-image episode renderer: one generated image per narration sentence."""
import argparse, asyncio, json, os, re, subprocess, sys, time
from pathlib import Path
import requests
import edge_tts

STYLE = ("photorealistic live-action Indonesian rural supernatural horror film still, "
"cold desaturated blue-gray shadows, muted forest green and earth tones, gloomy overcast dusk, "
"subtle volumetric fog, realistic wet muddy village roads, aged wooden Indonesian houses, "
"bamboo fences, dense tropical trees, restrained warm amber practical lights, dramatic but readable "
"natural lighting, realistic human anatomy and skin texture, cinematic composition, 16:9 widescreen. "
"No illustration, no anime, no cartoon, no glossy CGI, no text, no watermark.")
NEGATIVE = "cartoon, anime, illustration, painting, 3d render, CGI, oversaturated, fantasy armor, text, watermark, collage, split screen"

def sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    # Keep punctuation with each sentence; avoid splitting common abbreviations.
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Þ“\"'])", text) if x.strip()]

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-2500:])
    return p.stdout.strip()

def generate_image(prompt, token, out):
    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Accept":"image/png"},
        json={"inputs": prompt, "parameters":{"width": 1024, "height": 576, "negative_prompt":NEGATIVE}}, timeout=600)
    if r.status_code != 200:
        raise RuntimeError(f"Image generation failed HTTP {r.status_code}: {r.text[:700]}")
    if not r.headers.get("content-type","").startswith("image/"):
        raise RuntimeError(f"Image endpoint did not return an image: {r.text[:500]}")
    out.write_bytes(r.content)

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--output", required=True)
    args=ap.parse_args()
    token=os.getenv("HF_TOKEN")
    if not token: raise SystemExit("HF_TOKEN secret is required; refusing to make fake/mock visuals.")
    ffmpeg=os.getenv("FFMPEG_PATH","ffmpeg")
    src=Path(args.input).read_text(encoding="utf-8")
    lines=[x.strip() for x in src.splitlines() if x.strip() and not x.lstrip().startswith("#")]
    text=" ".join(lines)
    items=sentences(text)
    if not items: raise SystemExit("No narration sentences found.")
    out=Path(args.output); imgs=out/"images"; aud=out/"audio"; clips=out/"clips"
    for d in (imgs,aud,clips): d.mkdir(parents=True,exist_ok=True)
    manifest=[]
    voice=os.getenv("EDGE_TTS_VOICE","id-ID-ArdiNeural")
    rate=os.getenv("EDGE_TTS_RATE","-12%")
    for i,s in enumerate(items):
        n=i+1
        # Sentence-specific scene direction is grounded in the actual narration; locked style is appended unchanged.
        prompt=f"Scene {n}, depict this exact story moment faithfully: {s}. {STYLE}"
        image=imgs/f"scene_{n:04d}.png"
        audio=aud/f"scene_{n:04d}.mp3"
        if not image.exists():
            print(f"[{n}/{len(items)}] Generating still image", flush=True)
            generate_image(prompt,token,image)
            time.sleep(1)
        if not audio.exists():
            print(f"[{n}/{len(items)}] Generating Indonesian narration", flush=True)
            await edge_tts.Communicate(s,voice,rate=rate,pitch="-12Hz").save(str(audio))
        duration=float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(audio)]))
        clip=clips/f"clip_{n:04d}.mp4"
        run([ffmpeg,"-y","-loop","1","-i",str(image),"-i",str(audio),"-t",f"{duration:.3f}",
             "-vf","scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.00025,1.04)':d=1:s=1920x1080:fps=25,format=yuv420p",
             "-r","25","-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-b:a","160k",
             "-shortest",str(clip)])
        manifest.append({"scene":n,"narration":s,"image":str(image),"audio":str(audio),"clip":str(clip),"duration_seconds":duration,"prompt":prompt})
        (out/"scene_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    concat=out/"concat.txt"
    concat.write_text("".join(f"file '{(clips/f'clip_{i+1:04d}.mp4').resolve()}'\n" for i in range(len(items))),encoding="utf-8")
    final=out/"MYSTERY_VERSE_Kampung_Jabang_Mayit.mp4"
    run([ffmpeg,"-y","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(final)])
    print(f"RENDER_OK={final}",flush=True)

if __name__=="__main__": asyncio.run(main())
