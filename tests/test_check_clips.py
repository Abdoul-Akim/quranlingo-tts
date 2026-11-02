import numpy as np
import soundfile as sf

from check_clips import load_for_asr, normalise


def test_load_for_asr_gives_16k_mono_float32(tmp_path):
    # Our engines write 48 kHz (VoxCPM2) or 24 kHz (Chatterbox); Whisper needs 16 kHz mono.
    t = np.linspace(0, 2.0, 2 * 48000, endpoint=False)
    stereo = np.stack([np.sin(2 * np.pi * 220 * t)] * 2, axis=1) * 0.5
    path = tmp_path / "tone.wav"
    sf.write(path, stereo, 48000)

    audio = load_for_asr(path)

    assert audio.dtype == np.float32
    assert audio.ndim == 1
    assert abs(len(audio) - 2 * 16000) <= 16  # 2 seconds at 16 kHz


def test_normalise_ignores_case_and_punctuation():
    assert normalise("Hello, and WELCOME!") == "hello and welcome"


def test_normalise_handles_arabic_and_urdu_punctuation():
    assert normalise("هل نبدأ؟ استمعوا جيدًا، وخذوا وقتكم۔") == "هل نبدأ استمعوا جيدًا وخذوا وقتكم"
