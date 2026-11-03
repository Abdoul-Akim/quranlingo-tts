import numpy as np
import pytest

from line_jobs import TTS_DIR
from similarity import cosine, reference_for


def test_identical_voices_score_one():
    a = np.array([0.3, 0.4, 0.5])
    assert cosine(a, a) == pytest.approx(1.0)


def test_opposite_voices_score_minus_one():
    a = np.array([1.0, 0.0])
    assert cosine(a, -a) == pytest.approx(-1.0)


def test_scale_does_not_matter():
    a = np.array([1.0, 2.0, 3.0])
    assert cosine(a, 10 * a) == pytest.approx(1.0)


def test_native_folder_compares_with_the_native_voice():
    assert reference_for("voxcpm2", "fr", "ali") == TTS_DIR / "voices" / "fr" / "ali.wav"


def test_experiment_folder_compares_with_the_voice_it_was_cloned_from():
    assert reference_for("chatterbox_voice_en", "fr", "ali") == TTS_DIR / "voices" / "en" / "ali.wav"
