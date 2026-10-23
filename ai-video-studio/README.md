# AI Video Studio

Turns a written story into a finished vertical (9:16) Hindi short, ready for Instagram Reels and YouTube Shorts.

Claude writes the story, Google Flow draws the shots, and this tool adds Hindi voices, captions and music and joins everything into one video.

## Setup (once)

Needs Python 3.10+ and ffmpeg.

```bash
cd ai-video-studio
pip install -r requirements.txt
```

## Making an episode (series `jungle-ninja`, episode `ep01`)

1. **Get the Flow prompts**
   ```bash
   python -m studio prompts jungle-ninja ep01
   ```
   Open `series/jungle-ninja/out/ep01/flow_prompts.md`.

2. **Generate each shot in Google Flow.** Paste prompt `shot01`, generate, download. For `shot02` onward, start from the last frame of the previous clip (Flow's "Frames to Video") so the characters match. Save the clips as:
   ```
   series/jungle-ninja/clips/ep01/shot01.mp4
   series/jungle-ninja/clips/ep01/shot02.mp4
   ...
   ```

3. **Build the video**
   ```bash
   python -m studio build jungle-ninja ep01
   ```
   Output: `series/jungle-ninja/out/ep01/ep01.mp4`

Optional: drop a royalty-free music file (mp3/wav/m4a) into `series/jungle-ninja/music/`. It plays quietly under the voices.

## Testing without Flow clips or internet

```bash
python -m studio build jungle-ninja ep01 --dry-run --placeholders
```
Uses green placeholder clips and silent audio of the right length, so you can check timing and captions.

## How it fits together

| File | Job |
| --- | --- |
| `series/<name>/bible.json` | The cast: looks, caption colour and Hindi voice per character. The look text is pasted into every prompt to keep characters consistent. |
| `series/<name>/episodes/epNN.json` | The episode script: shots, Hindi lines and who speaks. |
| `studio/story.py` | Builds the Flow prompts. |
| `studio/voice.py` | Hindi voice per line using Edge TTS (free). Lines are cached, so rebuilds are fast. |
| `studio/captions.py` | Coloured Hindi captions, a few words at a time. |
| `studio/assemble.py` | Fits each clip to its dialogue, mixes the audio and renders the final video. |

## Voices

Edge TTS has two Hindi voices: `hi-IN-MadhurNeural` (male) and `hi-IN-SwaraNeural` (female). Characters sound different through pitch and speed settings in `bible.json`. If they sound too flat, the voice step in `voice.py` is the only thing to swap for a paid service.

## Writing the next episode

Copy `episodes/ep01.json` to `ep02.json` and write the next part. End each one on a cliffhanger, and change the premise or the stakes between episodes. Don't repeat the same setup each time.

## Before you post

- Mark the video as AI-generated when YouTube or Instagram asks.
- Review every video before publishing. This tool does not post for you.
