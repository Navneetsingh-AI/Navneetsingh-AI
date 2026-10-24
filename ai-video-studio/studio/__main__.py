"""Usage:
  python -m studio prompts jungle-ninja ep01        # write Flow prompts for each shot
  python -m studio build   jungle-ninja ep01        # clips + Hindi voice -> final mp4
  python -m studio build   jungle-ninja ep01 --dry-run --placeholders   # offline pipeline test
"""
import argparse
from pathlib import Path

from . import assemble, story

ROOT = Path(__file__).resolve().parent.parent / "series"


def main():
    p = argparse.ArgumentParser(prog="studio")
    p.add_argument("command", choices=["prompts", "build"])
    p.add_argument("series")
    p.add_argument("episode")
    p.add_argument("--dry-run", action="store_true", help="skip TTS, use silent audio of estimated length")
    p.add_argument("--voice", choices=["flow", "tts"], help="flow = keep Flow's voices (default per series); tts = Edge TTS Hindi")
    p.add_argument("--no-whisper", action="store_true", help="skip Whisper, time captions from silence only")
    p.add_argument("--placeholders", action="store_true", help="use stand-in clips for any missing shotNN.mp4")
    a = p.parse_args()

    series_dir = ROOT / a.series
    bible = story.load_series(series_dir)
    episode = story.load_episode(series_dir, a.episode)

    for w in story.check_shots(episode):
        print(f"WARNING {w}")

    if a.command == "prompts":
        out = series_dir / "out" / a.episode
        out.mkdir(parents=True, exist_ok=True)
        path = out / "flow_prompts.md"
        path.write_text(story.flow_prompts_markdown(bible, episode), encoding="utf-8")
        print(f"Wrote {path}\nSave generated clips as {series_dir / 'clips' / a.episode}/shot01.mp4, shot02.mp4, ...")
    else:
        final, total = assemble.build(series_dir, a.episode, bible, episode, a.dry_run, a.placeholders, a.voice, not a.no_whisper)
        print(f"Built {final} ({total:.1f}s)")


if __name__ == "__main__":
    main()
