# Turn clips into an anonymous listening round for the website.
#
# Two kinds of round:
#   voices   Testers pick a take for each character. Clips are named <character>_seed<N>.wav.
#   engines  Testers compare the same line spoken by different engines.
#
# Each clip is copied under a random name, so testers cannot guess the seed or engine.
# The answer key (random name to original file) is written to keys/, which is never uploaded.
#
# Run from the TTS folder:
#   python3 tools/make_round.py voices voices_en_v2 outputs/voice_design/en_v2_steps50_cfg1.5 young_female:2,3 middle_aged_female:2,3
#   python3 tools/make_round.py engines engines_en en chatterbox voxcpm2
import csv
import json
import secrets
import shutil
import sys
from pathlib import Path

from text_rules import prepare_text

TTS_DIR = Path(__file__).resolve().parents[1]
ROUNDS_DIR = TTS_DIR / "listening_site" / "rounds"
KEYS_DIR = TTS_DIR / "keys"

# Characters always appear in this order on the site.
CHARACTER_ORDER = ["young_male", "young_female", "middle_aged_male", "middle_aged_female"]

# What testers are told each line should sound like.
EMOTION_HINTS = {
    "question": "a warm, clear question",
    "option": "a warm, clear answer option",
}


def voices_items(source_dir: Path, filters: list[str]) -> list[dict]:
    # filters like "young_female:2,3" keep only those seeds; no filters keeps every clip.
    wanted = {}
    for f in filters:
        character, seeds = f.split(":")
        wanted[character] = {int(s) for s in seeds.split(",")}

    groups = {}
    for wav in sorted(source_dir.glob("*_seed*.wav")):
        character, seed = wav.stem.rsplit("_seed", 1)
        if wanted and int(seed) not in wanted.get(character, set()):
            continue
        groups.setdefault(character, []).append((f"seed{seed}", wav))

    return [
        {
            "item": character,
            # "middle_aged_female" becomes "Middle aged female".
            "label": character.replace("_", " ").capitalize(),
            "variants": variants,
        }
        for character, variants in sorted(groups.items(), key=lambda g: CHARACTER_ORDER.index(g[0]))
    ]


def engines_items(language: str, engines: list[str]) -> list[dict]:
    lines_path = TTS_DIR / "test_lines" / f"{language}.csv"
    step_dir = TTS_DIR / "outputs" / f"step1_{language}"
    with lines_path.open(encoding="utf-8") as f:
        lines = list(csv.DictReader(f))

    items = []
    for number, line in enumerate(lines, start=1):
        wavs = [(engine, step_dir / engine / f"{line['id']}.wav") for engine in engines]
        missing = [str(w) for _, w in wavs if not w.exists()]
        if missing:
            sys.exit(f"Missing clips: {', '.join(missing)}")
        emotion = line["emotion"]
        hint = EMOTION_HINTS.get(emotion, f"{emotion} ({line['intensity']})")
        items.append({
            "item": line["id"],
            "label": f"Line {number} of {len(lines)}",
            # Show the text exactly as the engines spoke it, so testers can spot skipped words.
            "text": prepare_text(line["text"], language),
            "hint": f"Should sound: {hint}",
            "variants": wavs,
        })
    return items


kind, round_name = sys.argv[1], sys.argv[2]
if kind == "voices":
    items = voices_items(Path(sys.argv[3]).resolve(), sys.argv[4:])
    question = "Which voice do you prefer?"
elif kind == "engines":
    items = engines_items(sys.argv[3], sys.argv[4:])
    question = "Which sounds more natural and fits the emotion better?"
else:
    sys.exit("First argument must be 'voices' or 'engines'.")
if not items:
    sys.exit("No clips found.")

round_dir = ROUNDS_DIR / round_name
key_path = KEYS_DIR / f"{round_name}.json"
# Never overwrite a round: testers may already have voted on it.
if round_dir.exists() or key_path.exists():
    sys.exit(f"Round '{round_name}' already exists. Pick a new name.")
round_dir.mkdir(parents=True)
KEYS_DIR.mkdir(exist_ok=True)

round_info = {"round": round_name, "kind": kind, "question": question, "items": []}
key = {"round": round_name, "clips": {}}

for item in items:
    clip_ids = []
    for variant, wav in item.pop("variants"):
        clip_id = secrets.token_hex(4)  # 8 random characters, e.g. "k7f2a91c"
        shutil.copy2(wav, round_dir / f"{clip_id}.wav")
        clip_ids.append(clip_id)
        key["clips"][clip_id] = {"item": item["item"], "variant": variant, "source": str(wav.relative_to(TTS_DIR))}
    # Shuffle so the order in round.json does not reveal anything either.
    secrets.SystemRandom().shuffle(clip_ids)
    item["clips"] = clip_ids
    round_info["items"].append(item)
    print(f"{item['item']}: {len(clip_ids)} clips")

(round_dir / "round.json").write_text(json.dumps(round_info, indent=2, ensure_ascii=False), encoding="utf-8")
key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")
print(f"Round written to {round_dir}")
print(f"Answer key written to {key_path} (keep it local, never upload it)")
