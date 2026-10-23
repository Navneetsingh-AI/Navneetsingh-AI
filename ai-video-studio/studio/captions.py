"""Burned-in Hindi captions as an ASS subtitle file, coloured per speaker."""

MAX_WORDS = 4


def _ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _bgr(hex_rgb):
    h = hex_rgb.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&"


def _chunks(text):
    words = text.split()
    return [" ".join(words[i:i + MAX_WORDS]) for i in range(0, len(words), MAX_WORDS)] or [text]


def build_ass(events, end_card, end_start, total_seconds, font_name="Noto Sans Devanagari"):
    """events: [(start, end, text, colour_hex)]. end_card: text shown from end_start to total_seconds."""
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,{font_name},118,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,420,1
Style: End,{font_name},130,&H0000E5FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,2,5,60,60,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = []
    for start, end, text, colour in events:
        chunks = _chunks(text)
        weights = [max(len(c), 1) for c in chunks]
        span = end - start
        t = start
        for chunk, weight in zip(chunks, weights):
            dur = span * weight / sum(weights)
            pop = r"{\fscx85\fscy85\t(0,120,\fscx100\fscy100)" + rf"\c{_bgr(colour)}" + "}"
            lines.append(f"Dialogue: 0,{_ass_time(t)},{_ass_time(t + dur)},Default,,0,0,0,,{pop}{chunk}")
            t += dur
    if end_card:
        lines.append(f"Dialogue: 1,{_ass_time(end_start)},{_ass_time(total_seconds)},End,,0,0,0,,{end_card.replace(chr(10), chr(92) + 'N')}")
    return header + "\n".join(lines) + "\n"
