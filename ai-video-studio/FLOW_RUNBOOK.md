# Flow runbook: generate an episode's clips in the person's own Chrome

For a Claude session running on the person's computer with Claude in Chrome connected. Read the chrome-browser skill first.

## Goal
Generate every shot of one episode in Google Flow, download the clips under the right names, then build the finished video with this repo's tool.

Example request: "Follow FLOW_RUNBOOK.md for series `jungle-cid`, episode `ep02`."

## Before you start
1. In the repo folder: `git pull origin claude/upbeat-ritchie-aze6ei`, then `cd ai-video-studio` and `pip install -r requirements.txt`.
2. `python -m studio prompts <series> <episode>` writes `series/<series>/out/<episode>/flow_prompts.md`, one prompt per shot. If it prints a WARNING, stop and tell the person.
3. Open Flow in the person's signed-in Chrome. Check the saved characters Bhola, Kallu, Chikki and Chulbul exist. If not, stop and tell the person.
4. Check the credit balance on screen. Each 8-second Fast clip costs about 20 credits. Tell the person the expected total (shots x 20) before you begin, and stop if the balance is lower.

## For each shot, in order (shot01, shot02, ...)
1. Start a new video in the Flow project. Settings: model Veo 3.1 Fast, vertical 9:16, 8 seconds, one clip.
2. Attach exactly the saved characters named in the prompt's "Characters" line. Never more than 3.
3. Shots after the first: start from the last frame of the previous clip if Flow offers it.
4. Paste the master look block (below) and then the shot's prompt from `flow_prompts.md`. Leave out the "Characters (attach these saved Flow characters)" line itself, which is an instruction to you.
5. Generate and wait for the clip. Do not click anything else while it renders.
6. Check the result: right characters, no obvious artefacts, the line count and order look right. You cannot judge audio quality; do not claim to.
7. Download it and save it as `series/<series>/clips/<episode>/shotNN.mp4` (shot01.mp4, shot02.mp4, ...).

## Stop and ask the person when
- Flow shows "can't generate ... third-party content providers". Try the same prompt once more. If it fails again, stop. Do not rewrite the prompt on your own and do not try to get around the filter.
- Any sign-in, payment, subscription or settings screen appears. Never enter passwords or payment details.
- The credit balance would run out.
- A clip has the wrong characters or voices swapped. Regenerate at most once, then ask.
- Flow looks different from what these steps describe. Describe what you see.

## Master look block (paste before each shot's prompt)
Premium 3D animated family comedy-mystery with expressive faces, believable fur and feather detail, soft physically-based lighting. World: a warm Indian jungle village at festival time, with mud-and-bamboo huts, terracotta roofs, strings of marigold garlands, rows of clay diyas, rangoli patterns, and one huge banyan tree at the centre of a dusty market square. Colour palette: saffron, marigold orange, warm earth browns and deep teal shadows. Cinematic 35mm full-frame look, shallow depth of field, gentle film grain, smooth motivated camera moves only. Vertical 9:16. Keep every face and key action inside the central 70% of the frame, with nothing important in the bottom 20% or top 12%. Audio: natural ambience and sound effects only. No music, no on-screen text, no captions, no subtitles, no logos. The characters speak Hindi in their own saved voices, one line at a time in the exact order given, with a short natural pause between speakers. Each line is spoken only by the character named, and only that character's mouth moves for it.

## After the last clip
1. Confirm every `shotNN.mp4` exists in `series/<series>/clips/<episode>/`.
2. `python -m studio build <series> <episode>`. The first run downloads a speech model of about 460 MB.
3. The finished video is `series/<series>/out/<episode>/<episode>.mp4`. Tell the person where it is and that they must listen to it for wrong voices and caption timing.
4. Remind them to mark the video as AI-generated when posting.

## Notes
- Only automate Flow if the person is fine with it. Google's terms may restrict automated use of Flow, and they should check.
- The tool removes Flow's corner marks from the picture by default. The invisible SynthID mark stays.
