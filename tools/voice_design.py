# How the base voices are designed (VoxCPM2 voice design) and judged automatically.
# Used by tools/base_voices.py (which takes to make) and tools/rank_takes.py (pitch filter).

# Voice design descriptions: the two wordings per character the owner chose in English
# (2026-11-08). Each one goes in brackets in front of the text; the other languages add
# ", speaking <language> with a native accent". Older wordings (v1, v2, v5, a light female
# voice shifted younger) are in Git history; the English Zahra pick zahra/v2_seed5 came from v2:
# "A little girl around ten years old, lively and talkative, cheerful high-pitched child voice, playful".
DESCRIPTIONS = {
    "ali": {
        "v4": "A boy of thirteen or fourteen whose voice is just starting to break, boyish and youthful, not a man and not a girl, calm and serious, friendly",
        "v6": "A teenage boy with a boyish voice and a slight youthful roughness, calm, warm and thoughtful",
    },
    "fatima": {
        "v3": "A woman of about thirty, a mother, warm and mature voice, medium pitch, natural and relaxed, gently smiling",
        "v4": "A grown woman around thirty, rich and warm mid-range voice, calm, caring and expressive, like a kind teacher",
    },
    "omar": {
        "v3": "A man around fifty, a loving father speaking to his children, warm and smiling voice, gentle and soft, calm and kind",
        "v4": "A fatherly man of about fifty, warm, friendly and caring voice, gently encouraging, like a grandfather telling a story by the fire, not deep or stern",
    },
    "zahra": {
        "v4": "A ten-year-old girl, a schoolgirl, clear and bright child voice, natural and not babyish, curious and lively",
        "v6": "A ten-year-old girl telling her friend about her day, animated and excited, natural child voice, medium high pitch",
    },
}

# Seeds per language (each seed is one take of each wording). English had the most takes, since
# that is where the wordings were chosen; tr, hi and ur got more where few passed the pitch filter.
SEEDS = {
    "en": [1, 2, 3, 4, 5, 6, 7, 8],
    "fr": [1, 2, 3], "ar": [1, 2, 3], "de": [1, 2, 3],
    "tr": [1, 2, 3, 4, 5, 6], "hi": [1, 2, 3, 4, 5, 6], "ur": [1, 2, 3, 4, 5, 6],
}

# Typical speaking pitch (median, in Hz) we aim for. Used to rank takes automatically.
# Set from the owner's English picks on 2026-11-08 (see tests/test_base_voices.py).
TARGET_PITCH_HZ = {
    "ali": (185, 225),
    "fatima": (200, 240),  # from the fr, ar and de picks (2026-11-08)
    "omar": (100, 160),
    "zahra": (245, 295),
}
