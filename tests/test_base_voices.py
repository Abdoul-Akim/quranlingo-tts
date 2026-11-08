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
def test_other_languages_have_two_seeds_per_wording(language):
    counts = Counter(job.character for job in jobs_for(language))
    assert counts == {"ali": 8, "zahra": 8, "fatima": 4, "omar": 4}


def test_only_children_get_the_from_female_method():
    variants = {(job.character, job.variant) for job in jobs_for("en")}
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
