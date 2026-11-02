# Automatic checks for generated clips: length, pitch, and whether the words came out right.
#
# Speech recognition (faster-whisper, MIT; Whisper weights, MIT) writes down what it hears,
# and we compare that with the text the clip should say:
#   cer  character error rate, 0.0 means a perfect match (works for every script)
#   wer  word error rate, for languages written with spaces
# Results go to checks.csv in the folder. Resumable: clips already in checks.csv are skipped.
#
# Run from the TTS folder with the analysis environment:
#   uv run --project analysis python tools/check_clips.py en passage outputs/base_voices/en
#   uv run --project analysis python tools/check_clips.py en lines outputs/step1_en/chatterbox
import csv
import string
import sys
import unicodedata
from pathlib import Path

import jiwer
import librosa
import numpy as np
import pyworld as pw
import soundfile as sf
from faster_whisper import WhisperModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_config import PASSAGES
from text_rules import prepare_text

TTS_DIR = Path(__file__).resolve().parents[1]
FIELDS = ["clip", "seconds", "pitch_hz", "cer", "wer", "heard", "expected"]


def normalise(text: str) -> str:
    # Lower case, no punctuation, single spaces, so only real word differences count.
    text = unicodedata.normalize("NFKC", text).lower()
    text = "".join(" " if unicodedata.category(c).startswith("P") or c in string.punctuation else c for c in text)
    return " ".join(text.split())


def load_for_asr(path) -> np.ndarray:
    # Whisper wants 16 kHz mono float32 samples. We pass samples, not a file path, because
    # faster-whisper 1.2.1 cannot decode files with the installed av 19.
    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(np.float32)


def median_pitch(audio: np.ndarray, sr: int) -> float:
    x = audio.astype(np.float64)
    f0, t = pw.dio(x, sr)            # fast pitch estimate
    f0 = pw.stonemask(x, f0, t, sr)  # refined
    voiced = f0[f0 > 0]
    return float(np.median(voiced)) if len(voiced) else 0.0


def expected_texts(language: str, mode: str) -> dict:
    if mode == "passage":
        return {"*": PASSAGES[language]}
    with (TTS_DIR / "test_lines" / f"{language}.csv").open(encoding="utf-8") as f:
        return {row["id"]: prepare_text(row["text"], language) for row in csv.DictReader(f)}


if __name__ == "__main__":
    language, mode, folder = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    texts = expected_texts(language, mode)
    report = folder / "checks.csv"
    done = {}
    if report.exists():
        with report.open(encoding="utf-8") as f:
            done = {row["clip"]: row for row in csv.DictReader(f)}

    wavs = sorted(p for p in folder.rglob("*.wav"))
    todo = [p for p in wavs if str(p.relative_to(folder)) not in done]
    if todo:
        # large-v3-turbo: multilingual and accurate; int8 keeps it fast enough on a laptop CPU.
        whisper = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    for wav in todo:
        audio, sr = sf.read(wav)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        expected = texts.get("*", texts.get(wav.stem.split("__")[0], ""))
        segments, _ = whisper.transcribe(load_for_asr(wav), language=language, beam_size=5)
        heard = " ".join(s.text.strip() for s in segments)
        ref, hyp = normalise(expected), normalise(heard)
        done[str(wav.relative_to(folder))] = {
            "clip": str(wav.relative_to(folder)),
            "seconds": f"{len(audio) / sr:.2f}",
            "pitch_hz": f"{median_pitch(audio, sr):.0f}",
            "cer": f"{jiwer.cer(ref, hyp):.3f}" if ref else "",
            "wer": f"{jiwer.wer(ref, hyp):.3f}" if ref else "",
            "heard": heard,
            "expected": expected,
        }
        with report.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(done.values())
        row = done[str(wav.relative_to(folder))]
        print(f"{row['clip']}: {row['seconds']}s pitch {row['pitch_hz']} Hz cer {row['cer']}", flush=True)
    print(f"Report: {report}")
