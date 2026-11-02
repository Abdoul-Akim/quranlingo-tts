# Phase A and B: design the base voices of Ali, Fatima, Omar and Zahra with VoxCPM2 voice design.
# Each character is tried with several description wordings and seeds, so listeners can choose.
# The list of takes comes from tools/base_voices.py.
# Resumable: clips that already exist are skipped, so rerunning continues where it stopped.
#
# Run from engines/voxcpm2:
#   uv run python design_base_voices.py en            one language
#   uv run python design_base_voices.py fr de tr      several languages
import json
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from voxcpm import VoxCPM

from voices_config import CFG_VALUE, INFERENCE_TIMESTEPS

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))
from base_voices import jobs_for, take_path
from project_config import PASSAGES

if __name__ == "__main__":
    model = None
    for language in sys.argv[1:] or ["en"]:
        out_root = TTS_DIR / "outputs" / "base_voices" / language
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "passage.txt").write_text(PASSAGES[language] + "\n", encoding="utf-8")
        manifest_path = out_root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

        for job in jobs_for(language):
            out_path = out_root / take_path(job)
            if out_path.exists():
                continue
            if model is None:  # load only when there is work to do
                start = time.time()
                model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False)
                print(f"Loaded on {model.tts_model.device} in {time.time() - start:.0f}s", flush=True)
            out_path.parent.mkdir(exist_ok=True)

            torch.manual_seed(job.seed)
            start = time.time()
            wav = model.generate(
                text=f"({job.description}){PASSAGES[language]}",
                cfg_value=CFG_VALUE, inference_timesteps=INFERENCE_TIMESTEPS,
            )
            sr = model.tts_model.sample_rate
            sf.write(out_path, wav, sr)
            manifest[take_path(job)] = job._asdict()
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{language} {take_path(job)}: {len(wav) / sr:.1f}s in {time.time() - start:.0f}s", flush=True)

    print("Done.", flush=True)
