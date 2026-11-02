# Quality sweep: same voice, same seed, different generation settings.
# Used to find settings that remove the metallic, buzzy sound.
# Run from engines/voxcpm2:  uv run python quality_sweep.py middle_aged_male 1
#                            (character name, then the seed of the take you liked)
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from voxcpm import VoxCPM

from voices_config import PASSAGE, VOICES

# More timesteps: more refinement passes over the sound, slower but cleaner.
TIMESTEPS = [10, 20, 30, 50]
# Lower cfg: the model follows the description less strictly, often more natural.
CFG_VALUES = [1.5, 2.0]

character = sys.argv[1] if len(sys.argv) > 1 else "middle_aged_male"
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
description = VOICES[character]

out_dir = Path(__file__).resolve().parents[2] / "outputs" / "quality_sweep" / "en"
out_dir.mkdir(parents=True, exist_ok=True)

start = time.time()
model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False)
sr = model.tts_model.sample_rate
print(f"Loaded on {model.tts_model.device} in {time.time() - start:.0f}s")

for steps in TIMESTEPS:
    for cfg in CFG_VALUES:
        torch.manual_seed(seed)
        start = time.time()
        wav = model.generate(text=f"({description}){PASSAGE}", cfg_value=cfg, inference_timesteps=steps)
        out_path = out_dir / f"{character}_seed{seed}_steps{steps}_cfg{cfg}.wav"
        sf.write(out_path, wav, sr)
        print(f"{out_path.name}: {len(wav) / sr:.1f}s of audio in {time.time() - start:.0f}s")

print(f"Done. Listen in {out_dir}")
