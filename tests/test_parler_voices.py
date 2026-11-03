from parler_voices import PARLER_LANGUAGES, jobs_for, parler_description
from project_config import CHARACTERS


def test_every_character_has_two_parler_descriptions():
    for character in CHARACTERS:
        assert parler_description(character, "v1") != parler_description(character, "v2")


def test_descriptions_end_with_the_clear_audio_phrase():
    # The model card says this phrase gives the cleanest recordings.
    for character in CHARACTERS:
        assert parler_description(character, "v1").endswith("very clear audio.")


def test_gender_matches_the_character():
    assert "male speaker" in parler_description("omar", "v1") and "female" not in parler_description("omar", "v1")
    assert "female speaker" in parler_description("fatima", "v1")


def test_children_are_young_and_high_pitched():
    for character in ("ali", "zahra"):
        d = parler_description(character, "v1")
        assert "young" in d and "high-pitched" in d


def test_parler_is_used_for_urdu_and_hindi_only():
    assert PARLER_LANGUAGES == ["ur", "hi"]


def test_jobs_cover_every_character_with_two_wordings_and_three_seeds():
    jobs = jobs_for("ur")
    assert len(jobs) == len(CHARACTERS) * 2 * 3
    assert {j.character for j in jobs} == set(CHARACTERS)
