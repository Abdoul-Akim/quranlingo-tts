# Good morning: what happened overnight and what to do

## 1. See how far the run got

```bash
cd "/Users/abdoul-akimsilue_1/document/work experience /Quranlingo/TTS"
cat outputs/logs/overnight.log outputs/logs/after.log
python3 tools/summarise.py && open outputs/report.md
```

Every stage resumes where it stopped. If the logs do not end with `ALL DONE`, start them again:

```bash
caffeinate -i zsh tools/run_overnight.sh && caffeinate -i zsh tools/run_after.sh
```

## 2. Listen to the base voices

```bash
open outputs/base_voices/en
```

Each character folder has takes named `<wording>_seed<N>.wav`, and for Ali and Zahra also
`<take>__shift_<strength>.wav` (pitch and formants shifted to sound younger).
`voices/en/provisional_picks.json` shows which take the measurements picked, and why.
That pick is only provisional: your ears decide.

## 3. Three things only you can do

1. **Push the work to GitHub** (needs your permission; it creates a new private repository):
   ```bash
   gh repo create quranlingo-tts --private --source=. --push
   ```
   The history shows every TDD step: a red test commit, then a green code commit.
2. **Accept the Indic Parler-TTS terms** for Urdu: open https://huggingface.co/ai4bharat/indic-parler-tts,
   log in as abdoulakim and accept. Access is automatic. Then:
   ```bash
   (cd engines/parler && uv run python design_base_voices.py ur hi)
   ```
3. **Deploy the new listening site** (one page per language; the first English test moves to `/en-v1`):
   ```bash
   cd listening_site && git add rounds && git commit -m "New rounds" && git push
   ```
   Check `git status` first: only `rounds/`, `app.py`, `site_logic.py` and `tests/` should change.

## 4. Things to check with the team

- Draft translations: `tools/project_config.py` (passages), `test_lines/emotional_lines.json`,
  `tools/variations.py`, `listening_site/rounds/pages.json`.
- Honorific forms per language in `tools/text_rules.py`.
- Licensing drafts in `docs/` (for the founder, and a lawyer for the voice licence).
