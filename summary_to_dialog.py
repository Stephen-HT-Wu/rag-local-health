from summarize_url import read_all_summaries_from_folder, convert_summary_to_dialog
from gtts import gTTS
import os
from openai import OpenAI   
from dotenv import load_dotenv
load_dotenv()

def convert_summary_to_dialog(text):
    prompt = f"整合以下文章內容為一個吸引人的介紹:\n{text[:3000]}"
    print(f"\n{prompt}\n")
    # 替換成你自己的 GPT 或 Claude 呼叫
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def read_all_summaries_from_folder(folder="summaries"):
    summaries = []
    files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")])
    for idx, filename in enumerate(files, 1):
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            content = f.read()
            # 只取摘要內容
            summary_line = [line for line in content.splitlines() if line.startswith("摘要:")]
            summary = summary_line[0][3:] if summary_line else content
            summaries.append(f"{summary}")
    return summaries

if __name__ == "__main__":
    # 直接從 summaries 資料夾讀取所有摘要
    print("🔍 從 summaries 資料夾讀取摘要...")
    all_summaries = read_all_summaries_from_folder("summaries")
    all_summaries_str = "\n\n".join(all_summaries)
    print("🔊 將摘要轉成對話稿...")
    # 若要轉成對話稿，可呼叫 convert_summary_to_dialog
    dialog = convert_summary_to_dialog(all_summaries_str)
    # 儲存對話稿為文字檔
    with open("intro.txt", "w", encoding="utf-8") as f:
        f.write(dialog)
    print("✅ 已將對話稿儲存為 intro.txt")

    # gTTS 單次建議不超過 5000 字元
    max_tts_length = 4900
    chunks = [dialog[i:i+max_tts_length] for i in range(0, len(dialog), max_tts_length)]
    for idx, chunk in enumerate(chunks, 1):
        tts = gTTS(chunk, lang='zh-tw')
        tts.save(f"intro_{idx}.mp3")
    print(f"✅ 語音摘要已生成，共 {len(chunks)} 段。")