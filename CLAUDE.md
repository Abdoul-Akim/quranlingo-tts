# QuranLingo TTS pipeline

Text-to-speech for QuranLingo, an app for learning about the Quran. It voices questions, instructions, stories and educational explanations in a natural, expressive voice. Audio is generated offline in batches and uploaded, so speed does not matter. Emotion and naturalness matter most.

- Languages in use (7): Urdu, English, French, Arabic, German, Turkish, Hindi. Spanish is not used in the app and is dropped for now.
- Characters (from the app's character sheet, 2026-11-02; replaces the earlier young/middle aged voices, which were wrong). Code names and descriptions live in `tools/project_config.py`.
  - `ali`: Ali, 14 year old boy. Serious and studious, warm-hearted and friendly; calm confidence, quiet dedication.
  - `fatima`: Fatima, 29 year old woman. Warm, nurturing, intelligent; a motherly guide who comforts mistakes and celebrates success.
  - `omar`: Omar, 50 year old man. Calm, wise, grounded; soft-spoken, the father figure and beloved elder guide.
  - `zahra`: Zahra, 10 year old girl. Bubbly, curious, full of energy; talkative and animated.
  - A character must sound like the same person every time within a language.
  - Main approach: a separate native base voice per character per language. Side experiment: clone the English base voice into the other languages; testers decide whether they prefer one voice everywhere or native voices (watch for accent).
- Characters present questions, celebrate work done and motivate users to practise.
- Prefer free open-source models that run locally. Use a paid cloud model only where the free ones are not good enough.
- The founder wants the voices usable by others after asking permission, never for harmful purposes. Drafts in `docs/licensing.md` and `docs/VOICES_LICENSE_DRAFT.md`; nothing is published yet.

## Rules that never change

- Quranic verses are never synthesised. They come from licensed human recitation.
- Only use models whose licence allows commercial use. Check current docs and licence before using a model; do not rely on memory. Avoid GPL dependencies (the repository may become public), for example Parselmouth.
- One engine and one fixed voice per character per language. Never mix engines for the same character.
- No em dashes or en dashes in code comments, docs or messages.
- All voices are synthetic, created by us (for example with voice design). No real person's voice is cloned.
- Stories are told by a narrator. No character speaks as a prophet.
- Engine watermarks (Chatterbox Perth, Gemini) are accepted.
- Never commit or upload `keys/`, `outputs/`, `voices/` or the spreadsheet (see `.gitignore`).

## Source data

- `All Questions Translations - Revised.xlsx`, sheet `review_ar_en`: 237 multiple choice questions on Juz Amma, with question and 4 options in all 8 languages (columns `<lang>_question`, `<lang>_opt1..4`). Other sheets are review logs, not content.
- `test_lines/emotional_lines.json`: the 8 emotional test lines in all 7 languages (non-English are drafts for native review). `tools/make_test_lines.py` builds `test_lines/<lang>.csv` from it plus 4 spreadsheet questions.

## How we work

- Test-driven development (owner's request, 2026-11-02): write the test, run it and see it fail, commit (`test: ... (red)`), write the code, see it pass, commit (`feat: ... (green)`). Run tests from the TTS folder: `uv run --project analysis python -m pytest`; site tests from `listening_site/`: `uv run python -m pytest`.
- Keep model scripts (`engines/*/`) thin; put logic in `tools/` so it can be tested without a model.
- Small steps. Explain the plan, wait for approval, then write code. After writing code, explain what it does and how to run it.
- Ask when something is unclear instead of guessing; when working unattended and unsure, do both options.
- The owner is new to TTS and stays in control: show every step and command, explain the concepts, and only run things the owner has approved. Pushing to GitHub, deploying the site and publishing anything need the owner's explicit go.
- Long jobs: one heavy model at a time (other projects on this Mac compete for memory), resumable scripts, never edit a shell script while it runs.

## Code map

| Path | What |
|---|---|
| `tools/project_config.py` | Languages, characters, descriptions, passages, target pitch, engine language support |
| `tools/text_rules.py` | Text before speech: honorific per language, Turkish endings, brackets spoken as asides |
| `tools/base_voices.py`, `engines/voxcpm2/design_base_voices.py` | Which base voice takes to design, and the VoxCPM2 run |
| `tools/parler_voices.py`, `engines/parler/design_base_voices.py` | Indic Parler-TTS for Urdu and Hindi (needs the model's terms accepted on Hugging Face) |
| `tools/age_shift.py` | Pitch and formant shift (WORLD vocoder) to make a voice sound younger; tried, not used in the current voices |
| `tools/check_clips.py`, `tools/rank_takes.py` | Whisper word check and pitch; ranking and provisional picks into `voices/<lang>/` |
| `tools/line_styles.py`, `tools/line_jobs.py`, `engines/*/generate.py` | Emotion styles per engine, paths, and the test line runs |
| `engines/chatterbox/speaker_similarity.py`, `tools/similarity.py` | Voice consistency check |
| `tools/variations.py` | Every character in every emotion (Phase C) |
| `tools/make_round.py`, `tools/results.py` | Listening rounds and vote counting |
| `tools/run_overnight.sh`, `tools/run_after.sh` | The full unattended run |
| `tools/summarise.py` | `outputs/report.md` |
| `tools/run_languages.sh` | Redo the other languages with the owner's chosen English wordings |
| `aws_site/`, `tools/aws_tools.py`, `tools/deploy_aws.sh`, `tools/serve_aws_site.py` | The listening site on AWS (see `aws_site/README.md`) |

## Listening and rating

- Moving to AWS (owner decision, 2026-11-08): QuranLingo's AWS account, S3 plus CloudFront for pages and audio, Lambda plus DynamoDB for votes, template in `aws_site/template.yaml`. Built and tested locally; waiting for QuranLingo to create the IAM user (`aws_site/deploy_policy.json`). The Render site below stays online until the AWS site is live. The address is QuranLingo's decision.

- Site: a Gradio app hosted on Render (owner's paid account), deployed from a private GitHub repo that contains only `listening_site/` (its own Git repository). One page per language from `listening_site/rounds/pages.json`; the first English test stays at `/en-v1`. Gradio Spaces on Hugging Face need PRO since 2026, so they are not used. Votes go to the private Hugging Face dataset `abdoulakim/quranlingo-tts-votes`. Clip file names are anonymised and the answer keys stay local (`keys/`), never uploaded.
- Testers compare clips blind (order shuffled per visitor, engine and seed hidden), answer A, B, C or same, with an optional comment.
- Raters are the internal team and some app users, who will not have claude.ai accounts, so the site must be hosted by us.

## Text decisions

- The symbol ﷺ is spoken as "peace be upon him" in English; the other languages' forms in `tools/text_rules.py` are drafts for the team to confirm.
- Each question and each answer option is its own clip.
- Questions that quote Quranic Arabic phrases are skipped for now. They must be handled later; how is still open.
- A gloss in brackets ("Jahannam (Hellfire)") is spoken as an aside; VoxCPM2 otherwise drops it (confirmed by Whisper).

## Engines

| Language | Candidates |
|---|---|
| en, fr, de, tr, ar | Chatterbox Multilingual V3 (MIT), VoxCPM2 (Apache-2.0) |
| hi | Same, plus Indic Parler-TTS (Apache-2.0) |
| ur | Indic Parler-TTS; VoxCPM2 as an untested experiment |

VoxCPM2 settings chosen by ear: 50 inference timesteps, cfg 1.5 (10 steps sounded metallic and buzzy). Set in `engines/voxcpm2/voices_config.py`. Gemini-TTS is paused (owner decision, 2026-10-25).

Facts checked 2026-10-24 and 2026-11-02 (recheck before relying on them):
- Chatterbox Multilingual V3: MIT, 23 languages (no Urdu). Every output carries an inaudible Perth watermark. V3 is only on GitHub, not PyPI (pinned commit `5de7a54`).
- VoxCPM2: Apache-2.0 code and weights, 30 languages (no Urdu), 48 kHz output. Runs on MPS on this Mac.
- Indic Parler-TTS: Apache-2.0, officially supports Urdu and Hindi, gated (accept terms), no voice cloning.
- Child voices are a known weak spot of TTS models (little child speech in training data).

## Plan

1. Test English on the engines. Done for the earlier characters; redone overnight for Ali, Fatima, Omar and Zahra.
2. Test the other languages; native speakers rate the clips.
3. Lock the engine per language and each character's voice (reference clip in `voices/<lang>/`).
4. Emotion directions: an LLM splits stories into segments and tags each with a speaker and an emotion from a fixed set (neutral, warm, happy, excited, sad, calm, curious, serious) with an intensity (low, medium, high). A person reviews the tags. Each engine maps tags to its controls (`tools/line_styles.py`). Questions and instructions use a fixed warm, clear style.
5. Batch generation: several takes per line, automatic checks (`tools/check_clips.py`, `engines/chatterbox/speaker_similarity.py`), a person picks the best take, volume matching, upload.
