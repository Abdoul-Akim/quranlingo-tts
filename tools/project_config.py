# Shared facts about the QuranLingo characters and languages, used by every engine script.
# How voices are designed and judged: tools/voice_design.py. The owner's choices: tools/owner_choices.py.
# Translations here are drafts and must be checked by a native speaker before release.

# Languages used in the app, in the order we work on them.
LANGUAGES = ["en", "fr", "de", "tr", "ar", "hi", "ur"]

LANGUAGE_NAMES = {
    "en": "English", "fr": "French", "de": "German", "tr": "Turkish",
    "ar": "Arabic", "hi": "Hindi", "ur": "Urdu",
}

# Characters always appear in this order.
CHARACTERS = ["ali", "fatima", "omar", "zahra"]

# Their names and ages as shown on the listening site, per language: tools/ui_text.py.

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
