pip install -r requirements.txt

# Audio Trim Tool (m4a)

自動裁切 `.m4a` 錄音檔，移除**開頭與結尾音量低於指定 dB（預設 -4 dB）**的區段。  
適合用於 Podcast、語音資料前處理、AI 訓練資料清洗。

---

## 功能特色
- ✅ 自動偵測有效音量區段
- ✅ 移除開頭與結尾低音量（靜音）錄音
- ✅ 支援 `.m4a`
- ✅ 可調整 dB 門檻與精度
- ✅ Windows 環境可用

---

## 環境需求
- Python 3.8 以上
- Windows 10 / 11
- ffmpeg（必須）

---

## 專案結構
```text
audio_trim/
│── trim_m4a.py
│── requirements.txt
│── README.md
│── input.m4a
│── output_trimmed.m4a
