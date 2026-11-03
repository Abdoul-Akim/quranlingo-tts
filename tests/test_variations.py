import pytest

from line_styles import EMOTIONS
from project_config import CHARACTERS, LANGUAGES
from variations import VARIATION_SENTENCE, variation_lines


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_language_has_the_variation_sentence(language):
    assert VARIATION_SENTENCE[language].strip()


def test_each_character_says_the_sentence_in_every_emotion():
    rows = variation_lines("en")
    spoken_emotions = [e for e in EMOTIONS if e != "option"]  # an option is not an emotion
    assert len(rows) == len(CHARACTERS) * len(spoken_emotions)
    for character in CHARACTERS:
        assert {r["emotion"] for r in rows if r["character"] == character} == set(spoken_emotions)


def test_ids_name_the_character_and_emotion():
    ids = [r["id"] for r in variation_lines("fr")]
    assert "zahra_happy" in ids and len(ids) == len(set(ids))


def test_emotions_are_medium_and_questions_fixed():
    rows = {r["id"]: r for r in variation_lines("en")}
    assert rows["ali_sad"]["intensity"] == "medium"
    assert rows["ali_question"]["intensity"] == "fixed"


def test_rows_use_the_language_sentence():
    assert all(r["text"] == VARIATION_SENTENCE["tr"] for r in variation_lines("tr"))
