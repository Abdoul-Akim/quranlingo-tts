# Turn clips into an anonymous listening round for the website.
#
# Kinds of round:
#   base        Testers pick each character's base voice from the owner's shortlist, or else the top 3 takes.
#   engines     Testers compare the same line spoken by different engines.
#   experiment  Testers compare a line in the native voice with the English voice speaking it.
#
# Each clip is copied under a random name, so testers cannot guess the seed or engine.
# The answer key (random name to original file) is written to keys/, which is never uploaded.
#
# Run from the TTS folder:
#   python3 tools/make_round.py base base_fr fr
#   python3 tools/make_round.py engines engines_fr fr chatterbox voxcpm2
#   python3 tools/make_round.py experiment experiment_fr fr voxcpm2 en
import csv
import json
import secrets
import shutil
import sys
from pathlib import Path

from project_config import CHARACTER_LABELS, CHARACTERS, OWNER_SHORTLIST, SAME_VOICE_EVERYWHERE
from rank_takes import rank
from text_rules import prepare_text

TTS_DIR = Path(__file__).resolve().parents[1]

TOP_TAKES = 3

QUESTIONS = {
    "base": "Which voice fits this character best?",
    "engines": "Which sounds more natural and fits the emotion better?",
    "experiment": "Which voice sounds more natural in your language?",
}

# What testers are told each line should sound like.
EMOTION_HINTS = {
    "question": "a warm, clear question",
    "option": "a warm, clear answer option",
}


def base_items(language: str) -> list[dict]:
    takes_dir = TTS_DIR / "outputs" / "base_voices" / language
    with (takes_dir / "checks.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    items = []
    for character in CHARACTERS:
        if SAME_VOICE_EVERYWHERE.get(character, language) != language:
            continue  # this character uses the English voice here, so there is nothing to choose
        shortlist = OWNER_SHORTLIST.get(language, {}).get(character)
        best = shortlist or [r["clip"] for r in rank(rows, character)[:TOP_TAKES]]
        if best:
            items.append({
                "item": character,
                "label": CHARACTER_LABELS[character],
                "variants": [(clip, takes_dir / clip) for clip in best],
            })
    return items


def _line_item(line: dict, language: str, number: int, total: int, wavs: list) -> dict:
    missing = [str(w) for _, w in wavs if not w.exists()]
    if missing:
        sys.exit(f"Missing clips: {', '.join(missing)}")
    emotion = line["emotion"]
    hint = EMOTION_HINTS.get(emotion, f"{emotion} ({line['intensity']})")
    return {
        "item": line["id"],
        "label": f"Line {number} of {total}",
        # Show the text exactly as the engines spoke it, so testers can spot skipped words.
        "text": prepare_text(line["text"], language),
        "hint": f"Should sound: {hint}",
        "variants": wavs,
    }


def _read_lines(language: str) -> list[dict]:
    with (TTS_DIR / "test_lines" / f"{language}.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def engines_items(language: str, engines: list[str]) -> list[dict]:
    step_dir = TTS_DIR / "outputs" / f"step1_{language}"
    lines = _read_lines(language)
    return [
        _line_item(line, language, n, len(lines), [(e, step_dir / e / f"{line['id']}.wav") for e in engines])
        for n, line in enumerate(lines, start=1)
    ]


def experiment_items(language: str, engine: str, voices_from: str) -> list[dict]:
    step_dir = TTS_DIR / "outputs" / f"step1_{language}"
    # Characters who already speak with the English voice would be compared with themselves.
    lines = [line for line in _read_lines(language) if line["character"] not in SAME_VOICE_EVERYWHERE]
    return [
        _line_item(line, language, n, len(lines), [
            ("native", step_dir / engine / f"{line['id']}.wav"),
            (f"voice_{voices_from}", step_dir / f"{engine}_voice_{voices_from}" / f"{line['id']}.wav"),
        ])
        for n, line in enumerate(lines, start=1)
    ]


def write_round(round_name: str, kind: str, question: str, items: list[dict]) -> Path:
    if not items:
        sys.exit("No clips found.")
    round_dir = TTS_DIR / "listening_site" / "rounds" / round_name
    keys_dir = TTS_DIR / "keys"
    key_path = keys_dir / f"{round_name}.json"
    # Never overwrite a round: testers may already have voted on it.
    if round_dir.exists() or key_path.exists():
        sys.exit(f"Round '{round_name}' already exists. Pick a new name.")
    round_dir.mkdir(parents=True)
    keys_dir.mkdir(exist_ok=True)

    round_info = {"round": round_name, "kind": kind, "question": question, "items": []}
    key = {"round": round_name, "clips": {}}
    for item in items:
        item = dict(item)
        clip_ids = []
        for variant, wav in item.pop("variants"):
            clip_id = secrets.token_hex(4)  # 8 random characters, e.g. "k7f2a91c"
            shutil.copy2(wav, round_dir / f"{clip_id}.wav")
            clip_ids.append(clip_id)
            key["clips"][clip_id] = {"item": item["item"], "variant": variant, "source": str(Path(wav).relative_to(TTS_DIR))}
        # Shuffle so the order in round.json does not reveal anything either.
        secrets.SystemRandom().shuffle(clip_ids)
        item["clips"] = clip_ids
        round_info["items"].append(item)
        print(f"{item['item']}: {len(clip_ids)} clips")

    (round_dir / "round.json").write_text(json.dumps(round_info, indent=2, ensure_ascii=False), encoding="utf-8")
    key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"Round written to {round_dir}")
    print(f"Answer key written to {key_path} (keep it local, never upload it)")
    return round_dir


if __name__ == "__main__":
    kind, round_name, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    if kind == "base":
        items = base_items(rest[0])
    elif kind == "engines":
        items = engines_items(rest[0], rest[1:])
    elif kind == "experiment":
        items = experiment_items(rest[0], rest[1], rest[2])
    else:
        sys.exit(f"First argument must be one of: {', '.join(QUESTIONS)}.")
    write_round(round_name, kind, QUESTIONS[kind], items)
