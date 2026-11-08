# Which base voice takes to design, per language: character, description wording and seed.
# Kept apart from the engine scripts so it can be tested without loading a model.
from typing import NamedTuple

from project_config import (
    CHARACTERS, CHOSEN_WORDINGS, DESCRIPTIONS, FROM_FEMALE_DESCRIPTIONS, LANGUAGE_NAMES, OTHER_LANGUAGE_SEEDS,
    REDESIGN_DESCRIPTIONS, REDESIGN_SEEDS,
)

# English is where we choose the method, so it gets more takes than the other languages.
CHILD_SEEDS = {"en": [1, 2, 3, 4, 5]}
ADULT_SEEDS = {"en": [1, 2, 3, 4]}
DEFAULT_SEEDS = [1, 2]


class Job(NamedTuple):
    character: str
    variant: str
    description: str
    seed: int


def jobs_for(language: str) -> list[Job]:
    if language != "en":
        return _chosen_wordings_jobs(language)
    jobs = []
    for character in CHARACTERS:
        child = character in FROM_FEMALE_DESCRIPTIONS
        seeds = (CHILD_SEEDS if child else ADULT_SEEDS).get(language, DEFAULT_SEEDS)
        variants = dict(DESCRIPTIONS[character])
        if child:
            variants["from_female"] = FROM_FEMALE_DESCRIPTIONS[character]
        for variant, description in variants.items():
            for seed in seeds:
                jobs.append(Job(character, variant, description, seed))
        for variant, description in REDESIGN_DESCRIPTIONS.get(character, {}).items():
            for seed in REDESIGN_SEEDS.get(language, []):
                jobs.append(Job(character, variant, description, seed))
    return jobs


def _chosen_wordings_jobs(language: str) -> list[Job]:
    # Since 2026-11-08 the other languages use only the wordings the owner chose in English.
    accent = f", speaking {LANGUAGE_NAMES[language]} with a native accent"
    return [
        Job(character, variant, REDESIGN_DESCRIPTIONS[character][variant] + accent, seed)
        for character in CHARACTERS
        for variant in CHOSEN_WORDINGS[character]
        for seed in OTHER_LANGUAGE_SEEDS
    ]


def take_path(job: Job) -> str:
    # Relative to outputs/base_voices/<lang>/, e.g. "ali/v1_seed1.wav".
    return f"{job.character}/{job.variant}_seed{job.seed}.wav"
