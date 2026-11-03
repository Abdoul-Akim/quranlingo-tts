# Phase C: emotional variations of each locked base voice.
# Every character says the same neutral sentence in every emotion, so listeners compare only
# the emotion. Writes test_lines/variations_<lang>.csv (same columns as the test lines).
# Translations are drafts for native review.
#
# Run from the TTS folder:  python3 tools/variations.py
from pathlib import Path

from line_styles import EMOTIONS
from project_config import CHARACTERS, LANGUAGES

VARIATION_SENTENCE = {
    "en": "That's the end of today's lesson. See you tomorrow.",
    "fr": "C'est la fin de la leçon d'aujourd'hui. À demain.",
    "de": "Das ist das Ende der heutigen Lektion. Bis morgen.",
    "tr": "Bugünkü dersimizin sonuna geldik. Yarın görüşmek üzere.",
    "ar": "هذه نهاية درس اليوم. نراكم غدًا.",
    "hi": "आज का पाठ यहीं ख़त्म होता है। कल मिलते हैं।",
    "ur": "آج کا سبق یہیں ختم ہوتا ہے۔ کل ملتے ہیں۔",
}

# An answer option is not an emotion, so it has no variation.
SPOKEN_EMOTIONS = [e for e in EMOTIONS if e != "option"]


def variation_lines(language: str) -> list[dict]:
    return [
        {"id": f"{character}_{emotion}", "character": character, "emotion": emotion,
         "intensity": "fixed" if emotion == "question" else "medium", "source_ref": "",
         "text": VARIATION_SENTENCE[language]}
        for character in CHARACTERS
        for emotion in SPOKEN_EMOTIONS
    ]


if __name__ == "__main__":
    from make_test_lines import write_lines

    out_dir = Path(__file__).resolve().parents[1] / "test_lines"
    for language in LANGUAGES:
        write_lines(variation_lines(language), out_dir / f"variations_{language}.csv")
        print(f"Wrote test_lines/variations_{language}.csv")
