# What the listening site shows testers about each clip, in the page's own language:
# the character's name and age, "Line 3 of 16", and how a line should sound.
# Translations other than English are drafts for native review (2026-11-15).

CHARACTER_LABELS = {
    "en": {"ali": "Ali (boy, 14)", "fatima": "Fatima (woman, 29)", "omar": "Omar (man, 50)", "zahra": "Zahra (girl, 10)"},
    "fr": {"ali": "Ali (garçon, 14 ans)", "fatima": "Fatima (femme, 29 ans)", "omar": "Omar (homme, 50 ans)", "zahra": "Zahra (fille, 10 ans)"},
    "de": {"ali": "Ali (Junge, 14)", "fatima": "Fatima (Frau, 29)", "omar": "Omar (Mann, 50)", "zahra": "Zahra (Mädchen, 10)"},
    "tr": {"ali": "Ali (erkek çocuk, 14)", "fatima": "Fatima (kadın, 29)", "omar": "Omar (erkek, 50)", "zahra": "Zahra (kız çocuk, 10)"},
    "ar": {"ali": "علي (فتى، 14 سنة)", "fatima": "فاطمة (امرأة، 29 سنة)", "omar": "عمر (رجل، 50 سنة)", "zahra": "زهراء (فتاة، 10 سنوات)"},
    "hi": {"ali": "अली (लड़का, 14)", "fatima": "फ़ातिमा (महिला, 29)", "omar": "उमर (पुरुष, 50)", "zahra": "ज़हरा (लड़की, 10)"},
    "ur": {"ali": "علی (لڑکا، 14)", "fatima": "فاطمہ (خاتون، 29)", "omar": "عمر (مرد، 50)", "zahra": "زہرا (لڑکی، 10)"},
}

LINE_LABELS = {
    "en": "Line {n} of {total}",
    "fr": "Phrase {n} sur {total}",
    "de": "Satz {n} von {total}",
    "tr": "Cümle {n} / {total}",
    "ar": "الجملة {n} من {total}",
    "hi": "वाक्य {n} / {total}",
    "ur": "جملہ {n} از {total}",
}

# "Should sound: <emotion> (<intensity>)"; questions and options have a fixed style instead.
HINTS = {
    "en": "Should sound: {emotion} ({intensity})",
    "fr": "Ton attendu : {emotion} (intensité {intensity})",
    "de": "Soll klingen: {emotion} ({intensity})",
    "tr": "Nasıl duyulmalı: {emotion} ({intensity})",
    "ar": "النبرة المطلوبة: {emotion} ({intensity})",
    "hi": "कैसा सुनाई देना चाहिए: {emotion} ({intensity})",
    "ur": "کیسا سنائی دینا چاہیے: {emotion} ({intensity})",
}
FIXED_HINTS = {
    "en": "Should sound: {style}",
    "fr": "Ton attendu : {style}",
    "de": "Soll klingen: {style}",
    "tr": "Nasıl duyulmalı: {style}",
    "ar": "النبرة المطلوبة: {style}",
    "hi": "कैसा सुनाई देना चाहिए: {style}",
    "ur": "کیسا سنائی دینا چاہیے: {style}",
}

EMOTIONS = {
    "en": {"neutral": "neutral", "warm": "warm", "happy": "happy", "excited": "excited", "sad": "sad",
           "calm": "calm", "curious": "curious", "serious": "serious",
           "question": "a warm, clear question", "option": "a warm, clear answer option"},
    "fr": {"neutral": "neutre", "warm": "chaleureux", "happy": "joyeux", "excited": "enthousiaste", "sad": "triste",
           "calm": "calme", "curious": "curieux", "serious": "sérieux",
           "question": "une question chaleureuse et claire", "option": "une proposition de réponse chaleureuse et claire"},
    "de": {"neutral": "neutral", "warm": "herzlich", "happy": "fröhlich", "excited": "begeistert", "sad": "traurig",
           "calm": "ruhig", "curious": "neugierig", "serious": "ernst",
           "question": "eine herzliche, klare Frage", "option": "eine herzliche, klare Antwortmöglichkeit"},
    "tr": {"neutral": "nötr", "warm": "sıcak", "happy": "mutlu", "excited": "heyecanlı", "sad": "üzgün",
           "calm": "sakin", "curious": "meraklı", "serious": "ciddi",
           "question": "sıcak ve net bir soru", "option": "sıcak ve net bir cevap seçeneği"},
    "ar": {"neutral": "محايدة", "warm": "دافئة", "happy": "سعيدة", "excited": "متحمسة", "sad": "حزينة",
           "calm": "هادئة", "curious": "فضولية", "serious": "جادة",
           "question": "سؤال دافئ وواضح", "option": "خيار إجابة دافئ وواضح"},
    "hi": {"neutral": "सामान्य", "warm": "आत्मीय", "happy": "खुश", "excited": "उत्साहित", "sad": "उदास",
           "calm": "शांत", "curious": "जिज्ञासु", "serious": "गंभीर",
           "question": "एक आत्मीय, साफ़ सवाल", "option": "जवाब का एक आत्मीय, साफ़ विकल्प"},
    "ur": {"neutral": "عام", "warm": "گرم جوش", "happy": "خوش", "excited": "پرجوش", "sad": "اداس",
           "calm": "پرسکون", "curious": "متجسس", "serious": "سنجیدہ",
           "question": "ایک گرم جوش، واضح سوال", "option": "جواب کا ایک گرم جوش، واضح انتخاب"},
}

INTENSITIES = {
    "en": {"low": "low", "medium": "medium", "high": "high"},
    "fr": {"low": "faible", "medium": "moyenne", "high": "forte"},
    "de": {"low": "leicht", "medium": "mittel", "high": "stark"},
    "tr": {"low": "hafif", "medium": "orta", "high": "güçlü"},
    "ar": {"low": "خفيفة", "medium": "متوسطة", "high": "قوية"},
    "hi": {"low": "हल्का", "medium": "मध्यम", "high": "तेज़"},
    "ur": {"low": "ہلکا", "medium": "درمیانہ", "high": "تیز"},
}


def character_label(character: str, language: str) -> str:
    return CHARACTER_LABELS[language][character]


def line_label(number: int, total: int, language: str) -> str:
    return LINE_LABELS[language].format(n=number, total=total)


def hint(emotion: str, intensity: str, language: str) -> str:
    if emotion in ("question", "option"):
        return FIXED_HINTS[language].format(style=EMOTIONS[language][emotion])
    return HINTS[language].format(emotion=EMOTIONS[language][emotion], intensity=INTENSITIES[language][intensity])
