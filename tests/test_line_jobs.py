from pathlib import Path

from line_jobs import TTS_DIR, output_dir, read_lines, voice_path


def test_native_clips_go_to_the_engine_folder():
    assert output_dir("fr", "voxcpm2") == TTS_DIR / "outputs" / "step1_fr" / "voxcpm2"


def test_experiment_clips_are_kept_apart():
    # Side experiment: the English voice speaking French goes to its own folder.
    assert output_dir("fr", "chatterbox", voices_from="en") == TTS_DIR / "outputs" / "step1_fr" / "chatterbox_voice_en"


def test_native_voice_by_default():
    assert voice_path("tr", "ali") == TTS_DIR / "voices" / "tr" / "ali.wav"


def test_experiment_uses_the_other_languages_voice():
    assert voice_path("tr", "ali", voices_from="en") == TTS_DIR / "voices" / "en" / "ali.wav"


def test_read_lines_reads_the_language_file():
    rows = read_lines("de")
    assert rows[0]["id"] == "e01" and rows[0]["text"].startswith("Der Koran")
