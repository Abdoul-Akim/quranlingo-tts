# Where test line clips go and which reference voice each one uses, for every engine.
#   Native:      outputs/step1_<lang>/<engine>/            voice from voices/<lang>/<character>.wav
#   Experiment:  outputs/step1_<lang>/<engine>_voice_<src>/  voice from voices/<src>/<character>.wav
import csv
from pathlib import Path

TTS_DIR = Path(__file__).resolve().parents[1]


def output_dir(language: str, engine: str, voices_from: str | None = None) -> Path:
    name = engine if not voices_from else f"{engine}_voice_{voices_from}"
    return TTS_DIR / "outputs" / f"step1_{language}" / name


def voice_path(language: str, character: str, voices_from: str | None = None) -> Path:
    return TTS_DIR / "voices" / (voices_from or language) / f"{character}.wav"


def read_lines(language: str) -> list[dict]:
    with (TTS_DIR / "test_lines" / f"{language}.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))
