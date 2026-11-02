# Shared settings for the English character voices, used by several scripts.

# Generation settings chosen by ear from the quality sweep (2026-10-24).
# 50 timesteps removes the metallic buzz; cfg 1.5 sounds more natural than 2.0.
INFERENCE_TIMESTEPS = 50
CFG_VALUE = 1.5

# Bump this whenever the descriptions change, so new takes go to a new folder.
# v1: young (mid twenties) and older (sixties, late fifties).
# v2: young and active, middle aged (mid forties).
VOICES_VERSION = "v2"

# The approved descriptions. Each one goes in brackets in front of the text.
VOICES = {
    "young_male": "A man in his mid twenties, active and energetic, friendly, clear and bright, medium pitch",
    "young_female": "A woman in her mid twenties, active and energetic, cheerful and clear, light and expressive",
    "middle_aged_male": "A middle aged man in his mid forties, warm, steady and clear, a kind storyteller",
    "middle_aged_female": "A middle aged woman in her mid forties, gentle and warm, calm and reassuring, like a kind teacher",
}

# Every character speaks the same calm passage, so only the voice differs.
PASSAGE = (
    "Hello, and welcome. Today we are going to read a short story together. "
    "Are you ready? Listen carefully and take your time. There is no rush at all."
)
