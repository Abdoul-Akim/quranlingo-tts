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
#   (pitch shift in semitones, formant ratio: 1.0 means no change, above 1 means younger)
import sys

import numpy as np
import pyworld as pw
import soundfile as sf


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


if __name__ == "__main__":
    in_path, out_path, semitones, ratio = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    audio, sr = sf.read(in_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    sf.write(out_path, shift(audio, sr, semitones, ratio), sr)
    print(f"Saved {out_path}")
