#from openai import OpenAI
from google.cloud import texttospeech
import os
import re
import ffmpeg
import os
from dotenv import load_dotenv
load_dotenv()

client = client = texttospeech.TextToSpeechClient()

# 設定要查詢的語言代碼為台灣華語
language_code = "zh-TW" # 或者 "cmn-TW"

response = client.list_voices(language_code=language_code)

# print(f"所有支援 {language_code} 的語音：")
# print("---")
# for voice in response.voices:
#     print(f"Name: {voice.name}")
#     print(f"  Gender: {texttospeech.SsmlVoiceGender(voice.ssml_gender).name}")
#     print(f"  Natural Sample Rate (Hz): {voice.natural_sample_rate_hertz}")
#     print(f"  Supported Languages: {voice.language_codes}")
#     print("---")

 
#read dialogue from a file dialog/dialog.txt
# or define it directly in the code
dialogue = []
with open("dialog/dialog.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        # 只根據角色名（小尚/小食）分割，不依標點
        match = re.match(r"^(小尚|小食)[：:](.+)$", line)
        if match:
            speaker = match.group(1)
            text = match.group(2).strip()
            if text:
                dialogue.append((speaker, text))
#print the dialogue to check
for i, (speaker, text) in enumerate(dialogue):
    print(f"Line {i+1}: {speaker} - {text}")    
# 定義角色對應的語音模型

# 角色對應 Google Cloud TTS voice name
voice_map = {
    "小尚": "cmn-TW-Wavenet-A",  # 女聲
    "小食": "cmn-TW-Wavenet-B"   # 男聲
}

os.makedirs("audio_parts", exist_ok=True)
audio_files = []

for i, (speaker, text) in enumerate(dialogue):
    voice_name = voice_map[speaker]
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="zh-TW",
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    filename = f"audio_parts/line_{i+1}_{speaker}.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    audio_files.append(filename)

print("已完成語音生成")
audio_files = sorted([f for f in os.listdir("audio_parts") if f.endswith(".mp3")])
with open("audio_parts/filelist.txt", "w", encoding="utf-8") as f:
    for filename in audio_files:
        f.write(f"file '{filename}'\n")

# 呼叫 ffmpeg 合併
os.system("ffmpeg -f concat -safe 0 -i audio_parts/filelist.txt -c copy merged_dialogue.mp3")
print("所有語音檔已合併至 merged_dialogue.mp3")


