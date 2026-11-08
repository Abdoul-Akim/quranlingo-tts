from collections import Counter

import pytest

from base_voices import jobs_for, take_path
from project_config import CHARACTERS, LANGUAGES


def test_english_has_more_takes_for_the_children():
    counts = Counter(job.character for job in jobs_for("en"))
    # Children: 3 wordings + the "from a female voice" method, 5 seeds each. Adults: 2 x 4.
    # Plus the 2026-11-08 redesign (English only): Ali, Fatima and Zahra 3 wordings, Omar 2, 8 seeds each.
    assert counts == {"ali": 20 + 24, "zahra": 20 + 24, "fatima": 8 + 24, "omar": 8 + 16}


def test_the_redesign_adds_new_wordings_without_touching_the_old_takes():
    variants = {(job.character, job.variant, job.seed) for job in jobs_for("en")}
    assert ("ali", "v6", 8) in variants and ("fatima", "v5", 8) in variants and ("omar", "v4", 8) in variants
    assert ("fatima", "v1", 4) in variants and ("fatima", "v1", 5) not in variants


@pytest.mark.parametrize("language", [l for l in LANGUAGES if l != "en"])
def test_other_languages_use_only_the_wordings_the_owner_chose_in_english(language):
    # 2026-11-08: two chosen wordings per character, three seeds each, no older wordings.
    jobs = jobs_for(language)
    assert Counter(job.character for job in jobs) == {"ali": 6, "zahra": 6, "fatima": 6, "omar": 6}
    assert {(j.character, j.variant) for j in jobs} == {
        ("ali", "v4"), ("ali", "v6"), ("fatima", "v3"), ("fatima", "v4"),
        ("omar", "v3"), ("omar", "v4"), ("zahra", "v4"), ("zahra", "v6"),
    }


def test_only_children_get_the_from_female_method():
    variants = {(job.character, job.variant) for job in jobs_for("en")}  # English only now
    assert ("ali", "from_female") in variants and ("zahra", "from_female") in variants
    assert not any(v == "from_female" for c, v in variants if c in ("fatima", "omar"))


def test_non_english_descriptions_ask_for_a_native_accent():
    assert all("native accent" not in job.description for job in jobs_for("en"))
    assert all("speaking Turkish with a native accent" in job.description for job in jobs_for("tr"))


def test_every_job_has_a_unique_file():
    paths = [take_path(job) for job in jobs_for("en")]
    assert len(paths) == len(set(paths))
    assert paths[0] == "ali/v1_seed1.wav"


def test_characters_come_in_the_fixed_order():
    seen = list(dict.fromkeys(job.character for job in jobs_for("en")))
    assert seen == CHARACTERS


def test_fatima_target_pitch_excludes_the_childish_takes():
    # The owner heard the 244 Hz pick as too young (2026-11-06).
    from project_config import TARGET_PITCH_HZ
    low, high = TARGET_PITCH_HZ["fatima"]
    assert 170 <= low and high <= 215


def test_target_pitch_follows_the_owners_english_choices():
    # Measured on the owner's picks (2026-11-08): Ali 204 and 215 Hz, Omar 141 and 158 Hz,
    # Zahra 275, 280 and 341 Hz. Ali at 233 Hz sounded like a girl.
    from project_config import TARGET_PITCH_HZ
    inside = lambda c, hz: TARGET_PITCH_HZ[c][0] <= hz <= TARGET_PITCH_HZ[c][1]
    assert inside("ali", 204) and inside("ali", 215) and not inside("ali", 233)
    assert inside("omar", 141) and inside("omar", 158)
    assert all(inside("zahra", hz) for hz in (275, 280, 341))


def test_target_pitch_follows_the_owners_french_arabic_and_german_choices():
    # Measured 2026-11-08. Zahra: every take above 290 Hz was turned down (11 of 11), picks 249 to 289.
    # Fatima: picks mostly 210 to 239, takes at 135 to 194 Hz turned down. Omar: picks 103 to 143,
    # takes at 94 and 99 Hz turned down.
    from project_config import TARGET_PITCH_HZ
    inside = lambda c, hz: TARGET_PITCH_HZ[c][0] <= hz <= TARGET_PITCH_HZ[c][1]
    assert all(inside("zahra", hz) for hz in (249, 259, 275, 276, 280, 289))
    assert not any(inside("zahra", hz) for hz in (305, 308, 322, 346))
    assert all(inside("fatima", hz) for hz in (210, 217, 223, 236, 239))
    assert not any(inside("fatima", hz) for hz in (165, 192, 194))
    assert all(inside("omar", hz) for hz in (103, 112, 121, 136, 143))
    assert not any(inside("omar", hz) for hz in (94, 99))
