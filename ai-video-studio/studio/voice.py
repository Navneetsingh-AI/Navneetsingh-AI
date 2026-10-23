"""Hindi text-to-speech per dialogue line (Microsoft Edge neural voices via edge-tts)."""
import asyncio
import hashlib
import subprocess
import wave
from pathlib import Path

SAMPLE_RATE = 48000


def _run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def _cache_path(cache_dir, text, voice):
    key = hashlib.sha1(f"{voice['name']}|{voice.get('rate')}|{voice.get('pitch')}|{text}".encode("utf-8")).hexdigest()[:16]
    return Path(cache_dir) / f"{key}.wav"


async def _edge_save(text, voice, mp3_path):
    import edge_tts

    comm = edge_tts.Communicate(text, voice["name"], rate=voice.get("rate", "+0%"), pitch=voice.get("pitch", "+0Hz"))
    await comm.save(str(mp3_path))


def _silent_wav(path, seconds):
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
          "-t", f"{seconds:.2f}", "-c:a", "pcm_s16le", str(path)])


def synth_line(text, voice, cache_dir, dry_run=False):
    """Returns a mono 48k wav path for one line. dry_run writes silence of a plausible length."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    wav = _cache_path(cache_dir, text, voice)
    if dry_run:
        wav = wav.with_suffix(".dry.wav")
    if wav.exists():
        return wav
    if dry_run:
        _silent_wav(wav, max(0.8, len(text) * 0.065))
        return wav
    mp3 = wav.with_suffix(".mp3")
    asyncio.run(_edge_save(text, voice, mp3))
    _run(["ffmpeg", "-y", "-i", str(mp3), "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s16le", str(wav)])
    mp3.unlink()
    return wav


def wav_seconds(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def mix_lines(segments, total_seconds, out_path):
    """segments: [(start_seconds, wav_path)] -> one mono wav of total_seconds with the lines placed."""
    frames = int(total_seconds * SAMPLE_RATE)
    buf = bytearray(frames * 2)
    for start, path in segments:
        with wave.open(str(path), "rb") as w:
            data = w.readframes(w.getnframes())
        offset = int(start * SAMPLE_RATE) * 2
        end = min(offset + len(data), len(buf))
        buf[offset:end] = data[: end - offset]
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(bytes(buf))
    return out_path
