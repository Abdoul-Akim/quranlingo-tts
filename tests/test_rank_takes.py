import csv
import json

import soundfile as sf
import numpy as np

from rank_takes import MAX_CER, pick_provisional, rank


def row(clip, pitch, cer):
    return {"clip": clip, "pitch_hz": str(pitch), "cer": str(cer)}


def test_takes_with_wrong_words_are_excluded():
    rows = [row("ali/a.wav", 200, MAX_CER + 0.05), row("ali/b.wav", 200, 0.0)]
    assert [r["clip"] for r in rank(rows, "ali")] == ["ali/b.wav"]


def test_pitch_inside_the_target_range_beats_clearer_words_outside_it():
    # Ali's target is a young voice; a deep 120 Hz take loses even with perfect words.
    rows = [row("ali/deep.wav", 120, 0.0), row("ali/young.wav", 200, 0.05)]
    assert rank(rows, "ali")[0]["clip"] == "ali/young.wav"


def test_inside_the_range_the_clearest_words_win():
    rows = [row("zahra/a.wav", 280, 0.08), row("zahra/b.wav", 260, 0.01)]
    assert rank(rows, "zahra")[0]["clip"] == "zahra/b.wav"


def test_outside_the_range_closer_pitch_ranks_higher():
    rows = [row("omar/a.wav", 200, 0.0), row("omar/b.wav", 160, 0.0)]  # target 85 to 145
    assert [r["clip"] for r in rank(rows, "omar")] == ["omar/b.wav", "omar/a.wav"]


def test_only_this_characters_takes_are_ranked():
    rows = [row("ali/a.wav", 200, 0.0), row("zahra/a.wav", 280, 0.0)]
    assert [r["clip"] for r in rank(rows, "ali")] == ["ali/a.wav"]


def write_checks(folder, rows):
    with (folder / "checks.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["clip", "pitch_hz", "cer"])
        w.writeheader()
        w.writerows(rows)


def test_pick_provisional_copies_the_best_take_with_its_words(tmp_path):
    takes = tmp_path / "base" / "en"
    (takes / "fatima").mkdir(parents=True)
    for name in ("x.wav", "y.wav"):
        sf.write(takes / "fatima" / name, np.zeros(1600), 16000)
    write_checks(takes, [row("fatima/x.wav", 300, 0.0), row("fatima/y.wav", 210, 0.02)])
    (takes / "passage.txt").write_text("Hello, and welcome.\n", encoding="utf-8")
    voices = tmp_path / "voices" / "en"

    picks = pick_provisional(takes, voices)

    assert picks["fatima"] == "fatima/y.wav"
    assert (voices / "fatima.wav").exists()
    assert (voices / "fatima.txt").read_text(encoding="utf-8") == "Hello, and welcome.\n"
    assert json.loads((voices / "provisional_picks.json").read_text())["fatima"]["take"] == "fatima/y.wav"


def test_pick_provisional_skips_a_character_with_no_usable_take(tmp_path):
    takes = tmp_path / "base" / "en"
    (takes / "omar").mkdir(parents=True)
    sf.write(takes / "omar" / "x.wav", np.zeros(1600), 16000)
    write_checks(takes, [row("omar/x.wav", 120, 0.9)])
    (takes / "passage.txt").write_text("Hi.\n", encoding="utf-8")
    assert "omar" not in pick_provisional(takes, tmp_path / "voices" / "en")


def test_pick_provisional_takes_the_owners_first_choice(tmp_path, monkeypatch):
    import rank_takes
    takes = tmp_path / "base" / "en"
    (takes / "fatima").mkdir(parents=True)
    for name in ("x.wav", "y.wav"):
        sf.write(takes / "fatima" / name, np.zeros(1600), 16000)
    write_checks(takes, [row("fatima/x.wav", 300, 0.0), row("fatima/y.wav", 210, 0.02)])
    (takes / "passage.txt").write_text("Hello.\n", encoding="utf-8")
    monkeypatch.setattr(rank_takes, "OWNER_SHORTLIST", {"en": {"fatima": ["fatima/x.wav", "fatima/y.wav"]}})

    picks = pick_provisional(takes, tmp_path / "voices" / "en")

    assert picks["fatima"] == "fatima/x.wav"  # the owner's ears beat the pitch target
    record = json.loads((tmp_path / "voices" / "en" / "provisional_picks.json").read_text())["fatima"]
    assert record["chosen_by"] == "owner shortlist" and record["runners_up"] == ["fatima/y.wav"]
