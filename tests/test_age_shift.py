import numpy as np
import pyworld as pw
import soundfile as sf

from age_shift import SHIFT_PLAN, apply_plan, shift, shifts_for

SR = 16000


def voice_like(f0=150.0, seconds=1.0):
    # A harmonic tone (like a sustained vowel) so the pitch tracker has something to follow.
    t = np.arange(int(SR * seconds)) / SR
    return sum(np.sin(2 * np.pi * f0 * k * t) / k for k in range(1, 12)) * 0.1


def median_f0(x):
    f0, _ = pw.harvest(x.astype(np.float64), SR)
    return float(np.median(f0[f0 > 0]))


def test_two_semitones_raise_pitch_by_about_12_percent():
    x = voice_like()
    y = shift(x, SR, semitones=2, formant_ratio=1.0)
    assert abs(median_f0(y) / median_f0(x) - 2 ** (2 / 12)) < 0.03


def test_shift_keeps_the_length():
    x = voice_like()
    assert abs(len(shift(x, SR, 3, 1.1)) - len(x)) < SR * 0.02


def test_adults_are_never_shifted():
    assert shifts_for("fatima", "v1") == [] and shifts_for("omar", "v2") == []


def test_children_designed_directly_are_made_slightly_younger():
    for character in ("ali", "zahra"):
        assert shifts_for(character, "v1") and all(s.semitones > 0 for s in shifts_for(character, "v1"))


def test_ali_from_a_female_voice_goes_down_and_zahra_goes_up():
    assert all(s.semitones < 0 for s in shifts_for("ali", "from_female"))
    assert all(s.semitones > 0 for s in shifts_for("zahra", "from_female"))


def test_apply_plan_writes_named_copies_and_is_resumable(tmp_path):
    folder = tmp_path / "ali"
    folder.mkdir()
    sf.write(folder / "v1_seed1.wav", voice_like(200), SR)
    sf.write(tmp_path / "ali" / "v1_seed1__shift_light.wav", voice_like(200), SR)  # already done

    written = apply_plan(tmp_path)

    names = sorted(p.name for p in folder.glob("*.wav"))
    expected = sorted(["v1_seed1.wav"] + [f"v1_seed1__shift_{s.name}.wav" for s in SHIFT_PLAN["ali"]["direct"]])
    assert names == expected
    assert "ali/v1_seed1__shift_light.wav" not in written  # skipped, it existed


def test_apply_plan_never_shifts_a_shifted_file(tmp_path):
    folder = tmp_path / "zahra"
    folder.mkdir()
    sf.write(folder / "v1_seed1__shift_light.wav", voice_like(260), SR)
    assert apply_plan(tmp_path) == []
