# Text rules applied before any engine speaks a line, so every engine gets the same text.
import re

# How the honorific symbol is spoken, per language.
# Drafts to be confirmed by QuranLingo's team (only English was decided by the owner).
HONORIFIC = {
    "en": "peace be upon him",
    "fr": "paix et salut sur lui",
    "de": "Allahs Segen und Frieden auf ihm",
    "tr": "sallallahu aleyhi ve sellem",
    "ar": "صلى الله عليه وسلم",
    "hi": "सल्लल्लाहु अलैहि वसल्लम",
    "ur": "صلی اللہ علیہ وسلم",
}

# Arabic script uses its own comma.
COMMA = {"ar": "،", "ur": "،"}

# Sentence punctuation in all our scripts: Latin, Arabic and Urdu (؟ ، ۔), Hindi (।).
PUNCTUATION = r"?.!,;:؟،۔।"


TURKISH_VOWELS = "aeıioöuüâîû"


def _turkish_suffix_to_noun(match: re.Match) -> str:
    # Turkish writes the case ending after the symbol: "Peygamber ﷺ'i". Spoken, it belongs on
    # the noun ("Peygamberi"), and the buffer letter depends on how the noun ends:
    # after a consonant drop a leading y or n ("ﷺ'yi" gives "Peygamberimizi"),
    # after a vowel keep it, or add one ("Nebi ﷺ'e" would give "Nebiye").
    noun, suffix = match.group(1), match.group(2)
    ends_in_vowel = noun[-1].lower() in TURKISH_VOWELS
    if not ends_in_vowel and len(suffix) > 1 and suffix[0] in "yn" and suffix[1] in TURKISH_VOWELS:
        suffix = suffix[1:]
    elif ends_in_vowel and suffix[0] in TURKISH_VOWELS:
        suffix = ("n" if suffix in ("in", "ın", "un", "ün") else "y") + suffix
    return f"{noun}{suffix} ﷺ"


def prepare_text(text: str, language: str) -> str:
    comma = COMMA.get(language, ",")

    # A gloss in brackets is spoken as a short aside: "Jahannam (Hellfire) is" becomes
    # "Jahannam, Hellfire, is". VoxCPM2 would otherwise treat it as an instruction and drop it.
    # Innermost brackets first, so nested ones work too.
    while re.search(r"\([^()]*\)", text):
        text = re.sub(r"\s*\(([^()]*)\)\s*", rf"{comma} \1{comma} ", text)

    if language == "tr":
        text = re.sub(r"(\w+)\s*ﷺ['’](\w+)", _turkish_suffix_to_noun, text)

    # "the Prophet ﷺ?"      becomes "the Prophet, peace be upon him?"
    # "the Prophet ﷺ from"  becomes "the Prophet, peace be upon him, from"
    text = re.sub(r"\s*ﷺ\s*", f"{comma} {HONORIFIC[language]}{comma} ", text)

    # Drop a comma that ends up right before other punctuation, or doubled.
    text = re.sub(rf"[,،]\s*([{PUNCTUATION}])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    # And one left at the very end ("the Prophet ﷺ" as the last word).
    return text.strip().rstrip(",،").strip()
