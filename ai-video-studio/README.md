# AI Video Studio

Turns a written story into a finished vertical (9:16) Hindi short for Instagram Reels and YouTube Shorts.

Claude writes the story, Google Flow draws and voices each shot with saved characters, and this tool adds Hindi captions, music and an end card and joins the shots into one video.

## Setup (once)

Needs Python 3.10+ and ffmpeg.

```bash
cd ai-video-studio
pip install -r requirements.txt
```

The first build downloads a speech model (about 460 MB) used to time the captions. If that fails or you skip it (`--no-whisper`), captions are timed from pauses in the audio, which is a little less exact.

## Making an episode (series `jungle-ninja`, episode `ep01`)

1. **Characters in Flow (once per series).** Each character is saved in Flow with a portrait, a body, a voice and character info. Voices used: Bhola, Kallu (Fenrir), Chikki (Autonoe), Saaya (Algenib).

2. **Get the prompts**
   ```bash
   python -m studio prompts jungle-ninja ep01
   ```
   Open `series/jungle-ninja/out/ep01/flow_prompts.md`.

3. **Generate each shot in Flow.** Attach the saved characters named in the prompt, paste the prompt, generate. For shot 2 onward, start from the last frame of the previous clip. Save the clips as:
   ```
   series/jungle-ninja/clips/ep01/shot01.mp4 ... shot05.mp4
   ```

4. **Build**
   ```bash
   python -m studio build jungle-ninja ep01
   ```
   Output: `series/jungle-ninja/out/ep01/ep01.mp4`

Optional: drop a royalty-free music file (mp3/wav/m4a) into `series/jungle-ninja/music/`. It plays quietly under the voices.

## Voice modes

- `flow` (default for this series): keeps the voices Flow generated, with lip sync. The tool only works out when each line is spoken so the coloured captions match.
- `tts`: replaces Flow's audio with free Edge TTS Hindi voices (no lip sync). Use `--voice tts`.

## Testing without Flow clips

```bash
python -m studio build jungle-ninja ep01 --placeholders --no-whisper
```
Uses green placeholder clips for any missing shots.

## Files

| File | Job |
| --- | --- |
| `series/<name>/bible.json` | The cast (look, caption colour, speaking pace), the visual style and the voice mode. |
| `series/<name>/episodes/epNN.json` | The episode script: shots, Hindi lines and who speaks. Keep each shot to about 15 spoken words. |
| `studio/story.py` | Builds the Flow prompts. |
| `studio/align.py` | Finds when each line is spoken in a clip (Whisper, or pauses as a fallback). |
| `studio/captions.py` | Coloured Hindi captions, a few words at a time. |
| `studio/voice.py` | Edge TTS Hindi voices for `tts` mode. |
| `studio/assemble.py` | Trims each clip to its dialogue, adds captions and music, renders the final video. |

## Writing the next episode

Copy `episodes/ep01.json` to `ep02.json` and write the next part. End each episode on a cliffhanger, and change the premise or stakes between episodes instead of repeating the same setup.

## Before you post

- Mark the video as AI-generated when YouTube or Instagram asks.
- Watch every video before publishing. This tool does not post for you.
