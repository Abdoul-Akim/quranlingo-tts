# Make a voice sound younger (or older) by shifting its pitch and its formants.
#
# Pitch is how high the voice is. Formants are the resonances of the throat and mouth;
# a smaller vocal tract moves them up, which is what makes a voice sound like a child
# rather than just a higher adult. Raising pitch alone gives a "chipmunk" sound.
#
# Uses the WORLD vocoder (pyworld, MIT; WORLD, modified BSD), which splits speech into
# pitch, spectral envelope (formants) and aperiodicity, so each can be changed separately.
#
# Run with the analysis environment, from the TTS folder:
#   uv run --project analysis python tools/age_shift.py in.wav out.wav 2 1.08
#       one file: pitch shift in semitones, formant ratio (1.0 = no change, above 1 = younger)
#   uv run --project analysis python tools/age_shift.py --plan outputs/base_voices/en
#       every child take in a language folder, using SHIFT_PLAN below (resumable)
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pyworld as pw
import soundfile as sf


class Shift(NamedTuple):
    name: str
    semitones: float
    formant_ratio: float


# Strengths to try. "direct" takes were designed as children; "from_female" takes were designed
# as a light adult woman and are moved toward the child. A 14 year old boy sits a little below
# an adult woman in pitch with similar formants; a 10 year old girl sits above, with higher formants.
SHIFT_PLAN = {
    "ali": {
        "direct": [Shift("light", 1, 1.04), Shift("young", 2, 1.08)],
        "from_female": [Shift("boy_a", -2, 1.0), Shift("boy_b", -3, 0.97)],
    },
    "zahra": {
        "direct": [Shift("light", 2, 1.06), Shift("young", 3, 1.12)],
        "from_female": [Shift("girl_a", 3, 1.10), Shift("girl_b", 4, 1.15)],
    },
}


def shifts_for(character: str, variant: str) -> list[Shift]:
    plan = SHIFT_PLAN.get(character)
    if not plan:
        return []
    return plan["from_female" if variant == "from_female" else "direct"]


def shift(audio: np.ndarray, sr: int, semitones: float, formant_ratio: float) -> np.ndarray:
    x = audio.astype(np.float64)
    f0, time_axis = pw.harvest(x, sr)          # pitch track
    sp = pw.cheaptrick(x, f0, time_axis, sr)   # spectral envelope: the formants
    ap = pw.d4c(x, f0, time_axis, sr)          # aperiodicity: breathiness and noise

    f0_new = f0 * 2 ** (semitones / 12)  # 12 semitones is one octave (double the pitch)

    # Formant shift: the new envelope at frequency f is the old one at f / ratio,
    # so with ratio 1.1 every resonance moves 10% higher.
    bins = np.arange(sp.shape[1])
    sp_new = np.empty_like(sp)
    for frame in range(sp.shape[0]):
        sp_new[frame] = np.interp(bins / formant_ratio, bins, sp[frame])

    y = pw.synthesize(f0_new, sp_new, ap, sr)
    # Keep the original loudness peak so shifted and unshifted takes compare fairly.
    peak = np.abs(y).max()
    return (y * (np.abs(x).max() / peak if peak > 0 else 1.0)).astype(np.float32)


def apply_plan(language_dir: Path) -> list[str]:
    # Writes <take>__shift_<name>.wav next to each child take. Returns the files it wrote.
    written = []
    for character in SHIFT_PLAN:
        for take in sorted((language_dir / character).glob("*.wav")) if (language_dir / character).exists() else []:
            if "__shift_" in take.stem:
                continue
            variant = take.stem.rsplit("_seed", 1)[0]
            audio = None
            for s in shifts_for(character, variant):
                out = take.with_name(f"{take.stem}__shift_{s.name}.wav")
                if out.exists():
                    continue
                if audio is None:
                    audio, sr = sf.read(take)
                    if audio.ndim > 1:
                        audio = audio.mean(axis=1)
                sf.write(out, shift(audio, sr, s.semitones, s.formant_ratio), sr)
                written.append(f"{character}/{out.name}")
    return written


if __name__ == "__main__":
    if sys.argv[1] == "--plan":
        for name in apply_plan(Path(sys.argv[2])):
            print(f"Saved {name}", flush=True)
    else:
        in_path, out_path, semitones, ratio = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        audio, sr = sf.read(in_path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        sf.write(out_path, shift(audio, sr, semitones, ratio), sr)
        print(f"Saved {out_path}")
