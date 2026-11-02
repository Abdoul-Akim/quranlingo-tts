# Piece 1a: check that VoxCPM2 runs on this Mac by generating one sentence.
# Run from engines/voxcpm2:  uv run python hello.py          (Mac GPU)
#                            uv run python hello.py cpu      (force CPU)
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from voxcpm import VoxCPM

# "auto" lets VoxCPM pick: CUDA (not on a Mac), then MPS (the Mac GPU), then CPU.
device = sys.argv[1] if len(sys.argv) > 1 else "auto"

# Write into TTS/outputs/hello, two folders up from this file.
out_dir = Path(__file__).resolve().parents[2] / "outputs" / "hello"
out_dir.mkdir(parents=True, exist_ok=True)

# The first run downloads the model from Hugging Face (several GB, once).
# load_denoiser=False: the denoiser cleans up noisy reference clips, which we do not have.
# optimize=False: skips torch.compile, which is built for NVIDIA GPUs.
start = time.time()
model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False, device=device)
print(f"Loaded on {model.tts_model.device} in {time.time() - start:.0f}s")

# Voice design: the description in brackets invents a voice. It is not read aloud.
text = "(A warm older man, calm and gentle)Welcome to QuranLingo. Today we will learn something new together."

torch.manual_seed(42)  # same seed, same take
start = time.time()
wav = model.generate(text=text, cfg_value=2.0, inference_timesteps=10)
sr = model.tts_model.sample_rate
print(f"Generated {len(wav) / sr:.1f}s of audio in {time.time() - start:.0f}s")

out_path = out_dir / "voxcpm2_hello.wav"
sf.write(out_path, wav, sr)
print(f"Saved {out_path}")
