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

# Voice design descriptions, several wordings per character. Voice design results vary,
# so we try more than one wording and let listeners choose.
DESCRIPTIONS = {
    "ali": {
        "v1": "A 14-year-old boy, young teenage voice, light and slightly high, not yet deep, calm, serious and studious, warm and friendly",
        "v2": "A teenage boy around fourteen, clear youthful voice that has not fully broken, gentle, thoughtful and kind",
        "v3": "A young boy about fourteen years old, bright and clean voice, calm and confident, friendly",
    },
    "fatima": {
        "v1": "A woman in her late twenties, warm, nurturing and intelligent, calm, gentle and reassuring, slightly motherly",
        "v2": "A young woman around thirty, soft and kind voice, clear and composed, comforting and supportive",
    },
    "omar": {
        "v1": "A man around fifty, calm, wise and grounded, soft-spoken, warm and fatherly, steady and reassuring",
        "v2": "A middle-aged man of about fifty, deep, gentle and kind voice, slow and thoughtful, a beloved elder",
    },
    "zahra": {
        "v1": "A 10-year-old girl, child's voice, high and bright, bubbly, curious and full of energy",
        "v2": "A little girl around ten years old, lively and talkative, cheerful high-pitched child voice, playful",
        "v3": "A young girl about ten years old, sweet, animated and expressive voice, excited and curious",
    },
}

# Redesign after the owner's listening (2026-11-06): Fatima sounded like a kid or robotic,
# Omar not warm or fatherly enough, Ali either a man or a girl. English only until the owner
# picks, 8 seeds each.
REDESIGN_DESCRIPTIONS = {
    "ali": {
        "v4": "A boy of thirteen or fourteen whose voice is just starting to break, boyish and youthful, not a man and not a girl, calm and serious, friendly",
        "v5": "A schoolboy around fourteen reading aloud in class, young boyish voice, medium pitch, earnest and studious",
        "v6": "A teenage boy with a boyish voice and a slight youthful roughness, calm, warm and thoughtful",
    },
    "fatima": {
        "v3": "A woman of about thirty, a mother, warm and mature voice, medium pitch, natural and relaxed, gently smiling",
        "v4": "A grown woman around thirty, rich and warm mid-range voice, calm, caring and expressive, like a kind teacher",
        "v5": "A thirty-year-old mother speaking softly to her child, warm, natural and lively, not high-pitched",
    },
    "omar": {
        "v3": "A man around fifty, a loving father speaking to his children, warm and smiling voice, gentle and soft, calm and kind",
        "v4": "A fatherly man of about fifty, warm, friendly and caring voice, gently encouraging, like a grandfather telling a story by the fire, not deep or stern",
    },
    # Added 2026-11-08: the owner wants Zahra to sound clearly ten, not a little child.
    "zahra": {
        "v4": "A ten-year-old girl, a schoolgirl, clear and bright child voice, natural and not babyish, curious and lively",
        "v5": "A girl of about ten, older than a little child, lively and talkative, cheerful, expressive and natural",
        "v6": "A ten-year-old girl telling her friend about her day, animated and excited, natural child voice, medium high pitch",
    },
}
REDESIGN_SEEDS = {"en": [1, 2, 3, 4, 5, 6, 7, 8]}

# The wordings the owner chose in English (2026-11-08). The other languages use only these,
# three seeds each, with a native accent.
CHOSEN_WORDINGS = {"ali": ["v4", "v6"], "fatima": ["v3", "v4"], "omar": ["v3", "v4"], "zahra": ["v4", "v6"]}
OTHER_LANGUAGE_SEEDS = [1, 2, 3]

# Method 3 for the children: design a light adult female voice, then shift it toward the child
# (see tools/age_shift.py). Research suggests adult female voices are the closest adult start point.
FROM_FEMALE_DESCRIPTIONS = {
    "ali": "A young woman with a light, boyish voice, clear and calm, friendly",
    "zahra": "A young woman with a light, girlish, bright voice, cheerful and energetic",
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
    # Owner's picks 2026-11-08. No French Ali yet; fr omar/v3_seed2 rejected (sounds like a woman).
    "fr": {
        "fatima": ["fatima/v3_seed2.wav"],
        "omar": ["omar/v4_seed1.wav", "omar/v4_seed2.wav", "omar/v4_seed3.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v6_seed2.wav"],
    },
    "ar": {
        "ali": ["ali/v6_seed1.wav", "ali/v6_seed3.wav"],
        "fatima": ["fatima/v3_seed2.wav", "fatima/v4_seed1.wav", "fatima/v4_seed2.wav", "fatima/v4_seed3.wav"],
        "omar": ["omar/v3_seed1.wav", "omar/v3_seed2.wav", "omar/v4_seed1.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v6_seed2.wav"],
    },
}

# Characters who keep one voice in every language: the English voice is cloned into the others
# (owner, 2026-11-08: the English Ali speaking French and Arabic beat every native Ali take).
SAME_VOICE_EVERYWHERE = {"ali": "en"}

# Typical speaking pitch (median, in Hz) we aim for. Used to rank takes automatically.
# Set from the owner's English picks on 2026-11-08 (see tests/test_base_voices.py).
TARGET_PITCH_HZ = {
    "ali": (185, 225),
    "fatima": (175, 215),
    "omar": (120, 165),
    "zahra": (250, 345),
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
