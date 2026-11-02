# Piece 1e: generate the English test lines with VoxCPM2.
# One take per line, cloning each character's reference voice from voices/en/
# and steering the emotion with a style instruction in brackets.
# Run from engines/voxcpm2:  uv run python generate.py
import csv
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from voxcpm import VoxCPM

from voices_config import CFG_VALUE, INFERENCE_TIMESTEPS

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))  # lets us import the shared text rules
from text_rules import prepare_text

LANGUAGE = "en"
SEED = 1

# Temporary mapping from emotion to a style instruction (the real mapping is step 4).
STYLES = {
    "neutral": "clear and even, informative",
    "warm": "warm and welcoming, friendly",
    "happy": "happy and cheerful, smiling",
    "excited": "excited and energetic, lively",
    "sad": "sad and gentle, slightly slower",
    "calm": "calm and soothing, slow and relaxed",
    "curious": "curious and wondering, inviting",
    "serious": "serious and firm, steady",
    "question": "warm and clear, like a friendly teacher",
    "option": "warm and clear, like a friendly teacher",
}
# Intensity adds a word in front of the style. Neutral and the fixed style never get one.
INTENSITY_WORDS = {"low": "slightly ", "medium": "", "high": "very ", "fixed": ""}


def style_for(emotion: str, intensity: str) -> str:
    word = "" if emotion == "neutral" else INTENSITY_WORDS[intensity]
    return f"{word}{STYLES[emotion]}"


lines_path = TTS_DIR / "test_lines" / f"{LANGUAGE}.csv"
voices_dir = TTS_DIR / "voices" / LANGUAGE
out_dir = TTS_DIR / "outputs" / f"step1_{LANGUAGE}" / "voxcpm2"
out_dir.mkdir(parents=True, exist_ok=True)

with lines_path.open(encoding="utf-8") as f:
    lines = list(csv.DictReader(f))

start = time.time()
model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False)
sr = model.tts_model.sample_rate
print(f"Loaded on {model.tts_model.device} in {time.time() - start:.0f}s")

for line in lines:
    style = style_for(line["emotion"], line["intensity"])
    text = f"({style}){prepare_text(line['text'], LANGUAGE)}"
    voice = voices_dir / f"{line['character']}.wav"

    torch.manual_seed(SEED)  # same seed, same take
    start = time.time()
    wav = model.generate(
        text=text,
        reference_wav_path=str(voice),
        cfg_value=CFG_VALUE,
        inference_timesteps=INFERENCE_TIMESTEPS,
    )

    out_path = out_dir / f"{line['id']}.wav"
    sf.write(out_path, wav, sr)
    print(f"{line['id']} ({line['character']}, {style}): {len(wav) / sr:.1f}s of audio in {time.time() - start:.0f}s")

print(f"Done. Listen in {out_dir}")
