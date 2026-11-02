import pytest

from line_styles import EMOTIONS, chatterbox_args, engines_for, voxcpm_text


def line(emotion="sad", intensity="medium", text="He never lost hope.", character="omar"):
    return {"emotion": emotion, "intensity": intensity, "text": text, "character": character}


@pytest.mark.parametrize("emotion", EMOTIONS)
def test_every_emotion_has_a_voxcpm_style(emotion):
    assert voxcpm_text(line(emotion), "en").startswith("(")


def test_style_goes_in_brackets_before_the_spoken_text():
    assert voxcpm_text(line("sad", "medium"), "en") == "(sad and gentle, slightly slower)He never lost hope."


def test_high_intensity_adds_very_and_low_adds_slightly():
    assert voxcpm_text(line("excited", "high"), "en").startswith("(very excited")
    assert voxcpm_text(line("calm", "low"), "en").startswith("(slightly calm")


def test_neutral_and_questions_never_get_an_intensity_word():
    assert voxcpm_text(line("neutral", "high"), "en").startswith("(clear and even")
    assert voxcpm_text(line("question", "fixed"), "en").startswith("(warm and clear")


def test_voxcpm_text_applies_the_text_rules():
    spoken = voxcpm_text(line("question", "fixed", "Who is Jahannam (Hellfire) for?"), "en")
    assert spoken.count("(") == 1  # only the style instruction keeps brackets


@pytest.mark.parametrize("intensity, exaggeration", [("low", 0.4), ("medium", 0.6), ("high", 0.8), ("fixed", 0.5)])
def test_chatterbox_dials_follow_intensity(intensity, exaggeration):
    assert chatterbox_args(line(intensity=intensity))["exaggeration"] == exaggeration


def test_engines_per_language():
    assert engines_for("en") == ["chatterbox", "voxcpm2"]
    assert "chatterbox" not in engines_for("ur")  # Chatterbox has no Urdu
    assert engines_for("ur") == ["voxcpm2"]  # untested experiment, see project_config
