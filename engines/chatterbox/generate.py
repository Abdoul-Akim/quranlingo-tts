# Generate the test lines with Chatterbox Multilingual V3, cloning each character's reference
# voice and setting the emotion dials from the line's intensity (tools/line_styles.py).
# Resumable: clips that already exist are skipped.
#
# Run from engines/chatterbox:
#   uv run python generate.py en fr de                native voices
#   uv run python generate.py fr de --voices-from en  experiment: the English voices speak French, German
import sys
import time
from pathlib import Path

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))
from line_jobs import output_dir, read_lines, voice_path
from line_styles import chatterbox_args, engines_for
from text_rules import prepare_text

SEED = 1

if __name__ == "__main__":
    args = sys.argv[1:]
    voices_from = args[args.index("--voices-from") + 1] if "--voices-from" in args else None
    languages = [a for a in args if a not in ("--voices-from", voices_from)] or ["en"]

    model = None
    for language in languages:
        if "chatterbox" not in engines_for(language):
            print(f"{language}: not supported by Chatterbox, skipped", flush=True)
            continue
        out_dir = output_dir(language, "chatterbox", voices_from)
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
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                model = ChatterboxMultilingualTTS.from_pretrained(device=device, t3_model="v3")
            torch.manual_seed(SEED)
            start = time.time()
            wav = model.generate(prepare_text(line["text"], language), language_id=language,
                                 audio_prompt_path=str(voice), **chatterbox_args(line))
            torchaudio.save(str(out_path), wav, model.sr)
            print(f"{language} {out_path.parent.name}/{line['id']} ({line['character']}): "
                  f"{wav.shape[-1] / model.sr:.1f}s in {time.time() - start:.0f}s", flush=True)
    print("Done.", flush=True)
