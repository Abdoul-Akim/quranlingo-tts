import pytest

from project_config import LANGUAGES
from text_rules import HONORIFIC, prepare_text


# Existing English behaviour (already implemented, kept as a safety net).
def test_honorific_before_question_mark():
    assert prepare_text("Who criticized the Prophet ﷺ?", "en") == "Who criticized the Prophet, peace be upon him?"


def test_honorific_mid_sentence():
    assert prepare_text("the Prophet ﷺ from praying", "en") == "the Prophet, peace be upon him, from praying"


def test_honorific_at_the_end():
    assert prepare_text("the truthfulness of the Prophet ﷺ", "en") == "the truthfulness of the Prophet, peace be upon him"


# New: every app language has a spoken honorific.
@pytest.mark.parametrize("language", LANGUAGES)
def test_every_language_has_an_honorific(language):
    assert HONORIFIC[language].strip()


def test_arabic_honorific_and_question_mark():
    assert prepare_text("كيف رد على من انتقد النبي ﷺ؟", "ar") == "كيف رد على من انتقد النبي، صلى الله عليه وسلم؟"


def test_urdu_honorific_and_full_stop():
    assert prepare_text("نبی ﷺ۔", "ur") == "نبی، صلی اللہ علیہ وسلم۔"


def test_hindi_honorific_and_danda():
    assert prepare_text("पैगंबर ﷺ।", "hi") == "पैगंबर, सल्लल्लाहु अलैहि वसल्लम।"


# New: a gloss in brackets is spoken, not dropped (VoxCPM2 treats brackets as instructions).
def test_brackets_become_commas():
    assert prepare_text("In what description was Jahannam (Hellfire) mentioned?", "en") == \
        "In what description was Jahannam, Hellfire, mentioned?"


def test_brackets_before_punctuation():
    assert prepare_text("a river in Jannah (Paradise).", "en") == "a river in Jannah, Paradise."


def test_no_brackets_left_anywhere():
    assert "(" not in prepare_text("Abundant good (a river (in Jannah))", "en")


# New: Turkish attaches case endings to the honorific symbol ("Peygamber ﷺ'i").
# Spoken, the ending belongs on the noun, with Turkish buffer letters (y, n) fixed up.
@pytest.mark.parametrize("written, spoken", [
    ("Peygamberimiz ﷺ'yi hor", "Peygamberimizi, sallallahu aleyhi ve sellem, hor"),
    ("Peygamber ﷺ'i", "Peygamberi, sallallahu aleyhi ve sellem"),
    ("Peygamberimiz ﷺ'e", "Peygamberimize, sallallahu aleyhi ve sellem"),
    ("Peygamberimiz ﷺ'in", "Peygamberimizin, sallallahu aleyhi ve sellem"),
    ("Nebi ﷺ'nin", "Nebinin, sallallahu aleyhi ve sellem"),
    ("Nebi ﷺ'ye", "Nebiye, sallallahu aleyhi ve sellem"),
    ("Nebi ﷺ’ye", "Nebiye, sallallahu aleyhi ve sellem"),  # typographic apostrophe
])
def test_turkish_suffix_moves_to_the_noun(written, spoken):
    assert prepare_text(written, "tr") == spoken


def test_symbol_in_brackets_is_still_spoken():
    assert prepare_text("el Profeta (ﷺ) dijo", "en") == "el Profeta, peace be upon him, dijo"
