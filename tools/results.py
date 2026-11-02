# Count the listening test votes, using the local answer keys to reveal which clip was which.
#
# Run from the TTS folder:
#   uv run --project listening_site python tools/results.py           votes from Hugging Face
#   uv run --project listening_site python tools/results.py --local   votes from this computer (local tests)
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

TTS_DIR = Path(__file__).resolve().parents[1]
KEYS_DIR = TTS_DIR / "keys"
VOTES_REPO = "abdoulakim/quranlingo-tts-votes"

if "--local" in sys.argv:
    votes_dir = TTS_DIR / "listening_site" / "votes"
else:
    from huggingface_hub import snapshot_download

    # Downloads the private votes dataset (needs to be logged in with `hf auth login`).
    votes_dir = Path(snapshot_download(repo_id=VOTES_REPO, repo_type="dataset")) / "data"

votes = [json.loads(line) for path in sorted(votes_dir.glob("*.jsonl")) for line in path.read_text(encoding="utf-8").splitlines()]
# Our own checks never count: the nickname "test", plus test runs made without it (by tester id).
EXCLUDED_TESTERS = {
    "83a322dc06914bc38b46c1edcc754a33",  # 2026-10-25, first online test on Render
}
votes = [v for v in votes if v["nickname"].lower() != "test" and v["tester_id"] not in EXCLUDED_TESTERS]
testers = {v["tester_id"] for v in votes}
print(f"{len(votes)} answers from {len(testers)} testers\n")

keys = {path.stem: json.loads(path.read_text(encoding="utf-8"))["clips"] for path in KEYS_DIR.glob("*.json")}

# counts[round][item] counts the winning variant ("seed2", "voxcpm2", ...) or "same".
counts = defaultdict(lambda: defaultdict(Counter))
comments = []
for v in votes:
    key = keys[v["round"]]
    winner = key[v["chosen_clip"]]["variant"] if v["chosen_clip"] else "same"
    counts[v["round"]][v["item"]][winner] += 1
    if v["comment"]:
        shown = ", ".join(f"{letter}={key[clip]['variant']}" for letter, clip in zip("ABC", v["clips"]))
        comments.append(f"{v['round']} {v['item']} ({shown}) {v['nickname'] or 'anonymous'}: {v['comment']}")

for round_name, items in counts.items():
    print(f"== {round_name}")
    total = Counter()
    by_group = defaultdict(Counter)
    for item, c in items.items():
        print(f"  {item:20} " + "  ".join(f"{name} {n}" for name, n in c.most_common()))
        total += c
        # Engine rounds: lines starting with "e" are emotional, "q" are questions and options.
        by_group[item[0]] += c
    print(f"  {'TOTAL':20} " + "  ".join(f"{name} {n}" for name, n in total.most_common()))
    if set(by_group) == {"e", "q"}:
        for group, label in (("e", "emotional lines"), ("q", "questions and options")):
            print(f"  {label:20} " + "  ".join(f"{name} {n}" for name, n in by_group[group].most_common()))
    print()

if comments:
    print("== comments")
    print("\n".join(comments))
