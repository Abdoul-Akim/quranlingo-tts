# Generate the test lines with VoxCPM2, cloning each character's reference voice and steering
# the emotion with a style instruction (tools/line_styles.py).
# Resumable: clips that already exist are skipped.
#
# Run from engines/voxcpm2:
#   uv run python generate.py en fr de                native voices
#   uv run python generate.py fr de --voices-from en  experiment: the English voices speak French, German
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from voxcpm import VoxCPM

from voices_config import CFG_VALUE, INFERENCE_TIMESTEPS

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))
from line_jobs import output_dir, read_lines, voice_path
from line_styles import engines_for, voxcpm_text

SEED = 1

if __name__ == "__main__":
    args = sys.argv[1:]
    voices_from = args[args.index("--voices-from") + 1] if "--voices-from" in args else None
    languages = [a for a in args if a not in ("--voices-from", voices_from)] or ["en"]

    model = None
    for language in languages:
        if "voxcpm2" not in engines_for(language):
            print(f"{language}: not supported by VoxCPM2, skipped", flush=True)
            continue
        out_dir = output_dir(language, "voxcpm2", voices_from)
        out_dir.mkdir(parents=True, exist_ok=True)
        for line in read_lines(language):
            out_path = out_dir / f"{line['id']}.wav"
            voice = voice_path(language, line["character"], voices_from)
            if out_path.exists():
                continue
            if not voice.exists():
                print(f"{language} {line['id']}: no voice {voice.relative_to(TTS_DIR)}, skipped", flush=True)
                continue
            if model is None:
                model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False)
            torch.manual_seed(SEED)
            start = time.time()
            wav = model.generate(
                text=voxcpm_text(line, language), reference_wav_path=str(voice),
                cfg_value=CFG_VALUE, inference_timesteps=INFERENCE_TIMESTEPS,
            )
            sr = model.tts_model.sample_rate
            sf.write(out_path, wav, sr)
            print(f"{language} {out_path.parent.name}/{line['id']} ({line['character']}): "
                  f"{len(wav) / sr:.1f}s in {time.time() - start:.0f}s", flush=True)
    print("Done.", flush=True)
