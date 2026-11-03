# Character descriptions for Indic Parler-TTS (Apache-2.0), the only open candidate for Urdu.
# Parler takes a plain sentence about the speaker, with the words its model card uses:
# gender, young, pitch (high-pitched, low-pitched), speed, expressive or monotone, and
# "very clear audio" for the cleanest recording. It cannot clone a reference voice.
from base_voices import Job
from project_config import CHARACTERS

PARLER_LANGUAGES = ["ur", "hi"]
SEEDS = [1, 2, 3]
CLEAR = "The recording is of very high quality, with very clear audio."

PARLER_DESCRIPTIONS = {
    "ali": {
        "v1": "A young male speaker with a slightly high-pitched voice delivers calm, clear and slightly expressive speech at a moderate speed.",
        "v2": "A young male speaker with a high-pitched, youthful voice speaks thoughtfully and kindly at a moderate pace.",
    },
    "fatima": {
        "v1": "A female speaker with a warm, moderate-pitched voice delivers gentle, slightly expressive and reassuring speech at a moderate speed.",
        "v2": "A female speaker with a soft, kind voice speaks calmly and clearly at a slightly slow pace, sounding nurturing and supportive.",
    },
    "omar": {
        "v1": "A male speaker with a low-pitched voice delivers calm, wise and slightly expressive speech at a slightly slow speed.",
        "v2": "A male speaker with a deep, gentle voice speaks softly and thoughtfully at a slow pace, sounding warm and fatherly.",
    },
    "zahra": {
        "v1": "A young female speaker with a very high-pitched voice delivers lively, animated and very expressive speech at a slightly fast speed.",
        "v2": "A young female speaker with a high-pitched, bright voice speaks cheerfully and curiously with lots of energy.",
    },
}


def parler_description(character: str, variant: str) -> str:
    return f"{PARLER_DESCRIPTIONS[character][variant]} {CLEAR}"


def jobs_for(language: str) -> list[Job]:
    return [
        Job(character, variant, parler_description(character, variant), seed)
        for character in CHARACTERS
        for variant in PARLER_DESCRIPTIONS[character]
        for seed in SEEDS
    ]
