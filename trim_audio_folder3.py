import os
import subprocess
import re

# INPUT_DIR = "input_m4a"
# OUTPUT_DIR = "output_m4a"
INPUT_DIR = "C:/Users/b9220/Desktop/input_m4a"
OUTPUT_DIR = "C:/Users/b9220/Desktop/output_m4a"

THRESHOLD_DB = -32      # dB
MIN_SILENCE = 0.05     # seconds
PADDING = 0.0         # seconds

os.makedirs(OUTPUT_DIR, exist_ok=True)

silence_start_re = re.compile(r"silence_start: ([0-9\.]+)")
silence_end_re = re.compile(r"silence_end: ([0-9\.]+)")

silence_start_re = re.compile(r"silence_start: ([0-9\.]+)")
silence_end_re = re.compile(r"silence_end: ([0-9\.]+)")

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

def batch():
    for fname in os.listdir(INPUT_DIR):
        if not fname.lower().endswith(".m4a"):
            continue

        inp = os.path.join(INPUT_DIR, fname)
        out = os.path.join(OUTPUT_DIR, "trimmed_" + fname)

        try:
            trim_file(inp, out)
            print(f"✅ 完成：{fname}")
        except Exception as e:
            print(f"❌ 失敗：{fname}")
            print(e)

if __name__ == "__main__":
    batch()