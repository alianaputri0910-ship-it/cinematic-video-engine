#!/usr/bin/env python3
"""Build a sentence-by-sentence visual scene plan for MYSTERY VERSE."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

STYLE = (
    "Photorealistic live-action Indonesian rural horror film still, "
    "16:9 widescreen, desaturated blue-gray shadows, muted forest greens, "
    "subdued earth tones, overcast cloudy sky, gloomy natural light, "
    "restrained highlights, deep readable shadows, subtle atmospheric haze, "
    "aged Indonesian village houses with clay-tile roofs, muddy lanes, "
    "bamboo fences, dense trees, small warm amber practical lights, "
    "realistic human anatomy and skin texture, natural hair and fabric detail, "
    "cinematic framing, restrained depth of field, realistic production design. "
    "Match the exact look of the approved MYSTERY VERSE master reference. "
    "Do not change the film color grade or visual style."
)
NEGATIVE = (
    "anime, cartoon, illustration, painting, fantasy art, glossy CGI, "
    "oversaturated colors, bright sunny lighting, futuristic objects, "
    "text, captions, watermark, collage, storyboard panels, split screen"
)

# Avoid splitting common Indonesian abbreviations.
ABBREVIATIONS = ("Dr.", "dr.", "Jl.", "No.", "Prof.", "Sdr.", "Ny.", "Tn.")

def split_sentences(text: str) -> list[str]:
    protected = text
    placeholders = {}
    for i, abbr in enumerate(ABBREVIATIONS):
        token = f"__ABBR{i}__"
        protected = protected.replace(abbr, token)
        placeholders[token] = abbr
    parts = re.split(r"(?<=[.!?…])\s+|\n{2,}", protected)
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        for token, abbr in placeholders.items():
            part = part.replace(token, abbr)
        # Ignore headings/separators as narration, but retain them as section metadata.
        if part.startswith("#") or part.startswith("---"):
            continue
        if re.fullmatch(r"(OPENING|BAB\s+\d+|CLOSING).*", part, re.I):
            continue
        result.append(part)
    return result

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=Path("output/kampung-jabang-mayit/scene-plan.json"))
    args = ap.parse_args()
    text = args.input.read_text(encoding="utf-8")
    sentences = split_sentences(text)
    scenes = []
    for idx, sentence in enumerate(sentences, 1):
        scenes.append({
            "scene_id": f"scene_{idx:03d}",
            "index": idx,
            "narration_text": sentence,
            "visual_prompt": (
                f"Create one coherent cinematic shot depicting this exact story moment: {sentence} "
                f"{STYLE} No additional plot events."
            ),
            "negative_prompt": NEGATIVE,
            "aspect_ratio": "16:9",
            "master_reference_required": True,
            "duration_source": "align_to_tts_audio",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "project": "MYSTERY VERSE",
        "episode": "Kampung Jabang Mayit",
        "scene_count": len(scenes),
        "scene_granularity": "one narration sentence per scene",
        "visual_lock": "docs/mystery-verse-kampung-jabang-mayit-production-lock.md",
        "scenes": scenes,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {len(scenes)} sentence-level scenes: {args.output}")

if __name__ == "__main__":
    main()
