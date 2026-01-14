import subprocess
import re
from pathlib import Path

# ========= 使用者參數 =========
INPUT_DIR = Path("C:/Users/b9220/Desktop/input_m4a")
# OUTPUT_DIR = Path("C:/Users/b9220/Desktop/input_m4a")
OUTPUT_DIR = Path("C:/Users/b9220/Desktop/output_m4a")

SILENCE_DB = -28        # 靜音門檻
SILENCE_DURATION = 0.5 # 靜音需持續多久才算
MIN_SEGMENT_SEC = 0.5  # 最短輸出段落（避免碎檔）
# ==============================


def detect_silence(file):
    """
    回傳 [(silence_start, silence_end), ...]
    """
    cmd = [
        "ffmpeg",
        "-i", str(file),
        "-af", f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_DURATION}",
        "-f", "null",
        "-"
    ]

    p = subprocess.Popen(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )

    silence = []
    start = None

    for line in p.stderr:
        if "silence_start" in line:
            start = float(re.search(r"silence_start: ([0-9.]+)", line).group(1))
        elif "silence_end" in line:
            end = float(re.search(r"silence_end: ([0-9.]+)", line).group(1))
            silence.append((start, end))
            start = None

    return silence


def get_duration(file):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file)
    ]
    return float(subprocess.check_output(cmd))


def split_file(file):
    duration = get_duration(file)
    silences = detect_silence(file)

    segments = []
    prev_end = 0.0

    for s_start, s_end in silences:
        if s_start - prev_end >= MIN_SEGMENT_SEC:
            segments.append((prev_end, s_start))
        prev_end = s_end

    if duration - prev_end >= MIN_SEGMENT_SEC:
        segments.append((prev_end, duration))

    for idx, (start, end) in enumerate(segments):
        out = OUTPUT_DIR / f"{file.stem}_part_{idx:03d}.m4a"

        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{start}",
            "-to", f"{end}",
            "-i", str(file),
            "-c", "copy",
            str(out)
        ]

        subprocess.run(cmd, check=True)


def main():
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    files = list(input_dir.glob("*.m4a"))

    if not files:
        print("❌ 找不到 m4a")
        return

    for f in files:
        print(f"▶ 切割中：{f.name}")
        split_file(f)

    print("✅ 全部完成")


if __name__ == "__main__":
    main()