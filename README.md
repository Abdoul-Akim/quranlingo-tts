# QuranLingo TTS

Offline text-to-speech pipeline for [QuranLingo](#), an app for learning about the Quran. It gives the app's four characters natural, expressive voices in 7 languages: English, French, German, Turkish, Arabic, Hindi and Urdu.

| Character | Who |
|---|---|
| Ali | 14 year old boy, serious and studious, warm and friendly |
| Fatima | 29 year old woman, warm, nurturing and intelligent |
| Omar | 50 year old man, calm, wise and grounded |
| Zahra | 10 year old girl, bubbly, curious and full of energy |

All voices are synthetic, designed from text descriptions. No real person's voice is cloned. Quranic verses are never synthesised; they come from licensed human recitation.

## How it works

1. **Base voices:** each character's voice is designed from a description (VoxCPM2 voice design, or Indic Parler-TTS for Urdu). Ali keeps his English voice in every language, cloned into each one. A pitch and formant shift for younger voices (`tools/age_shift.py`) was tried and is not used in the current voices.
2. **Automatic checks:** speech recognition checks every take for wrong or missing words, and pitch is measured (`tools/check_clips.py`). Takes with a pitch clearly wrong for the character are dropped, and the rest are ranked (`tools/rank_takes.py`).
3. **People choose:** a blind listening website lets native speakers pick the best takes and engines (`tools/make_round.py`, the site is a separate repository).
4. **Generation:** each engine clones the chosen base voice and speaks the app's lines with the right emotion (`engines/*/generate.py`, `tools/line_styles.py`). Voice consistency is checked against the base voice (`engines/chatterbox/speaker_similarity.py`).

## Engines

| Engine | Licence | Languages used |
|---|---|---|
| [VoxCPM2](https://github.com/OpenBMB/VoxCPM) | Apache-2.0 | en, fr, de, tr, ar, hi (ur experimental) |
| [Chatterbox Multilingual V3](https://github.com/resemble-ai/chatterbox) | MIT, outputs watermarked | en, fr, de, tr, ar, hi |
| [Indic Parler-TTS](https://huggingface.co/ai4bharat/indic-parler-tts) | Apache-2.0 | ur, hi |

Each engine has its own Python environment under `engines/`, because they need different PyTorch versions.

## Running

Requires [uv](https://docs.astral.sh/uv/) and an Apple Silicon Mac (or a CUDA GPU).

```bash
# Tests (run from this folder)
uv run --project analysis python -m pytest

# Everything, one heavy job at a time, resumable
caffeinate -i zsh tools/run_overnight.sh
caffeinate -i zsh tools/run_after.sh
```

## What is not in this repository

- `keys/`: the listening test answer keys (they reveal which clip is which).
- `outputs/`, `voices/`: generated audio and the reference voices.
- The question spreadsheet (QuranLingo content).

## Contributing

Development is test first: write a failing test, commit it, make it pass, commit. See `CONTRIBUTING.md`.

## Licence

Not decided yet (see `docs/licensing.md`).
