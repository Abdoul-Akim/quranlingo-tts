# Collect every measurement into one readable report: outputs/report.md
#   Base voices: the provisional pick per character and language (tools/rank_takes.py)
#   Test lines:  word accuracy (checks.csv) and voice consistency (similarity.csv) per engine
#
# Run from the TTS folder:  python3 tools/summarise.py
import csv
import json
from pathlib import Path

from project_config import CHARACTERS, LANGUAGES
from rank_takes import MAX_CER

TTS_DIR = Path(__file__).resolve().parents[1]


def engine_scores(checks: list[dict], similarity: list[dict]) -> dict:
    cers = [float(r["cer"]) for r in checks if r.get("cer") not in ("", None)]
    sims = [float(r["similarity"]) for r in similarity]
    return {
        "clips": len(cers),
        "mean_cer": round(sum(cers) / len(cers), 3) if cers else None,
        "bad_clips": sum(c > MAX_CER for c in cers),
        "mean_similarity": round(sum(sims) / len(sims), 3) if sims else None,
    }


def markdown_table(header: list, rows: list) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join("" if v is None else str(v) for v in row) + " |" for row in rows]
    return "\n".join(lines)


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    parts = ["# Overnight report", "",
             "Automatic measurements only. Provisional picks are for continuing work; people make the real choice.", ""]

    parts += ["## Provisional base voices", ""]
    pick_rows = []
    for language in LANGUAGES:
        picks_file = TTS_DIR / "voices" / language / "provisional_picks.json"
        picks = json.loads(picks_file.read_text()) if picks_file.exists() else {}
        for character in CHARACTERS:
            p = picks.get(character)
            pick_rows.append([language, character, p["take"] if p else "not done", p and p["pitch_hz"], p and p["cer"]])
    parts += [markdown_table(["Language", "Character", "Take", "Pitch (Hz)", "Word errors (cer)"], pick_rows), ""]

    parts += ["## Test lines per engine", "",
              f"cer: character error rate from speech recognition (0 is perfect; above {MAX_CER} counts as bad). "
              "Similarity: voice fingerprint match with the reference (1.0 is the same voice; about 0.65 is a different person).", ""]
    line_rows = []
    for language in LANGUAGES:
        for folder in sorted((TTS_DIR / "outputs" / f"step1_{language}").glob("*/")):
            s = engine_scores(_read(folder / "checks.csv"), _read(folder / "similarity.csv"))
            line_rows.append([language, folder.name, s["clips"], s["mean_cer"], s["bad_clips"], s["mean_similarity"]])
    parts += [markdown_table(["Language", "Engine", "Clips checked", "Mean cer", "Bad clips", "Mean similarity"], line_rows), ""]

    out = TTS_DIR / "outputs" / "report.md"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(TTS_DIR)}")
