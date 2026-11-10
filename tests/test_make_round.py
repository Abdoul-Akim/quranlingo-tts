import csv
import json

import numpy as np
import pytest
import soundfile as sf

import make_round
from make_round import base_items, experiment_items, write_round


@pytest.fixture
def project(tmp_path, monkeypatch):
    # A miniature TTS folder: base voice takes with checks, and test line clips.
    monkeypatch.setattr(make_round, "TTS_DIR", tmp_path)
    base = tmp_path / "outputs" / "base_voices" / "en"
    rows = []
    for character, pitches in {"ali": [200, 190, 120, 210], "zahra": [280, 270]}.items():
        (base / character).mkdir(parents=True)
        for i, pitch in enumerate(pitches):
            clip = f"{character}/v1_seed{i + 1}.wav"
            sf.write(base / clip, np.zeros(1600), 16000)
            rows.append({"clip": clip, "pitch_hz": pitch, "cer": 0.01 * i})
    with (base / "checks.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["clip", "pitch_hz", "cer"])
        w.writeheader()
        w.writerows(rows)

    lines = tmp_path / "test_lines"
    lines.mkdir()
    with (lines / "fr.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "character", "emotion", "intensity", "source_ref", "text"])
        w.writeheader()
        w.writerow({"id": "e01", "character": "omar", "emotion": "sad", "intensity": "low", "source_ref": "", "text": "Bonjour (salut)."})
    for folder in ("voxcpm2", "voxcpm2_voice_en"):
        (tmp_path / "outputs" / "step1_fr" / folder).mkdir(parents=True)
        sf.write(tmp_path / "outputs" / "step1_fr" / folder / "e01.wav", np.zeros(1600), 16000)
    return tmp_path


def test_base_round_offers_the_top_three_takes_per_character(project):
    items = {i["item"]: i for i in base_items("en")}
    ali = [variant for variant, _ in items["ali"]["variants"]]
    # 120 Hz is far outside Ali's young range, so it is left out of his top three.
    assert len(ali) == 3 and "ali/v1_seed3.wav" not in ali
    assert len(items["zahra"]["variants"]) == 2  # fewer takes than three is fine
    assert items["ali"]["label"].startswith("Ali")


def test_base_round_lists_characters_in_the_fixed_order(project):
    assert [i["item"] for i in base_items("en")] == ["ali", "zahra"]


def test_experiment_round_pairs_native_and_english_voice(project):
    (item,) = experiment_items("fr", "voxcpm2", "en")
    assert [variant for variant, _ in item["variants"]] == ["native", "voice_en"]
    assert item["text"] == "Bonjour, salut."  # shown as spoken


def test_write_round_hides_the_takes_and_keeps_the_key(project):
    items = base_items("en")
    write_round("base_en", "base", "Which voice fits the character best?", items)

    info = json.loads((project / "listening_site" / "rounds" / "base_en" / "round.json").read_text(encoding="utf-8"))
    key = json.loads((project / "keys" / "base_en.json").read_text())["clips"]
    clips = [c for item in info["items"] for c in item["clips"]]
    assert len(clips) == 5 and all(len(c) == 8 for c in clips)  # random names only
    assert {key[c]["variant"] for c in clips} >= {"ali/v1_seed1.wav", "zahra/v1_seed1.wav"}
    assert "seed" not in json.dumps(info)


def test_write_round_never_overwrites(project):
    write_round("r", "base", "q", base_items("en"))
    with pytest.raises(SystemExit):
        write_round("r", "base", "q", base_items("en"))


def test_the_owners_shortlist_replaces_the_automatic_top_three(project, monkeypatch):
    # The owner listened and shortlisted Ali's takes; Zahra has no shortlist, so stays automatic.
    monkeypatch.setattr(make_round, "OWNER_SHORTLIST", {"en": {"ali": ["ali/v1_seed3.wav", "ali/v1_seed1.wav"]}})
    items = {i["item"]: i for i in base_items("en")}
    assert [v for v, _ in items["ali"]["variants"]] == ["ali/v1_seed3.wav", "ali/v1_seed1.wav"]
    assert len(items["zahra"]["variants"]) == 2


def test_a_character_with_one_voice_everywhere_has_no_base_question_in_other_languages(project, monkeypatch):
    monkeypatch.setattr(make_round, "SAME_VOICE_EVERYWHERE", {"ali": "en"})
    fr = project / "outputs" / "base_voices" / "fr"
    fr.mkdir(parents=True)
    (project / "outputs" / "base_voices" / "en" / "checks.csv").rename(fr / "checks.csv")
    assert [i["item"] for i in base_items("fr")] == ["zahra"]


def test_the_experiment_leaves_out_a_character_who_already_has_the_english_voice(project, monkeypatch):
    monkeypatch.setattr(make_round, "SAME_VOICE_EVERYWHERE", {"omar": "en"})
    assert experiment_items("fr", "voxcpm2", "en") == []  # e01 is Omar's only line


def test_without_owner_picks_every_verified_take_is_offered_up_to_five(project):
    # 2026-11-10: testers choose among all takes the system verified (pitch inside the target,
    # words right), at most 5, the most a question can show.
    base = project / "outputs" / "base_voices" / "en"
    rows = []
    for i, pitch in enumerate([250, 255, 260, 265, 270, 275, 330]):  # Zahra: six inside, one too high
        clip = f"zahra/v4_seed{i + 1}.wav"
        sf.write(base / clip, np.zeros(1600), 16000)
        rows.append({"clip": clip, "pitch_hz": pitch, "cer": 0.0})
    with (base / "checks.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["clip", "pitch_hz", "cer"])
        w.writeheader()
        w.writerows(rows)
    (item,) = base_items("en")
    assert len(item["variants"]) == 5 and "zahra/v4_seed7.wav" not in [v for v, _ in item["variants"]]
