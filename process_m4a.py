import subprocess
import re
from pathlib import Path
import tempfile
import os

# ========= 使用者設定 =========
INPUT_DIR = Path("C:/Users/b9220/Desktop/input_m4a")
OUTPUT_DIR = Path("C:/Users/b9220/Desktop/output_m4a")

SILENCE_DB = -35
SILENCE_DURATION = 1.0
MIN_SEGMENT_SEC = 1.0

THRESHOLD_DB = -38      # dB
MIN_SILENCE = 0.5     # seconds
PADDING = 0.0         # seconds

EDGE_SILENCE_DB = -32        # 修邊用（可比主門檻稍低）
EDGE_SILENCE_DURATION = 0.2 # 頭尾靜音判定
# =============================

silence_start_re = re.compile(r"silence_start: ([0-9\.]+)")
silence_end_re = re.compile(r"silence_end: ([0-9\.]+)")

silence_start_re = re.compile(r"silence_start: ([0-9\.]+)")
silence_end_re = re.compile(r"silence_end: ([0-9\.]+)")

def detect_silence(file):
    cmd = [
        "ffmpeg",
        "-i", str(file),
        "-af", f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_DURATION}",
        "-f", "null", "-"
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


def trim_edges(input_file, output_file):
    """
    移除單一音檔的頭尾靜音
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-af",
        f"silenceremove="
        f"start_periods=1:"
        f"start_duration={EDGE_SILENCE_DURATION}:"
        f"start_threshold={EDGE_SILENCE_DB}dB:"
        f"stop_periods=1:"
        f"stop_duration={EDGE_SILENCE_DURATION}:"
        f"stop_threshold={EDGE_SILENCE_DB}dB",
        "-c:a", "aac",
        str(output_file)
    ]
    subprocess.run(cmd, check=True)

def detect_range(filepath):
    cmd = [
        "ffmpeg",
        "-i", filepath,
        "-af", f"silencedetect=noise={THRESHOLD_DB}dB:d={MIN_SILENCE}",
        "-f", "null", "-"
    ]

    result = subprocess.run(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    starts = []
    ends = []

    for line in result.stderr.splitlines():
        if m := silence_start_re.search(line):
            starts.append(float(m.group(1)))
        if m := silence_end_re.search(line):
            ends.append(float(m.group(1)))

    # 預設值（整段都有聲）
    start = 0.0
    end = None

    # 如果開頭是靜音，會先看到 silence_end
    if ends:
        start = ends[0]

    # 如果結尾是靜音，會看到 silence_start
    if starts:
        end = starts[-1]

    # padding
    start = max(0, start - PADDING)
    if end is not None:
        end += PADDING

    # 防呆：避免 end <= start
    if end is not None and end <= start:
        end = None

    return start, end

def trim_file(input_path, output_path):
    start, end = detect_range(input_path)

    cmd = ["ffmpeg", "-y", "-i", input_path]

    if start > 0:
        cmd += ["-ss", f"{start:.3f}"]

    if end is not None:
        cmd += ["-to", f"{end:.3f}"]

    cmd += ["-c:a", "aac", "-movflags", "+faststart", output_path]

    subprocess.run(cmd, check=True)

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
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        # 先快速切
        cut_cmd = [
            "ffmpeg", "-y",
            "-ss", f"{start}",
            "-to", f"{end}",
            "-i", str(file),
            "-c", "copy",
            str(tmp_path)
        ]
        subprocess.run(cut_cmd, check=True)

        # 再修頭尾靜音
        final_out = OUTPUT_DIR / f"{file.stem}_part_{idx:03d}.m4a"
        # trim_edges(tmp_path, final_out)
        trim_file(tmp_path, final_out)

        os.remove(tmp_path)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    files = list(INPUT_DIR.glob("*.m4a"))
    if not files:
        print("❌ 找不到 m4a")
        return

    for f in files:
        print(f"▶ 處理中：{f.name}")
        split_file(f)

    print("✅ 全部完成（已清除每段頭尾靜音）")


if __name__ == "__main__":
    main()
