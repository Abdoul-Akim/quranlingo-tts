# Licensing options (DRAFT, for the founder to decide; not legal advice)

The repository has two different things to license: **the code** and **the voices**.

## 1. The code

Every engine and tool we use allows any licence for our own code:

| Component | Licence |
|---|---|
| VoxCPM2 | Apache-2.0 |
| Chatterbox | MIT |
| Indic Parler-TTS, parler-tts | Apache-2.0 |
| pyworld, WORLD | MIT, modified BSD |
| faster-whisper, Whisper weights | MIT |
| Gradio, huggingface_hub, librosa, jiwer | Apache-2.0, Apache-2.0, ISC, Apache-2.0 |

We avoided Parselmouth (GPLv3), because a GPL dependency would force the repository to be GPL too.

Two common choices, both fine:

| | **Apache-2.0** (recommended) | **MIT** |
|---|---|---|
| Use, change, sell | Yes | Yes |
| Patent protection for users | Yes, explicit | No |
| Length | Long | Very short |
| Matches | VoxCPM2, Parler, Gradio | Chatterbox |

## 2. The voices

The founder's wish: anyone may use the voices, but only after asking permission, and never for harmful purposes. That is **not** an open-source licence, so the voices need their own terms, separate from the code. A draft is in `docs/VOICES_LICENSE_DRAFT.md`.

Things to decide before publishing the voices:

- **Which files are "the voices":** only the reference clips, or also generated audio?
- **Brand risk:** anyone with Ali's reference clip can make "Ali" say anything. Publishing the clips publicly lets people misuse them before asking. An alternative is to publish samples only and send the reference clips to people who are granted permission.
- **Children's voices:** Ali and Zahra sound like minors. Some providers (for example ElevenLabs) forbid child-like voices in their libraries. Our terms should explicitly forbid sexual, violent, deceptive or political use.
- **Watermarks:** Chatterbox output carries an inaudible watermark, which helps show where a clip came from.
- **The engines' own terms:** VoxCPM2 forbids impersonation, fraud and disinformation, and asks that AI-generated content is labelled. Our voice terms should pass these on.
