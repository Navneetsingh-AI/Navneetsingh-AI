"""Loads a series bible + episode script and turns them into Google Flow prompts."""
import json
from pathlib import Path

CLIP_SECONDS = 8


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_series(series_dir):
    return load_json(Path(series_dir) / "bible.json")


def load_episode(series_dir, episode):
    return load_json(Path(series_dir) / "episodes" / f"{episode}.json")


def shot_characters(shot):
    """Characters that must appear in the picture: speakers plus anyone listed in `cast`."""
    names = list(shot.get("cast", []))
    for line in shot.get("lines", []):
        if line["speaker"] not in names:
            names.append(line["speaker"])
    return names


def flow_prompt(bible, episode, index, shot):
    chars = shot_characters(shot)
    look = "\n".join(f"- {bible['characters'][c]['name_en']}: {bible['characters'][c]['look']}" for c in chars)
    continuity = ""
    if index > 0:
        continuity = (
            f"\nContinuity: start from the last frame of shot{index:02d} "
            "(use Flow's 'Frames to Video' / 'Extend' with that frame) so characters and set match.\n"
        )
    return (
        f"{bible['style']}\n\n"
        f"Characters (keep their looks exactly as described):\n{look}\n\n"
        f"Scene: {shot['visual']}\n"
        f"Camera: {shot.get('camera', 'steady medium shot, slight handheld energy')}\n"
        f"Setting: {bible['world']}\n"
        f"{continuity}"
        f"Format: vertical 9:16, {CLIP_SECONDS} seconds.\n"
        "Audio: ambient jungle-village sounds and sound effects only. No dialogue, no narration, "
        "no music, no on-screen text, no captions, no logos."
    )


def flow_prompts_markdown(bible, episode):
    out = [f"# {bible['title']} - {episode['title']}\n"]
    out.append(
        "Paste each prompt into Google Flow, generate, download, and save the clip as "
        "`clips/<episode>/shotNN.mp4` (e.g. `shot01.mp4`). Spoken Hindi is added later by the "
        "studio, so keep Flow's audio off or ignore it.\n"
    )
    for i, shot in enumerate(episode["shots"]):
        out.append(f"## shot{i + 1:02d}\n")
        out.append("```text\n" + flow_prompt(bible, episode, i, shot) + "\n```\n")
    return "\n".join(out)
