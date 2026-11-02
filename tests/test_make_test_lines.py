import csv

import openpyxl
import pytest

from make_test_lines import QUESTION_PLAN, build_rows, write_lines
from project_config import CHARACTERS, LANGUAGES

HEADER = ["ref", "surah_name_ar", "unit", "Ayah_range", "difficulty"]


def fake_spreadsheet(path, languages):
    # A tiny copy of the real sheet layout: <lang>_question and <lang>_opt1..4 per language.
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "review_ar_en"
    columns = list(HEADER)
    for lang in languages:
        columns += [f"{lang}_question"] + [f"{lang}_opt{i}" for i in range(1, 5)]
    ws.append(columns)
    for ref, _ in QUESTION_PLAN:
        row = [ref, "", 1, "", ""]
        for lang in languages:
            row += [f"{lang} question {ref} ﷺ?"] + [f"{lang} option {i}" for i in range(1, 5)]
        ws.append(row)
    wb.save(path)


@pytest.fixture
def sheet(tmp_path):
    path = tmp_path / "questions.xlsx"
    fake_spreadsheet(path, LANGUAGES)
    return path


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_language_gets_8_emotional_lines_and_the_questions(sheet, language):
    rows = build_rows(language, sheet)
    ids = [r["id"] for r in rows]
    assert ids[:8] == [f"e0{i}" for i in range(1, 9)]
    assert "q01" in ids and "q04_opt4" in ids
    assert all(r["text"].strip() for r in rows)


def test_questions_come_from_the_language_columns(sheet):
    rows = {r["id"]: r for r in build_rows("fr", sheet)}
    assert rows["q01"]["text"].startswith("fr question")
    assert rows["q04_opt2"]["text"] == "fr option 2"


def test_only_known_characters_are_used(sheet):
    for language in LANGUAGES:
        assert {r["character"] for r in build_rows(language, sheet)} <= set(CHARACTERS)


def test_every_character_speaks_at_least_two_lines(sheet):
    rows = build_rows("en", sheet)
    for character in CHARACTERS:
        assert sum(r["character"] == character for r in rows) >= 2


def test_honorific_is_kept_raw_in_the_file(sheet):
    # The file keeps ﷺ; prepare_text turns it into speech at generation time.
    rows = {r["id"]: r for r in build_rows("en", sheet)}
    assert "ﷺ" in rows["q01"]["text"]


def test_write_lines_makes_a_readable_csv(sheet, tmp_path):
    out = tmp_path / "ar.csv"
    write_lines(build_rows("ar", sheet), out)
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0].keys() >= {"id", "character", "emotion", "intensity", "source_ref", "text"}
    assert len(rows) == 16
