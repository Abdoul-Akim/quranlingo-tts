import pytest

from project_config import CHARACTERS, LANGUAGES
from ui_text import character_label, hint, line_label

EMOTIONS = ["neutral", "warm", "happy", "excited", "sad", "calm", "curious", "serious"]


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_label_exists_in_every_language(language):
    for character in CHARACTERS:
        assert character_label(character, language)
    assert line_label(1, 16, language)
    for emotion in EMOTIONS:
        for intensity in ("low", "medium", "high"):
            assert hint(emotion, intensity, language)
    assert hint("question", "fixed", language) and hint("option", "fixed", language)


@pytest.mark.parametrize("language", [l for l in LANGUAGES if l != "en"])
def test_other_languages_show_no_english_words(language):
    english = ["woman", "girl", "boy", "man,", "Line", "Should sound", "warm", "medium", "high"]  # "question" is French too
    shown = " ".join([character_label(c, language) for c in CHARACTERS] + [line_label(3, 16, language)]
                     + [hint(e, "medium", language) for e in EMOTIONS] + [hint("question", "fixed", language)])
    assert not [w for w in english if w in shown]


def test_french_examples():
    assert character_label("zahra", "fr") == "Zahra (fille, 10 ans)"
    assert line_label(3, 16, "fr") == "Phrase 3 sur 16"
    assert hint("warm", "medium", "fr") == "Ton attendu : chaleureux (intensité moyenne)"


def test_english_stays_as_before():
    assert character_label("fatima", "en") == "Fatima (woman, 29)"
    assert line_label(1, 16, "en") == "Line 1 of 16"
    assert hint("warm", "medium", "en") == "Should sound: warm (medium)"
    assert hint("question", "fixed", "en") == "Should sound: a warm, clear question"
