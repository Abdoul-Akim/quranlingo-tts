# Design base voices for Urdu (and Hindi, as an extra candidate) with Indic Parler-TTS.
# Needs one-time access: accept the terms on https://huggingface.co/ai4bharat/indic-parler-tts
# Clips go to outputs/base_voices/<lang>_parler/ so they never mix with another engine's takes.
# Resumable: clips that already exist are skipped.
#
# Run from engines/parler:  uv run python design_base_voices.py ur hi
import json
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))
from base_voices import take_path
from parler_voices import jobs_for
from project_config import PASSAGES

MODEL_ID = "ai4bharat/indic-parler-tts"

if __name__ == "__main__":
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = tokenizer = description_tokenizer = None
    for language in sys.argv[1:] or ["ur"]:
        out_root = TTS_DIR / "outputs" / "base_voices" / f"{language}_parler"
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "passage.txt").write_text(PASSAGES[language] + "\n", encoding="utf-8")
        manifest_path = out_root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

        for job in jobs_for(language):
            out_path = out_root / take_path(job)
            if out_path.exists():
                continue
            if model is None:
                start = time.time()
                model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID).to(device)
                tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
                description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
                print(f"Loaded on {device} in {time.time() - start:.0f}s", flush=True)
            out_path.parent.mkdir(exist_ok=True)

            # Two inputs, as on the model card: the voice description and the text to speak.
            description = description_tokenizer(job.description, return_tensors="pt").to(device)
            prompt = tokenizer(PASSAGES[language], return_tensors="pt").to(device)
            torch.manual_seed(job.seed)
            start = time.time()
            generation = model.generate(
                input_ids=description.input_ids, attention_mask=description.attention_mask,
                prompt_input_ids=prompt.input_ids, prompt_attention_mask=prompt.attention_mask,
            )
            audio = generation.cpu().numpy().squeeze()
            sr = model.config.sampling_rate
            sf.write(out_path, audio, sr)
            manifest[take_path(job)] = job._asdict()
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{language} {take_path(job)}: {len(audio) / sr:.1f}s in {time.time() - start:.0f}s", flush=True)
    print("Done.", flush=True)
