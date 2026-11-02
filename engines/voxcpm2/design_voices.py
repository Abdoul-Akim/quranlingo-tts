# Piece 1b: design the 4 English character voices with VoxCPM2 voice design.
# Makes 3 takes per character (seeds 1, 2, 3) so the owner can pick one each.
# Run from engines/voxcpm2:  uv run python design_voices.py
import time
from pathlib import Path

import soundfile as sf
import torch
from voxcpm import VoxCPM

from voices_config import CFG_VALUE, INFERENCE_TIMESTEPS, PASSAGE, VOICES, VOICES_VERSION

SEEDS = [1, 2, 3]

# The folder name records the descriptions version and the settings,
# so takes made with different ones never overwrite each other.
out_dir = (
    Path(__file__).resolve().parents[2] / "outputs" / "voice_design"
    / f"en_{VOICES_VERSION}_steps{INFERENCE_TIMESTEPS}_cfg{CFG_VALUE}"
)
out_dir.mkdir(parents=True, exist_ok=True)
# Keep the transcript next to the clips: cloning later needs the exact words.
(out_dir / "passage.txt").write_text(PASSAGE + "\n", encoding="utf-8")

start = time.time()
model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False)
sr = model.tts_model.sample_rate
print(f"Loaded on {model.tts_model.device} in {time.time() - start:.0f}s")

for character, description in VOICES.items():
    for seed in SEEDS:
        torch.manual_seed(seed)
        start = time.time()
        wav = model.generate(
            text=f"({description}){PASSAGE}", cfg_value=CFG_VALUE, inference_timesteps=INFERENCE_TIMESTEPS
        )
        out_path = out_dir / f"{character}_seed{seed}.wav"
        sf.write(out_path, wav, sr)
        print(f"{out_path.name}: {len(wav) / sr:.1f}s of audio in {time.time() - start:.0f}s")

print(f"Done. Listen in {out_dir}")
