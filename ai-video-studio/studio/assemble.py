"""Builds the final 9:16 episode: trims/pads clips to the dialogue, mixes Hindi voices, burns captions."""
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

from . import captions, voice

W, H, FPS = 1080, 1920, 30
LEAD, GAP, TAIL = 0.35, 0.25, 0.55  # seconds before first line, between lines, after last line
MIN_SHOT = 2.5
END_CARD_SECONDS = 1.8
AMBIENT_VOLUME = 0.18
MUSIC_VOLUME = 0.10
FONT_DIR = Path(__file__).parent / "fonts"


def _run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")


def _has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def _placeholder_clip(path, label, seconds=8):
    """Stand-in for a Flow clip so the whole pipeline can be tested without generating video."""
    txt = path.with_suffix(".txt")
    txt.write_text("\n".join(textwrap.wrap(label, 28)), encoding="utf-8")
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    vf = f"drawtext=fontfile={font}:textfile={txt}:fontcolor=white:fontsize=56:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=14"
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x2d6a4f:s={W}x{H}:d={seconds}:r={FPS}",
          "-vf", vf, "-pix_fmt", "yuv420p", str(path)])
    txt.unlink()


def _find_clip(clips_dir, n):
    for ext in ("mp4", "mov", "webm", "mkv"):
        p = clips_dir / f"shot{n:02d}.{ext}"
        if p.exists():
            return p
    return None


def build(series_dir, episode_id, bible, episode, dry_run=False, placeholders=False):
    series_dir = Path(series_dir)
    clips_dir = series_dir / "clips" / episode_id
    out_dir = series_dir / "out" / episode_id
    work = out_dir / "work"
    cache = series_dir / ".cache" / "voice"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (work / "fonts").mkdir()
    shutil.copy(FONT_DIR / "NotoSansDevanagari.ttf", work / "fonts")

    shots = episode["shots"]
    timeline, cap_events, seg_files = [], [], []
    clock = 0.0

    for i, shot in enumerate(shots):
        n = i + 1
        clip = _find_clip(clips_dir, n)
        if clip is None:
            if not placeholders:
                raise SystemExit(f"Missing clip: {clips_dir}/shot{n:02d}.mp4  (use --placeholders to test without clips)")
            clips_dir.mkdir(parents=True, exist_ok=True)
            clip = work / f"placeholder{n:02d}.mp4"
            _placeholder_clip(clip, f"SHOT {n}: {shot['visual']}")

        # Lay the dialogue out on this shot's local timeline.
        t, placed = LEAD, []
        for line in shot.get("lines", []):
            ch = bible["characters"][line["speaker"]]
            wav = voice.synth_line(line["hi"], ch["voice"], cache, dry_run=dry_run)
            dur = voice.wav_seconds(wav)
            placed.append((t, t + dur, wav, line["hi"], ch["caption_color"]))
            t += dur + GAP
        speech_end = (t - GAP) if placed else LEAD
        length = max(MIN_SHOT, speech_end + TAIL)
        if i == len(shots) - 1:
            length += END_CARD_SECONDS

        voice_wav = work / f"voice{n:02d}.wav"
        voice.mix_lines([(s, w) for s, _, w, _, _ in placed], length, voice_wav)

        seg = work / f"seg{n:02d}.mp4"
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,"
              f"tpad=stop_mode=clone:stop_duration=10")
        cmd = ["ffmpeg", "-y", "-i", str(clip), "-i", str(voice_wav)]
        if _has_audio(clip):
            af = (f"[0:a]volume={AMBIENT_VOLUME},aresample={voice.SAMPLE_RATE},apad[amb];"
                  f"[1:a]apad[v];[amb][v]amix=inputs=2:duration=longest:normalize=0[a]")
            cmd += ["-filter_complex", f"[0:v]{vf}[v0];{af}", "-map", "[v0]", "-map", "[a]"]
        else:
            cmd += ["-vf", vf, "-map", "0:v", "-map", "1:a"]
        cmd += ["-t", f"{length:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", str(voice.SAMPLE_RATE), "-ac", "2", str(seg)]
        _run(cmd)
        seg_files.append(seg)

        for s, e, _, text, colour in placed:
            cap_events.append((clock + s, clock + e, text, colour))
        timeline.append({"shot": n, "start": round(clock, 2), "length": round(length, 2),
                         "lines": [{"speaker": l["speaker"], "hi": l["hi"]} for l in shot.get("lines", [])]})
        clock += length

    total = clock
    ass = captions.build_ass(cap_events, episode.get("end_card", ""), total - END_CARD_SECONDS, total)
    (work / "captions.ass").write_text(ass, encoding="utf-8")

    listing = work / "list.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in seg_files), encoding="utf-8")
    joined = work / "joined.mp4"
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "joined.mp4"], cwd=work)

    music = next(iter(sorted((series_dir / "music").glob("*.[mw][pa][34v]"))), None) if (series_dir / "music").exists() else None
    final = out_dir / f"{episode_id}.mp4"
    sub = "subtitles=captions.ass:fontsdir=fonts"
    if music:
        fc = (f"[0:v]{sub}[v];[1:a]aloop=loop=-1:size=2e9,volume={MUSIC_VOLUME}[m];"
              f"[0:a][m]amix=inputs=2:duration=first:normalize=0[a]")
        cmd = ["ffmpeg", "-y", "-i", "joined.mp4", "-i", str(music.resolve()), "-filter_complex", fc]
    else:
        fc = f"[0:v]{sub}[v]"
        cmd = ["ffmpeg", "-y", "-i", "joined.mp4", "-filter_complex", fc]
    cmd += ["-map", "[v]", "-map", "[a]" if music else "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(final.resolve())]
    _run(cmd, cwd=work)

    (out_dir / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return final, total
