# Voice consistency check for test line clips, using Chatterbox's voice encoder (MIT).
# Writes similarity.csv in the folder: for each clip, its similarity to the reference voice
# it was cloned from (1.0 = the same voice). Works for any engine's clips.
#
# Run from engines/chatterbox:
#   uv run python speaker_similarity.py en ../../outputs/step1_en/voxcpm2
import csv
import sys
from pathlib import Path

import librosa
import torch
from huggingface_hub import hf_hub_download
from chatterbox.models.voice_encoder import VoiceEncoder

TTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TTS_DIR / "tools"))
from line_jobs import read_lines
from similarity import cosine, reference_for

if __name__ == "__main__":
    language, folder = sys.argv[1], Path(sys.argv[2]).resolve()
    encoder = VoiceEncoder()
    encoder.load_state_dict(torch.load(hf_hub_download("ResembleAI/chatterbox", "ve.pt"), map_location="cpu", weights_only=True))
    encoder.eval()

    def fingerprint(path):
        # Load at the encoder's own rate (16 kHz), so it never resamples: its resampler
        # needs the resampy package, which is not installed.
        rate = encoder.hp.sample_rate
        wav, _ = librosa.load(path, sr=rate, mono=True)
        return encoder.embeds_from_wavs([wav], sample_rate=rate, as_spk=True)

    references = {}
    rows = []
    for line in read_lines(language):
        clip = folder / f"{line['id']}.wav"
        reference = reference_for(folder.name, language, line["character"])
        if not clip.exists() or not reference.exists():
            continue
        if reference not in references:
            references[reference] = fingerprint(reference)
        score = cosine(fingerprint(clip), references[reference])
        rows.append({"clip": clip.name, "character": line["character"], "similarity": f"{score:.3f}",
                     "reference": str(reference.relative_to(TTS_DIR))})
        print(f"{clip.name} ({line['character']}): {score:.3f}", flush=True)

    with (folder / "similarity.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["clip", "character", "similarity", "reference"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Report: {folder / 'similarity.csv'}")
