# Text rules applied before any engine speaks a line, so every engine gets the same text.
import re

# How the honorific symbol is spoken, per language. Other languages are added when we test them.
HONORIFIC = {
    "en": "peace be upon him",
}


def prepare_text(text: str, language: str) -> str:
    # "the Prophet ﷺ?"      becomes "the Prophet, peace be upon him?"
    # "the Prophet ﷺ from"  becomes "the Prophet, peace be upon him, from"
    text = re.sub(r"\s*ﷺ\s*", f", {HONORIFIC[language]}, ", text)
    # Drop a comma that ends up right before other punctuation.
    text = re.sub(r",\s*([?.!,;:])", r"\1", text)
    # And one left at the very end ("the Prophet ﷺ" as the last word).
    return text.strip().rstrip(",")
