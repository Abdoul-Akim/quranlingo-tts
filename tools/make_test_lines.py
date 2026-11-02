# Build test_lines/<lang>.csv for every app language:
#   e01 to e08  emotional lines, from test_lines/emotional_lines.json (translations)
#   q01 to q04  questions from the spreadsheet in that language; q04 also has its 4 options
# The honorific ﷺ stays in the file; prepare_text turns it into speech at generation time.
#
# Run from the TTS folder:
#   uv run --project analysis python tools/make_test_lines.py
import csv
import json
from pathlib import Path

import openpyxl

from project_config import LANGUAGES

TTS_DIR = Path(__file__).resolve().parents[1]
SHEET = TTS_DIR / "All Questions Translations - Revised.xlsx"
EMOTIONAL_LINES = TTS_DIR / "test_lines" / "emotional_lines.json"
FIELDS = ["id", "character", "emotion", "intensity", "source_ref", "text"]

# Spreadsheet question (by ref) and the character who asks it. The last one also reads its options.
QUESTION_PLAN = [("كو٢", "zahra"), ("نب٣", "omar"), ("كا٦", "fatima"), ("زل٤", "ali")]


def read_questions(sheet_path) -> dict:
    ws = openpyxl.load_workbook(sheet_path, read_only=True, data_only=True)["review_ar_en"]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    return {row[0]: dict(zip(header, row)) for row in rows if row and row[0]}


def build_rows(language: str, sheet_path=SHEET) -> list[dict]:
    lines = json.loads(EMOTIONAL_LINES.read_text(encoding="utf-8"))["lines"]
    rows = [
        {"id": l["id"], "character": l["character"], "emotion": l["emotion"],
         "intensity": l["intensity"], "source_ref": "", "text": l[language]}
        for l in lines
    ]
    questions = read_questions(sheet_path)
    for number, (ref, character) in enumerate(QUESTION_PLAN, start=1):
        q = questions[ref]
        rows.append({"id": f"q0{number}", "character": character, "emotion": "question",
                     "intensity": "fixed", "source_ref": ref, "text": q[f"{language}_question"]})
        if number == len(QUESTION_PLAN):
            for i in range(1, 5):
                rows.append({"id": f"q0{number}_opt{i}", "character": character, "emotion": "option",
                             "intensity": "fixed", "source_ref": ref, "text": q[f"{language}_opt{i}"]})
    return rows


def write_lines(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    for language in LANGUAGES:
        out = TTS_DIR / "test_lines" / f"{language}.csv"
        write_lines(build_rows(language), out)
        print(f"Wrote {out.relative_to(TTS_DIR)}")
