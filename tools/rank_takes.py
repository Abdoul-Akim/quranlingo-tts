# Rank voice takes automatically, from the measurements in checks.csv (see check_clips.py).
#   1. Takes whose words came out wrong (character error rate above MAX_CER) are excluded.
#   2. Takes whose pitch is inside the character's target range come first.
#   3. Then the clearest words win; outside the range, the closest pitch wins.
# This only picks PROVISIONAL voices so work can continue; people make the real choice.
#
# Run from the TTS folder:
#   uv run --project analysis python tools/rank_takes.py outputs/base_voices/en voices/en
import csv
import json
import shutil
import sys
from pathlib import Path

from project_config import CHARACTERS, OWNER_SHORTLIST, TARGET_PITCH_HZ

MAX_CER = 0.10


def _pitch_distance(pitch: float, character: str) -> float:
    low, high = TARGET_PITCH_HZ[character]
    if low <= pitch <= high:
        return 0.0
    return (low - pitch if pitch < low else pitch - high) / ((low + high) / 2)


def rank(rows: list[dict], character: str) -> list[dict]:
    usable = [
        r for r in rows
        if r["clip"].split("/")[0] == character and r.get("cer") not in ("", None) and float(r["cer"]) <= MAX_CER
    ]
    return sorted(usable, key=lambda r: (_pitch_distance(float(r["pitch_hz"]), character), float(r["cer"])))


def read_checks(takes_dir: Path) -> list[dict]:
    with (takes_dir / "checks.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pick_provisional(takes_dir: Path, voices_dir: Path) -> dict:
    # Copies the best take per character to voices/<lang>/<character>.wav with its words (.txt).
    rows = read_checks(takes_dir)
    passage = (takes_dir / "passage.txt").read_text(encoding="utf-8")
    voices_dir.mkdir(parents=True, exist_ok=True)
    picks, record = {}, {}
    for character in CHARACTERS:
        ranked = rank(rows, character)
        shortlist = OWNER_SHORTLIST.get(takes_dir.name, {}).get(character)
        if shortlist:
            by_clip = {r["clip"]: r for r in rows}
            ranked = [by_clip[c] for c in shortlist]
        if not ranked:
            continue
        best = ranked[0]
        shutil.copy2(takes_dir / best["clip"], voices_dir / f"{character}.wav")
        (voices_dir / f"{character}.txt").write_text(passage, encoding="utf-8")
        picks[character] = best["clip"]
        record[character] = {"take": best["clip"], "pitch_hz": best["pitch_hz"], "cer": best["cer"],
                             "runners_up": [r["clip"] for r in (ranked[1:] if shortlist else ranked[1:3])],
                             "chosen_by": "owner shortlist" if shortlist else "automatic, provisional"}
    (voices_dir / "provisional_picks.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return picks


if __name__ == "__main__":
    for character, take in pick_provisional(Path(sys.argv[1]), Path(sys.argv[2])).items():
        print(f"{character}: {take}")
