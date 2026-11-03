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

### Final status, 06:55

Both runs ended with `ALL DONE` at 06:48. The only failure is `parler_base` (Urdu and Hindi with Indic Parler-TTS): access is still waiting for you to accept the model's terms (section 3).

**One bug found and fixed (TDD, commits c9971d0 red and eb081a0 green):** the English test lines in `outputs/step1_en` were from 2026-10-24, made with the OLD young and middle aged voices. The resumable script saw the files and skipped them. Clips older than their voice are now redone. The old clips are kept in `outputs/archive/step1_en_old_voices_2026-10-24`. The English lines were regenerated with the new voices (06:49 to 07:00) and rechecked: voice similarity is now 0.926 on Chatterbox and 0.886 on VoxCPM2 (was 0.73 with the old clips). The English lines round `lines_en` was rebuilt from them; the stale round and its key are in `outputs/archive/round_lines_en_old_voices`. Log: `outputs/logs/redo_en.log`.

**What the measurements say (outputs/report.md)**
- Chatterbox reads the words more accurately than VoxCPM2 in every language. Arabic is weak for both (Chatterbox 6 of 16 clips flagged, VoxCPM2 9 of 16).
- VoxCPM2 in Hindi sometimes keeps talking after the sentence, in made-up words (for example `q03`, `q04_opt4`). Listen to `outputs/step1_hi/voxcpm2` before trusting it.
- Urdu on VoxCPM2 (not officially supported): 11 of 16 clips flagged. Indic Parler-TTS is still needed.
- The English voice cloned into other languages reads worse than the native voices with VoxCPM2 (for example French cer 0.141 against 0.044), and about the same with Chatterbox.
- Voice similarity is 0.87 to 0.92 everywhere outside English, so each character stays recognisable.
- New this run: every character in every emotion in English, `open outputs/variations_en`.

### Status at the 06:04 check (last check of the night)

No stage has failed.

**Finished**
- Base voices for all 7 languages, with provisional picks in `voices/<lang>/` (Urdu is the experimental VoxCPM2 version).
- English test lines on both engines, with word checks (Chatterbox mean cer 0.017, 1 bad clip; VoxCPM2 0.022, 2 bad clips).
- Native test lines for fr, de, tr, ar, hi on both engines, and ur on VoxCPM2 (16 clips each).
- The experiment with the English voice cloned into the other languages: VoxCPM2 complete. Chatterbox is complete for fr, de, tr and ar.

**Still running at 06:04**
- The Chatterbox experiment for Hindi (5 of 16 clips).
- Then: word checks on the non-English lines, then `run_after.sh`: voice similarity, the English variations, the listening rounds and the final report. Memory is very tight (swap almost full), so this is slow. If the logs do not end with `ALL DONE`, run the command in section 1 again.

**Listen to first**
1. The English picks: `open voices/en`. These are the voices everything else is built from. Note that the old young/middle aged files are still in that folder; only `ali`, `fatima`, `omar` and `zahra` are new.
2. English lines, one engine against the other: `open outputs/step1_en/voxcpm2 outputs/step1_en/chatterbox`
3. One other language, native voices against the cloned English voice, for example French: `open outputs/step1_fr`

**Worth knowing**
- The word check never reaches 0 for Turkish and Arabic, because the text has marks that Whisper does not write (Turkish "â", Arabic tanween such as "مرحبًا"). The floor is the same for every take (tr 0.008, ar 0.056), so the ranking is still fair. A fix (ignore those marks when comparing) is a small TDD change for later. I did not change it mid-run, so all the scores stay comparable.

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
