import os
from pydub import AudioSegment
import numpy as np

# INPUT_DIR = "input_m4a"
# OUTPUT_DIR = "output_m4a"
INPUT_DIR = "C:/Users/b9220/Desktop/input_m4a"
OUTPUT_DIR = "C:/Users/b9220/Desktop/output_m4a"
THRESHOLD_DB = -40.0   # dBFS 門檻
FRAME_MS = 10      # 分析精度（毫秒）
PADDING_MS = 100      # 前後保留時間
# PADDING_MS = 0      # 前後保留時間

os.makedirs(OUTPUT_DIR, exist_ok=True)

def trim_audio_by_db(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    # print(len(audio))

    frames = [
        audio[i:i + FRAME_MS]
        for i in range(0, len(audio), FRAME_MS)
    ]

    dbs = np.array([f.dBFS for f in frames])
    # print(dbs)

    valid = np.where(dbs >= THRESHOLD_DB)[0]

    if len(valid) == 0:
        print(f"⚠️ 無有效音訊：{os.path.basename(input_path)}")
        return

    # start_ms = max(0, valid[0] * FRAME_MS - PADDING_MS)
    start_ms = max(0, valid[0] * FRAME_MS)
    end_ms = min(len(audio), (valid[-1] + 1) * FRAME_MS + PADDING_MS)
    # end_ms = len(audio)
    # print(valid)
    # print(valid[0], start_ms)
    # print(valid[-1], end_ms)

    trimmed = audio[start_ms:end_ms]
    # print([start_ms,end_ms])
    trimmed.export(
        output_path,
        format="mp4",
        codec="aac"
    )

    print(f"✅ 處理完成：{os.path.basename(input_path)}")

def batch_process():
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".m4a")]

    if not files:
        print("❌ 找不到 m4a 檔案")
        return

    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, "trimmed_"+filename)

        try:
            trim_audio_by_db(input_path, output_path)
        except Exception as e:
            print(f"❌ 錯誤：{filename}")
            print(e)

if __name__ == "__main__":
    batch_process()
