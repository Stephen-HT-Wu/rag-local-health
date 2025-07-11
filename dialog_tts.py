#from openai import OpenAI
from google.cloud import texttospeech
import os
import re
import ffmpeg
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', s)]


# client = texttospeech.TextToSpeechClient()
client = OpenAI()


# 設定要查詢的語言代碼為台灣華語
language_code="cmn-CN"
# language_code="en-US"
# response = client.list_voices(language_code=language_code)

# 讀取對話內容
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
# voice_map = {
#     "小尚": "cmn-CN-Chirp3-HD-Leda",  # 女聲
#     "小食": "cmn-CN-Chirp3-HD-Zubenelgenubi"   # 男聲
    # "小尚": "en-US-Studio-O",  # 女聲
    # "小食": "en-US-Studio-Q"   # 男聲   
# }

# 角色對應 OpenAI TTS voice name
voice_map = {
    "小尚": "sage",  # 女聲（可選：alloy, echo, fable, onyx, nova, shimmer）
    "小食": "ballad"    # 男聲
}

instructions = """Personality/affect: a high-energy cheerleader helping with administrative tasks \n\nVoice: Enthusiastic, and bubbly, with an uplifting and motivational quality.\n\nTone: Encouraging and playful, making even simple tasks feel exciting and fun.\n\nDialect: Casual and upbeat, using informal phrasing and pep talk-style expressions.\n\nPronunciation: Crisp and lively, with exaggerated emphasis on positive words to keep the energy high.\n\nFeatures: Uses motivational phrases, cheerful exclamations, and an energetic rhythm to create a sense of excitement and engagement."""


os.makedirs("audio_parts", exist_ok=True)
audio_files = []

for i, (speaker, text) in enumerate(dialogue):
    voice_name = voice_map[speaker]
    # synthesis_input = texttospeech.SynthesisInput(text=text)
    # voice = texttospeech.VoiceSelectionParams(
    #     language_code=language_code,
    #     name=voice_name
    # )
    # audio_config = texttospeech.AudioConfig(
    #     audio_encoding=texttospeech.AudioEncoding.MP3,
    #     speaking_rate=1.15  # 語速
    # )
    # response = client.synthesize_speech(
    #     input=synthesis_input,
    #     voice=voice,
    #     audio_config=audio_config
    # )
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice=voice_name,
        input=text,
        instructions=instructions,
        response_format="mp3",
        # 這裡可以調整語速，1.0 是正常速度，
        # 1.15 是稍快，1.2 是更快
        speed=1.15
    )
    filename = f"audio_parts/line_{i+1}_{speaker}.mp3"
    with open(filename, "wb") as out:
        out.write(response.content)
    audio_files.append(filename)
    print(f"已生成語音檔: {filename}")

print("已完成語音生成")



audio_files = sorted([f for f in os.listdir("audio_parts") if f.endswith(".mp3")])
audio_files = sorted(
    [f for f in os.listdir("audio_parts") if f.endswith(".mp3")],
    key=natural_sort_key
)

with open("audio_parts/filelist.txt", "w", encoding="utf-8") as f:
    for filename in audio_files:
        f.write(f"file '{filename}'\n")

# 呼叫 ffmpeg 合併
os.system("ffmpeg -f concat -safe 0 -i audio_parts/filelist.txt -y -c copy merged_dialogue/merged_dialogue_openAI.mp3")
print("所有語音檔已合併至 merged_dialogue/merged_dialogue.mp3")


