# Where clips go and which reference voice each one uses, for every engine.
#   Native:      outputs/<set>_<lang>/<engine>/              voice from voices/<lang>/<character>.wav
#   Experiment:  outputs/<set>_<lang>/<engine>_voice_<src>/  voice from voices/<src>/<character>.wav
# The default set is "step1" (test_lines/<lang>.csv); "variations" reads test_lines/variations_<lang>.csv.
import csv
from pathlib import Path

TTS_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SET = "step1"


def output_dir(language: str, engine: str, voices_from: str | None = None, line_set: str = DEFAULT_SET) -> Path:
    name = engine if not voices_from else f"{engine}_voice_{voices_from}"
    return TTS_DIR / "outputs" / f"{line_set}_{language}" / name


def voice_path(language: str, character: str, voices_from: str | None = None) -> Path:
    return TTS_DIR / "voices" / (voices_from or language) / f"{character}.wav"


def read_lines(language: str, line_set: str = DEFAULT_SET) -> list[dict]:
    name = f"{language}.csv" if line_set == DEFAULT_SET else f"{line_set}_{language}.csv"
    with (TTS_DIR / "test_lines" / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))
