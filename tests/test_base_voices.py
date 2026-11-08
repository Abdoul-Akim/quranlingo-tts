from collections import Counter

import pytest

from base_voices import jobs_for, take_path
from project_config import CHARACTERS, LANGUAGES


def test_english_uses_the_chosen_wordings_with_eight_seeds():
    # The older English wordings (v1, v2, v5 and the "from a female voice" method) were dropped
    # on 2026-11-09; their takes stay on disk and in Git history.
    jobs = jobs_for("en")
    assert Counter(job.character for job in jobs) == {"ali": 16, "fatima": 16, "omar": 16, "zahra": 16}
    assert {(j.character, j.variant) for j in jobs} == {
        ("ali", "v4"), ("ali", "v6"), ("fatima", "v3"), ("fatima", "v4"),
        ("omar", "v3"), ("omar", "v4"), ("zahra", "v4"), ("zahra", "v6"),
    }


@pytest.mark.parametrize("language", [l for l in LANGUAGES if l != "en"])
def test_other_languages_use_only_the_wordings_the_owner_chose_in_english(language):
    # 2026-11-08: two chosen wordings per character, three seeds each (six in tr, hi and ur,
    # where few takes passed the filter, so testers get more choice). Ali has the English voice.
    jobs = jobs_for(language)
    per_character = 12 if language in ("tr", "hi", "ur") else 6
    assert Counter(job.character for job in jobs) == {"zahra": per_character, "fatima": per_character, "omar": per_character}
    assert {(j.character, j.variant) for j in jobs} == {
        ("fatima", "v3"), ("fatima", "v4"), ("omar", "v3"), ("omar", "v4"), ("zahra", "v4"), ("zahra", "v6"),
    }


def test_non_english_descriptions_ask_for_a_native_accent():
    assert all("native accent" not in job.description for job in jobs_for("en"))
    assert all("speaking Turkish with a native accent" in job.description for job in jobs_for("tr"))


def test_every_job_has_a_unique_file():
    paths = [take_path(job) for job in jobs_for("en")]
    assert len(paths) == len(set(paths))
    assert paths[0] == "ali/v4_seed1.wav"


def test_characters_come_in_the_fixed_order():
    seen = list(dict.fromkeys(job.character for job in jobs_for("en")))
    assert seen == CHARACTERS


def test_fatima_target_pitch_excludes_the_childish_takes():
    # The owner heard the 244 Hz pick as too young (2026-11-06).
    from voice_design import TARGET_PITCH_HZ
    low, high = TARGET_PITCH_HZ["fatima"]
    assert not low <= 244 <= high


def test_target_pitch_follows_the_owners_english_choices():
    # Measured on the owner's picks (2026-11-08): Ali 204 and 215 Hz, Omar 141 and 158 Hz,
    # Zahra 275 and 280 Hz (her 341 Hz English pick stays chosen by ear, but the other
    # languages showed higher takes are turned down). Ali at 233 Hz sounded like a girl.
    from voice_design import TARGET_PITCH_HZ
    inside = lambda c, hz: TARGET_PITCH_HZ[c][0] <= hz <= TARGET_PITCH_HZ[c][1]
    assert inside("ali", 204) and inside("ali", 215) and not inside("ali", 233)
    assert inside("omar", 141) and inside("omar", 158)
    assert all(inside("zahra", hz) for hz in (275, 280))


def test_target_pitch_follows_the_owners_french_arabic_and_german_choices():
    # Measured 2026-11-08. Zahra: every take above 290 Hz was turned down (11 of 11), picks 249 to 289.
    # Fatima: picks mostly 210 to 239, takes at 135 to 194 Hz turned down. Omar: picks 103 to 143,
    # takes at 94 and 99 Hz turned down.
    from voice_design import TARGET_PITCH_HZ
    inside = lambda c, hz: TARGET_PITCH_HZ[c][0] <= hz <= TARGET_PITCH_HZ[c][1]
    assert all(inside("zahra", hz) for hz in (249, 259, 275, 276, 280, 289))
    assert not any(inside("zahra", hz) for hz in (305, 308, 322, 346))
    assert all(inside("fatima", hz) for hz in (210, 217, 223, 236, 239))
    assert not any(inside("fatima", hz) for hz in (165, 192, 194))
    assert all(inside("omar", hz) for hz in (103, 112, 121, 136, 143))
    assert not any(inside("omar", hz) for hz in (94, 99))
