# Phase A and B: design the base voices of Ali, Fatima, Omar and Zahra with VoxCPM2 voice design.
# Each character is tried with several description wordings and seeds, so listeners can choose.
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
from project_config import CHARACTERS, DESCRIPTIONS, FROM_FEMALE_DESCRIPTIONS, LANGUAGE_NAMES, PASSAGES

# English is where we choose the method, so it gets more takes than the other languages.
SEEDS = {"en": [1, 2, 3, 4, 5]}
DEFAULT_SEEDS = [1, 2]
ADULT_SEEDS = {"en": [1, 2, 3, 4]}
DEFAULT_ADULT_SEEDS = [1, 2]


def jobs_for(language):
    # Yields (character, variant name, description, seed) for one language.
    accent = "" if language == "en" else f", speaking {LANGUAGE_NAMES[language]} with a native accent"
    for character in CHARACTERS:
        child = character in FROM_FEMALE_DESCRIPTIONS
        seeds = (SEEDS if child else ADULT_SEEDS).get(language, DEFAULT_SEEDS if child else DEFAULT_ADULT_SEEDS)
        variants = dict(DESCRIPTIONS[character])
        if child:
            variants["from_female"] = FROM_FEMALE_DESCRIPTIONS[character]
        for variant, description in variants.items():
            for seed in seeds:
                yield character, variant, description + accent, seed


languages = sys.argv[1:] or ["en"]
model = None
for language in languages:
    out_root = TTS_DIR / "outputs" / "base_voices" / language
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "passage.txt").write_text(PASSAGES[language] + "\n", encoding="utf-8")
    manifest_path = out_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    for character, variant, description, seed in jobs_for(language):
        out_path = out_root / character / f"{variant}_seed{seed}.wav"
        if out_path.exists():
            continue
        if model is None:  # load only when there is work to do
            start = time.time()
            model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, optimize=False)
            print(f"Loaded on {model.tts_model.device} in {time.time() - start:.0f}s", flush=True)
        out_path.parent.mkdir(exist_ok=True)

        torch.manual_seed(seed)
        start = time.time()
        wav = model.generate(
            text=f"({description}){PASSAGES[language]}",
            cfg_value=CFG_VALUE, inference_timesteps=INFERENCE_TIMESTEPS,
        )
        sr = model.tts_model.sample_rate
        sf.write(out_path, wav, sr)
        manifest[f"{character}/{out_path.name}"] = {"description": description, "seed": seed, "variant": variant}
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{language} {character}/{out_path.name}: {len(wav) / sr:.1f}s in {time.time() - start:.0f}s", flush=True)

print("Done.", flush=True)
