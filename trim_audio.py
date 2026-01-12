from pydub import AudioSegment
import numpy as np

def trim_audio_by_db(
    input_file,
    output_file,
    threshold_db=-4.0,
    frame_ms=10
):
    """
    移除開頭與結尾 dBFS 小於 threshold_db 的區段
    """
    audio = AudioSegment.from_file(input_file, format="m4a")

    frames = [
        audio[i:i + frame_ms]
        for i in range(0, len(audio), frame_ms)
    ]

    dbs = np.array([f.dBFS for f in frames])

    # 找到有效音量範圍
    valid_indices = np.where(dbs >= threshold_db)[0]

    if len(valid_indices) == 0:
        print("⚠️ 沒有找到高於門檻的音訊")
        return

    start_frame = valid_indices[0]
    end_frame = valid_indices[-1]

    start_ms = start_frame * frame_ms
    end_ms = min((end_frame + 1) * frame_ms, len(audio))

    padding = 200
    start_ms = max(0, start_ms - padding)
    end_ms = min(len(audio), end_ms + padding)

    trimmed_audio = audio[start_ms:end_ms]
    trimmed_audio.export(output_file, format="mp4")

    print(f"✅ 裁切完成")
    print(f"Start: {start_ms} ms")
    print(f"End  : {end_ms} ms")

if __name__ == "__main__":
    trim_audio_by_db(
        input_file="input.m4a",
        output_file="output_trimmed.m4a",
        threshold_db=-20.0,
        frame_ms=10
    )
