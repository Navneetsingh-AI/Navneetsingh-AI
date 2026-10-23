"""Works out when each scripted Hindi line is spoken inside a Flow clip that already contains its own voices.

Primary method: Whisper (faster-whisper) gives word timestamps; script words are mapped onto them by position.
Fallback (no Whisper / no model): silence detection finds the voiced stretches and the lines are spread over them,
weighted by text length and each character's speaking pace, then snapped to the nearest pause.
"""
import re
import subprocess

NOISE_DB = -38
MIN_PAUSE = 0.12
SNAP_WINDOW = 1.5
_model = None


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def voiced_segments(path, total):
    """[(start, end)] stretches where the clip's audio is above the noise floor."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af",
                        f"silencedetect=noise={NOISE_DB}dB:d={MIN_PAUSE}", "-f", "null", "-"],
                       capture_output=True, text=True)
    sil, start = [], None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            start = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and start is not None:
            sil.append((start, float(m.group(1))))
            start = None
    if start is not None:
        sil.append((start, total))
    voiced, t = [], 0.0
    for s, e in sil:
        if s - t > 0.05:
            voiced.append((t, s))
        t = e
    if total - t > 0.05:
        voiced.append((t, total))
    # A short blip before a clear pause at the very start is a sound effect, not speech.
    if len(voiced) > 2 and voiced[0][1] - voiced[0][0] < 0.55 and voiced[1][0] - voiced[0][1] >= 0.25:
        voiced = voiced[1:]
    return voiced


def asr_words(path):
    """[(start, end)] per spoken word from Whisper, or None if unavailable."""
    global _model
    try:
        from faster_whisper import WhisperModel

        if _model is None:
            _model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = _model.transcribe(str(path), language="hi", word_timestamps=True)
        words = [(w.start, w.end) for seg in segments for w in (seg.words or [])]
        return words or None
    except Exception as exc:  # missing package, offline model download, etc.
        print(f"  (Whisper unavailable: {type(exc).__name__}; using silence-based timing)")
        return None


def _flatten(lines):
    return [(i, w) for i, line in enumerate(lines) for w in line["hi"].split()]


def _from_asr(lines, words, asr):
    out = [[None, None] for _ in lines]
    n, m = len(words), len(asr)
    for k, (li, _) in enumerate(words):
        a = asr[min(m - 1, round(k * (m - 1) / max(n - 1, 1)))]
        out[li][0] = a[0] if out[li][0] is None else out[li][0]
        out[li][1] = a[1]
    return [tuple(x) for x in out]


def _from_silence(lines, words, voiced, pace, total):
    if not voiced:  # silent clip (e.g. placeholder): spread evenly
        voiced = [(0.4, max(0.8, total - 0.6))]
    weights = [len(w) * pace.get(lines[li]["speaker"], 1.0) + 1 for li, w in words]
    span = sum(e - s for s, e in voiced)
    cum, acc = [], 0.0
    for w in weights:
        cum.append(acc)
        acc += w
    cum.append(acc)

    def at(frac):  # position in voiced time -> absolute time
        left = frac * span
        for s, e in voiced:
            if left <= e - s:
                return s + left
            left -= e - s
        return voiced[-1][1]

    gaps = [(voiced[i][1], voiced[i + 1][0]) for i in range(len(voiced) - 1)]
    bounds = []  # absolute (end_of_line_k, start_of_line_k+1)
    last_gap = -1
    for li in range(len(lines) - 1):
        k = sum(1 for x, _ in words if x <= li)
        target = at(cum[k] / acc)
        best, best_d = None, SNAP_WINDOW
        for gi, (gs, ge) in enumerate(gaps):
            if gi > last_gap and abs((gs + ge) / 2 - target) < best_d:
                best, best_d = gi, abs((gs + ge) / 2 - target)
        if best is None:
            bounds.append((target, target))
        else:
            bounds.append(gaps[best])
            last_gap = best
    starts = [voiced[0][0]] + [b[1] for b in bounds]
    ends = [b[0] for b in bounds] + [voiced[-1][1]]
    return list(zip(starts, ends))


def line_times(clip, lines, characters, use_whisper=True):
    """Returns ([(start, end)] per line, speech_end) in clip time."""
    total = duration(clip)
    voiced = voiced_segments(clip, total)
    words = _flatten(lines)
    asr = asr_words(clip) if (use_whisper and voiced and words) else None
    if asr and len(asr) >= 2:
        times = _from_asr(lines, words, asr)
    else:
        pace = {k: v.get("pace", 1.0) for k, v in characters.items()}
        times = _from_silence(lines, words, voiced, pace, total)
    speech_end = max([e for _, e in times] + [voiced[-1][1] if voiced else 0])
    return times, speech_end
