# Shared settings for the QuranLingo characters and languages, used by every engine script.
# Translations here are drafts and must be checked by a native speaker before release.

# Languages used in the app, in the order we work on them.
LANGUAGES = ["en", "fr", "de", "tr", "ar", "hi", "ur"]

LANGUAGE_NAMES = {
    "en": "English", "fr": "French", "de": "German", "tr": "Turkish",
    "ar": "Arabic", "hi": "Hindi", "ur": "Urdu",
}

# Characters always appear in this order.
CHARACTERS = ["ali", "fatima", "omar", "zahra"]

CHARACTER_LABELS = {
    "ali": "Ali (boy, 14)",
    "fatima": "Fatima (woman, 29)",
    "omar": "Omar (man, 50)",
    "zahra": "Zahra (girl, 10)",
}

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

# Takes the owner shortlisted by ear, per language and character. The first one becomes the
# reference voice in voices/<lang>/, and testers choose among all of them. Characters missing
# here keep the automatic pick (tools/rank_takes.py).
OWNER_SHORTLIST = {
    "en": {
        "ali": ["ali/v6_seed2.wav", "ali/v4_seed6.wav"],
        "fatima": ["fatima/v3_seed3.wav", "fatima/v3_seed2.wav", "fatima/v4_seed6.wav"],
        "omar": ["omar/v4_seed5.wav", "omar/v3_seed2.wav"],
        "zahra": ["zahra/v4_seed7.wav", "zahra/v6_seed4.wav", "zahra/v2_seed5.wav"],
    },
    # Owner's picks 2026-11-08. The take designed for Omar as omar/v3_seed2 sounds like a woman,
    # so it is Fatima's French voice.
    "fr": {
        "fatima": ["omar/v3_seed2.wav", "fatima/v3_seed2.wav"],
        "omar": ["omar/v4_seed1.wav", "omar/v4_seed2.wav", "omar/v4_seed3.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v6_seed2.wav"],
    },
    "ar": {
        "fatima": ["fatima/v3_seed2.wav", "fatima/v4_seed1.wav", "fatima/v4_seed2.wav", "fatima/v4_seed3.wav"],
        "omar": ["omar/v3_seed1.wav", "omar/v3_seed2.wav", "omar/v4_seed1.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v6_seed2.wav"],
    },
    "de": {
        "fatima": ["fatima/v3_seed2.wav", "fatima/v4_seed2.wav", "fatima/v4_seed3.wav"],
        "omar": ["omar/v3_seed2.wav", "omar/v3_seed3.wav", "omar/v4_seed2.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v4_seed1.wav"],
    },
}

# Characters who keep one voice in every language: the English voice is cloned into the others
# (owner, 2026-11-08: the English Ali speaking French and Arabic beat every native Ali take).
SAME_VOICE_EVERYWHERE = {"ali": "en"}

# Typical speaking pitch (median, in Hz) we aim for. Used to rank takes automatically.
# Set from the owner's English picks on 2026-11-08 (see tests/test_base_voices.py).
TARGET_PITCH_HZ = {
    "ali": (185, 225),
    "fatima": (200, 240),  # from the fr, ar and de picks (2026-11-08)
    "omar": (100, 160),
    "zahra": (245, 295),
}

# The calm reference passage every voice reads. Same meaning in every language.
PASSAGES = {
    "en": "Hello, and welcome. Today we are going to read a short story together. Are you ready? Listen carefully and take your time. There is no rush at all.",
    "fr": "Bonjour et bienvenue. Aujourd'hui, nous allons lire ensemble une petite histoire. On y va ? Écoute bien et prends ton temps. Rien ne presse.",
    "de": "Hallo und herzlich willkommen. Heute lesen wir zusammen eine kurze Geschichte. Bist du bereit? Hör gut zu und nimm dir Zeit. Es gibt überhaupt keine Eile.",
    "tr": "Merhaba, hoş geldin. Bugün birlikte kısa bir hikâye okuyacağız. Hazır mısın? Dikkatlice dinle ve acele etme. Hiç acelemiz yok.",
    "ar": "مرحبًا، وأهلًا وسهلًا بكم. اليوم سنقرأ معًا قصة قصيرة. هل نبدأ؟ استمعوا جيدًا وخذوا وقتكم، فلا داعي للعجلة أبدًا.",
    "hi": "नमस्ते, और आपका स्वागत है। आज हम साथ मिलकर एक छोटी सी कहानी पढ़ेंगे। क्या आप तैयार हैं? ध्यान से सुनिए और अपना समय लीजिए। कोई जल्दी नहीं है।",
    "ur": "السلام علیکم، اور خوش آمدید۔ آج ہم مل کر ایک چھوٹی سی کہانی پڑھیں گے۔ کیا آپ تیار ہیں؟ غور سے سنیے اور اپنا وقت لیجیے۔ کوئی جلدی نہیں ہے۔",
}

# Engines that officially support each language (checked 2026-10-24 and 2026-11-02).
# VoxCPM2 is also tried on Urdu as an untested experiment.
ENGINE_LANGUAGES = {
    "voxcpm2": ["en", "fr", "de", "tr", "ar", "hi"],
    "chatterbox": ["en", "fr", "de", "tr", "ar", "hi"],
}
