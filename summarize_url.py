import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from urllib.parse import urljoin
from gtts import gTTS
from dotenv import load_dotenv
import os
load_dotenv()

def get_links_from_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")
    
    a_tags = soup.find_all("a", class_="article__item", href=True)
    print(f"共找到 {len(a_tags)} 個文章連結")
    
    links = []
    for a in a_tags:
        href = a['href']
        full_url = urljoin(url, href)  # 把相對路徑補成完整網址
        links.append(full_url)
    
    return links

def get_article_text(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    return soup.get_text()

def generate_summary(text, persona="general"):
    prompt = f"請針對以下文章內容，為一位「{persona}」產出摘要，控制在 100 字內：\n{text[:3000]}"
    # 替換成你自己的 GPT 或 Claude 呼叫
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def summarize_index(url, persona="一般用戶"):
    links = get_links_from_page(url)
    print(f"找到 {len(links)} 個文章連結。")
    if not links:
        return []   
    else:
        print("文章連結：", links)

    # 生成摘要
    print(f"🔍 正在為 {len(links)} 篇文章生成摘要")
    summaries = []
    for idx, link in enumerate(links, 1):
        text = get_article_text(link)
        summary = generate_summary(text, persona)
        print(f"處理 {link} ...")
        print(f"摘要：{summary}")
        summaries.append({"url": link, "summary": summary})
        # 直接在這裡寫入摘要檔案
        filename = f"summaries/summary_{idx}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"URL: {link}\n摘要: {summary}\n")
    return summaries

def convert_summary_to_dialog(text):
    prompt = f"請針對以下文章內容，轉成男女兩個人介紹的對話稿:\n{text[:3000]}"
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
            summaries.append(f"第 {idx} 篇：{summary}")
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
    with open("dialog.txt", "w", encoding="utf-8") as f:
        f.write(dialog)
    print("✅ 已將對話稿儲存為 dialog.txt")

    # gTTS 單次建議不超過 5000 字元
    max_tts_length = 4900
    chunks = [dialog[i:i+max_tts_length] for i in range(0, len(dialog), max_tts_length)]
    for idx, chunk in enumerate(chunks, 1):
        tts = gTTS(chunk, lang='zh-tw')
        tts.save(f"dialog_{idx}.mp3")
    print(f"✅ 語音摘要已生成，共 {len(chunks)} 段。")


# if __name__ == "__main__":
#     url = "https://supertaste.tvbs.com.tw/asia/"
#     print(f"🔍 正在處理網站：{url}")
#     results = summarize_index(url, persona="學生")
#     print("✅ 摘要生成完成！")
  
#     # 生成語音摘要
#     print("🔊 正在生成語音摘要...")     
#     # 生成語音摘要，gTTS 單次建議不超過 5000 字元
#     max_tts_length = 4900
#     all_summaries = "\n\n".join([f"第 {i+1} 篇：{r['summary']}" for i, r in enumerate(results)])
#     # 將 all_summaries 轉成男女兩個人介紹的對話稿
#     print("🔊 將摘要轉成對話稿...")
#     dialog=convert_summary_to_dialog(all_summaries)
#     # 若超過長度則分段產生多個 mp3
#     chunks = [dialog[i:i+max_tts_length] for i in range(0, len(dialog), max_tts_length)]
#     for idx, chunk in enumerate(chunks, 1):
#         tts = gTTS(chunk, lang='zh-tw')
#         tts.save(f"summary_{idx}.mp3")
#     print(f"✅ 語音摘要已生成，共 {len(chunks)} 段。")