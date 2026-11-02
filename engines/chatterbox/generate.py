# Piece 1d: generate the English test lines with Chatterbox Multilingual V3.
# One take per line, using each character's reference voice from voices/en/.
# Run from engines/chatterbox:  uv run python generate.py
import csv
import sys
import time
from pathlib import Path

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))  # lets us import the shared text rules
from text_rules import prepare_text

LANGUAGE = "en"
SEED = 1

# Temporary mapping from intensity to Chatterbox's two dials (the real mapping is step 4).
# exaggeration: how dramatic the delivery is (default 0.5).
# cfg_weight: how strictly it follows the reference pacing; lower suits expressive speech (default 0.5).
DIALS = {
    "low": {"exaggeration": 0.4, "cfg_weight": 0.5},
    "medium": {"exaggeration": 0.6, "cfg_weight": 0.4},
    "high": {"exaggeration": 0.8, "cfg_weight": 0.3},
    "fixed": {"exaggeration": 0.5, "cfg_weight": 0.5},  # questions and options
}

lines_path = TTS_DIR / "test_lines" / f"{LANGUAGE}.csv"
voices_dir = TTS_DIR / "voices" / LANGUAGE
out_dir = TTS_DIR / "outputs" / f"step1_{LANGUAGE}" / "chatterbox"
out_dir.mkdir(parents=True, exist_ok=True)

with lines_path.open(encoding="utf-8") as f:
    lines = list(csv.DictReader(f))

device = "mps" if torch.backends.mps.is_available() else "cpu"
start = time.time()
# The first run downloads the V3 checkpoint from Hugging Face.
model = ChatterboxMultilingualTTS.from_pretrained(device=device, t3_model="v3")
print(f"Loaded on {device} in {time.time() - start:.0f}s")

for line in lines:
    text = prepare_text(line["text"], LANGUAGE)
    dials = DIALS[line["intensity"]]
    voice = voices_dir / f"{line['character']}.wav"

    torch.manual_seed(SEED)  # same seed, same take
    start = time.time()
    wav = model.generate(text, language_id=LANGUAGE, audio_prompt_path=str(voice), **dials)

    out_path = out_dir / f"{line['id']}.wav"
    torchaudio.save(str(out_path), wav, model.sr)
    seconds = wav.shape[-1] / model.sr
    print(f"{line['id']} ({line['character']}, {line['emotion']}): {seconds:.1f}s of audio in {time.time() - start:.0f}s")

print(f"Done. Listen in {out_dir}")
