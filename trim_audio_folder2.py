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

def detect_audio_range(filepath):
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

    silence_starts = []
    silence_ends = []

    for line in result.stderr.splitlines():
        if m := silence_start_re.search(line):
            silence_starts.append(float(m.group(1)))
        if m := silence_end_re.search(line):
            silence_ends.append(float(m.group(1)))

    if not silence_starts and not silence_ends:
        return 0, None

    start = silence_ends[0] if silence_ends else 0
    end = silence_starts[-1] if silence_starts else None

    start = max(0, start - PADDING)
    if end is not None:
        end += PADDING

    return start, end

def trim_file(input_path, output_path):
    start, end = detect_audio_range(input_path)

    cmd = ["ffmpeg", "-y", "-i", input_path]

    if start > 0:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]

    cmd += ["-c:a", "aac", "-movflags", "+faststart", output_path]

    subprocess.run(cmd, check=True)

def batch_process():
    for fname in os.listdir(INPUT_DIR):
        if not fname.lower().endswith(".m4a"):
            continue

        input_path = os.path.join(INPUT_DIR, fname)
        output_path = os.path.join(OUTPUT_DIR, "trimmed_"+fname)

        try:
            trim_file(input_path, output_path)
            print(f"✅ 完成：{fname}")
        except Exception as e:
            print(f"❌ 失敗：{fname}")
            print(e)

if __name__ == "__main__":
    batch_process()
