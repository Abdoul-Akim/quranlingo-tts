# Which base voice takes to design, per language: character, description wording and seed.
# Kept apart from the engine scripts so it can be tested without loading a model.
from typing import NamedTuple

from project_config import CHARACTERS, DESCRIPTIONS, LANGUAGE_NAMES, SAME_VOICE_EVERYWHERE, SEEDS


class Job(NamedTuple):
    character: str
    variant: str
    description: str
    seed: int


def jobs_for(language: str) -> list[Job]:
    # Characters with the English voice everywhere (Ali) need no takes in the other languages.
    accent = "" if language == "en" else f", speaking {LANGUAGE_NAMES[language]} with a native accent"
    return [
        Job(character, variant, description + accent, seed)
        for character in CHARACTERS if SAME_VOICE_EVERYWHERE.get(character, language) == language
        for variant, description in DESCRIPTIONS[character].items()
        for seed in SEEDS[language]
    ]


def take_path(job: Job) -> str:
    # Relative to outputs/base_voices/<lang>/, e.g. "ali/v4_seed1.wav".
    return f"{job.character}/{job.variant}_seed{job.seed}.wav"
