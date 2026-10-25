# Handoff: Jungle CID (read this first)

You are continuing a project with Navneet. A previous Claude session (a cloud session that could not reach Navneet's computer) built a pipeline that turns story scripts into finished vertical Hindi shorts. Your job on this Mac session: use Navneet's own Chrome (Claude in Chrome) to generate each episode's clips in Google Flow, then build the finished video with the tool.

## The project
- Repo: github.com/Navneetsingh-AI/Navneetsingh-AI, branch `claude/upbeat-ritchie-aze6ei`, folder `ai-video-studio/`.
- Series `jungle-cid` ("Jungle CID"): a 30-second-per-episode Hindi comedy-mystery for Instagram Reels and YouTube Shorts, about animals in an Indian village where things keep going missing.
- Read these files first: `README.md`, `series/jungle-cid/ARC.md` (season plan, locked twist and clue tracker), `FLOW_RUNBOOK.md` (the exact procedure for Flow), `series/jungle-cid/bible.json`, `series/jungle-cid/episodes/ep0N.json`.

## Cast (saved as characters in Navneet's Flow, each with a portrait, body, voice and info)
- **Bhola**: very innocent, very dumb sloth bear (red-yellow checked scarf). Believes whatever he is told and panics: "क्या मैं ही चोर हूँ?". Deep, slow voice.
- **Kallu**: sarcastic crow (green turban with one upright feather). Secretly behind the thefts, uses Bhola's innocence. Fast, high, raspy voice (Flow voice "Fenrir custom").
- **Chikki**: bold investigator (a sandy-gold desert fox with huge ears, round glasses, plum-purple long coat, cream scarf, magnifying glass). Girlish, sharp, fast, straightforward voice.
- **Chulbul**: tiny white rat (brown newsboy cap, sky-blue vest, bandaged tail). Chikki's chaotic sidekick. Fast, squeaky voice. **Secret: he is the boss behind everything (locked twist). Never reveal it early; hide the clues from `ARC.md` in the background.**
- Saaya (ninja) was cut from this series. Do not use him.

## Status
- Episode 1: built and delivered (4 shots).
- Episode 2: scripted (5 shots), `series/jungle-cid/episodes/ep02.json`. Clips NOT generated yet. This is the first job.
- Episode 3: scripted (5 shots). Episodes 4-10 are outlined in `ARC.md`, not scripted.

## Flow rules learned the hard way
- A shot can attach at most **3 saved characters**, and at most **2 should speak**, or voices get swapped. `python -m studio prompts ...` prints a WARNING when a shot breaks this.
- Flow's filter ("third-party content providers") blocked prompts that described Chikki as a fox / detective / trench coat, used the word "Pixar", and used "secret agent". Refer to characters **by name only**; the saved character supplies the look. If a prompt is blocked, retry once, then stop and ask Navneet. Never try to evade the filter.
- Clips are 8 seconds, vertical 9:16, Veo 3.1 Fast for tests. About 20 credits per Fast clip.
- Start each shot after the first from the last frame of the previous clip when Flow offers it.

## Pipeline (run inside `ai-video-studio/`; use `.venv/bin/python` after `setup_mac.sh`)
- `python -m studio prompts jungle-cid ep02` writes the per-shot prompts to `series/jungle-cid/out/ep02/flow_prompts.md`.
- Save clips as `series/jungle-cid/clips/ep02/shot01.mp4` ... `shot05.mp4`.
- `python -m studio build jungle-cid ep02` builds the final video (keeps Flow's voices, hand-or-auto-timed Hindi captions coloured by speaker, an end card "पार्ट N जल्द आ रहा है! बने रहिए!", and fills in Flow's corner marks). Output: `series/jungle-cid/out/ep02/ep02.mp4`. The first build downloads a Whisper model (about 460 MB); `--no-whisper` skips it.
- Captions: automatic timing can be wrong on fast, overlapping lines. Check a few frames; a shot can carry a hand-timed `"captions"` track (see README).
- Do not mention Diwali anywhere; Navneet does not want it.

## Rules
- Never type passwords or payment details. Stop on any sign-in, payment or settings screen.
- Tell Navneet the expected credit cost before generating, and stop if credits run low.
- You cannot judge audio quality. Say so, and ask Navneet to listen for wrong voices, cut-off lines and caption timing.
- Posting requires marking the video as AI-generated. The invisible SynthID mark stays.
- Google's terms may restrict automated use of Flow; remind Navneet once.
- Do not push video files to git (they are ignored).

## How Navneet likes to work
Short plain English, step by step. Give prompts in full in the chat. For creative work (prompts, scripts) he wants a professional film director's detail, one shot or episode at a time. Ask before long creative batches.

## First actions
1. Confirm you can see Navneet's signed-in Flow tab and the four saved characters.
2. Run `bash setup_mac.sh` if `.venv` does not exist.
3. Tell Navneet the plan and the credit cost for episode 2 (5 shots, about 100 credits), then follow `FLOW_RUNBOOK.md` for series `jungle-cid`, episode `ep02`.
