# QuranLingo TTS pipeline

Text-to-speech for QuranLingo, an app for learning about the Quran. It voices questions, instructions, stories and educational explanations in a natural, expressive voice. Audio is generated offline in batches and uploaded, so speed does not matter. Emotion and naturalness matter most.

- Languages in use (7): Urdu, English, French, Arabic, German, Turkish, Hindi. Spanish is not used in the app and is dropped for now.
- Characters (from the app's character sheet, 2026-11-02; replaces the earlier young/middle aged voices, which were wrong):
  - `ali`: Ali, 14 year old boy. Serious and studious, warm-hearted and friendly; calm confidence, quiet dedication. The dependable scholar who motivates learners.
  - `fatima`: Fatima, 29 year old woman. Warm, nurturing, intelligent; calm, kind, reliable, a motherly guide who comforts mistakes and celebrates success.
  - `omar`: Omar, 50 year old man. Calm, wise, grounded; soft-spoken, the father figure and beloved elder guide.
  - A character must sound like the same person every time within a language.
  - Main approach: a separate native base voice per character per language. Side experiment: clone the English base voice into the other languages; testers decide whether they prefer one voice everywhere or native voices (watch for accent).
- Characters present questions, celebrate work done and motivate users to practise.
- Prefer free open-source models that run locally. Use a paid cloud model only where the free ones are not good enough.

## Rules that never change

- Quranic verses are never synthesised. They come from licensed human recitation.
- Only use models whose licence allows commercial use. Check current docs and licence before using a model; do not rely on memory.
- One engine and one fixed voice per character per language. Never mix engines for the same character.
- No em dashes or en dashes in code comments, docs or messages.
- All voices are synthetic, created by us (for example with voice design). No real person's voice is cloned.
- Stories are told by a narrator. No character speaks as a prophet.
- Engine watermarks (Chatterbox Perth, Gemini) are accepted.

## Source data

- `All Questions Translations - Revised.xlsx`, sheet `review_ar_en`: 237 multiple choice questions on Juz Amma, with question and 4 options in all 8 languages (columns `<lang>_question`, `<lang>_opt1..4`). Other sheets are review logs, not content.

## How we work

- Small steps. Explain the plan, wait for approval, then write code.
- After writing code, explain what it does and how to run it.
- Ask when something is unclear instead of guessing.
- The owner is new to TTS and stays in control: show every step and command, explain the concepts, and only run things the owner has approved.

## Listening and rating

- Site: a Gradio app hosted on Render (owner's paid account), deployed from a private GitHub repo that contains only `listening_site/`. Gradio Spaces on Hugging Face need PRO since 2026, so they are not used. Votes go to the private Hugging Face dataset `abdoulakim/quranlingo-tts-votes`. Clip file names are anonymised and the answer keys stay local (`keys/`), never uploaded.
- Testers compare pairs blind (A/B order shuffled per visitor, engine and seed hidden) and answer A, B or same, with an optional comment. Rounds are built with `tools/make_round.py`, the site is `listening_site/app.py`, votes are counted with `tools/results.py`.
- Raters are the internal team and some app users, who will not have claude.ai accounts, so the site must be hosted by us.

## Text decisions

- The symbol ﷺ is spoken as "peace be upon him" (replaced in the text before generation).
- Each question and each answer option is its own clip.
- Questions that quote Quranic Arabic phrases are skipped for now. They must be handled later; how is still open.

## Shortlist (nothing decided yet)

| Language | Candidates |
|---|---|
| en, de, fr, es, ar, tr | Chatterbox Multilingual V3 (MIT), VoxCPM2 (Apache-2.0), Gemini-TTS (paid comparison) |
| hi | Same, plus Indic Parler-TTS (Apache-2.0) |
| ur | Indic Parler-TTS (weak, untested); Gemini-TTS likely |

VoxCPM2 settings chosen by ear: 50 inference timesteps, cfg 1.5 (10 steps sounded metallic and buzzy). Set in `engines/voxcpm2/voices_config.py`.

Facts checked 2026-10-24 (recheck before relying on them):
- Chatterbox Multilingual V3: MIT, 23 languages (no Urdu). Every output carries an inaudible Perth watermark.
- VoxCPM2: Apache-2.0 code and weights, 30 languages (no Urdu), 48 kHz output. Docs target CUDA; Mac (MPS) support is unconfirmed.
- Gemini-TTS (gemini-3.8-flash-tts): paid API, 24 kHz output. Urdu is not in its supported language list.

## Plan

1. Test English: about 10 emotional test lines on Chatterbox, VoxCPM2 and Gemini-TTS. The owner listens.
2. Test the other 7 languages; native speakers rate the clips.
3. Lock the engine per language and each character's voice (for example a reference clip).
4. Emotion directions: an LLM splits stories into segments and tags each with a speaker and an emotion from a fixed set (neutral, warm, happy, excited, sad, calm, curious, serious) with an intensity (low, medium, high). A person reviews the tags. Each engine maps tags to its controls (text prompts for Gemini and VoxCPM2, exaggeration and pacing dials for Chatterbox). Questions and instructions use a fixed warm, clear style.
5. Batch generation: several takes per line, automatic checks (speech recognition for misread words, speaker similarity for voice consistency), a person picks the best take, volume matching, upload.

Current step: 1. Gemini-TTS is paused (owner decision, 2026-10-25): step 1 compares Chatterbox and VoxCPM2 only, and testers choose between them on the listening site. Urdu still needs a separate engine (neither supports it).
