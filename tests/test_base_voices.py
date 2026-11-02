from collections import Counter

import pytest

from base_voices import jobs_for, take_path
from project_config import CHARACTERS, LANGUAGES


def test_english_has_more_takes_for_the_children():
    counts = Counter(job.character for job in jobs_for("en"))
    # Children: 3 wordings + the "from a female voice" method, 5 seeds each. Adults: 2 x 4.
    assert counts == {"ali": 20, "zahra": 20, "fatima": 8, "omar": 8}


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
