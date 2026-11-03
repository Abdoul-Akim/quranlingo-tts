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


def test_variation_clips_go_to_their_own_folder():
    assert output_dir("en", "voxcpm2", line_set="variations") == TTS_DIR / "outputs" / "variations_en" / "voxcpm2"


def test_read_lines_can_read_another_set():
    rows = read_lines("en", line_set="variations")
    assert rows[0]["id"] == "ali_neutral"


def test_a_clip_made_before_its_voice_changed_is_redone(tmp_path):
    # The English lines from 2026-10-24 used the old voices and were skipped as "done".
    import os
    from line_jobs import is_done
    clip, voice = tmp_path / "e01.wav", tmp_path / "ali.wav"
    assert not is_done(clip, voice)
    clip.write_bytes(b"x"); voice.write_bytes(b"x")
    os.utime(clip, (1000, 1000)); os.utime(voice, (2000, 2000))
    assert not is_done(clip, voice)
    os.utime(clip, (3000, 3000))
    assert is_done(clip, voice)
