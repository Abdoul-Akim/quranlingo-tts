# How each engine is told the emotion of a line (temporary mapping; step 4 refines it).
#   VoxCPM2:    a style instruction in brackets before the text
#   Chatterbox: two dials, exaggeration and cfg_weight, set by intensity only
from project_config import ENGINE_LANGUAGES
from text_rules import prepare_text

EMOTIONS = ["neutral", "warm", "happy", "excited", "sad", "calm", "curious", "serious", "question", "option"]

VOXCPM_STYLES = {
    "neutral": "clear and even, informative",
    "warm": "warm and welcoming, friendly",
    "happy": "happy and cheerful, smiling",
    "excited": "excited and energetic, lively",
    "sad": "sad and gentle, slightly slower",
    "calm": "calm and soothing, slow and relaxed",
    "curious": "curious and wondering, inviting",
    "serious": "serious and firm, steady",
    "question": "warm and clear, like a friendly teacher",
    "option": "warm and clear, like a friendly teacher",
}
# Neutral and the fixed question style never get an intensity word.
INTENSITY_WORDS = {"low": "slightly ", "medium": "", "high": "very ", "fixed": ""}

# exaggeration: how dramatic (default 0.5). cfg_weight: how strictly it follows the
# reference pacing; lower suits expressive speech (default 0.5).
CHATTERBOX_DIALS = {
    "low": {"exaggeration": 0.4, "cfg_weight": 0.5},
    "medium": {"exaggeration": 0.6, "cfg_weight": 0.4},
    "high": {"exaggeration": 0.8, "cfg_weight": 0.3},
    "fixed": {"exaggeration": 0.5, "cfg_weight": 0.5},
}

# Languages an engine does not officially support but we try anyway, clearly marked.
EXPERIMENTAL_LANGUAGES = {"voxcpm2": ["ur"]}


def voxcpm_text(line: dict, language: str) -> str:
    word = "" if line["emotion"] == "neutral" else INTENSITY_WORDS[line["intensity"]]
    return f"({word}{VOXCPM_STYLES[line['emotion']]}){prepare_text(line['text'], language)}"


def chatterbox_args(line: dict) -> dict:
    return dict(CHATTERBOX_DIALS[line["intensity"]])


def engines_for(language: str) -> list[str]:
    return sorted(
        engine for engine, languages in ENGINE_LANGUAGES.items()
        if language in languages or language in EXPERIMENTAL_LANGUAGES.get(engine, [])
    )
