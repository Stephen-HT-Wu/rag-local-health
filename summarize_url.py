import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from urllib.parse import urljoin
from gtts import gTTS
from dotenv import load_dotenv
import os
load_dotenv()

summary_words = 300  # 摘要字數限制   
article_limit = 5  # 每次處理的文章數量限制

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

def generate_article_summary(text):
    prompt = f"請針對以下文章內容，寫出容易理解、掌握重點、採取行動的摘要，控制在 {summary_words}字內：\n{text[:3000]}"
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_persona_summary(text, persona):
    # 針對不同角色生成摘要
    prompt = f"請針對以下文章內容，整理出吸引{persona}閱讀的文章。避免提到年齡、角色。並且保留適當的 link\n{text[:3000]}"
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_dialog(text):
    # 生成 podcast 風格的對話稿
    prompt = f"請將以下文章內容轉換成適合tts的文字檔。有男女兩個主持人，男的叫小食，性格風趣幽默。女的叫小尚，性格可愛俏皮。不要有超連結\n{text[:3000]}"

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def summarize_index(url):

    all_links = get_links_from_page(url)
    
    if not all_links:
        print("🔴 沒有找到任何文章連結，請檢查網址或網頁結構。")
        return []       
    
    # 如果文章數量少於 article_limit，則處理全部文章
    # 否則只處理前 article_limit 篇文章 
    limited_links = []
    if len(all_links) < article_limit:
        limited_links = all_links
        print(f"🔍 文章數量少於 {article_limit} 篇，將處理全部 {len(all_links)} 篇文章")
    else:
        limited_links = all_links[:article_limit]
        print(f"🔍 文章數量超過 {article_limit} 篇，將處理前 {article_limit} 篇文章")
    
    print(f"🔍 正在為 {len(limited_links)} 篇文章生成摘要")
    if not os.path.exists("summaries"):
        os.makedirs("summaries")    
    print("✅ 已建立 summaries 資料夾") 
    summaries = []
    for idx, link in enumerate(limited_links, 1):
        text = get_article_text(link)
        summary = generate_article_summary(text)
        print(f"處理 {link} ...")
        print(f"摘要：{summary}")
        # 將摘要以 append 模式寫入同一個檔案
        filename = f"summaries/summary_{idx}.txt"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"URL: {link}\n摘要: {summary}\n\n")
        summaries.append({"url": link, "summary": summary})
    return summaries


def generate_whole_summary(summaries):
    if not summaries:
        return "沒有可用的摘要。"
    
    # 將所有摘要及連結合併成一個大文本
    combined_text = "\n\n".join([f"URL: {summary['url']}\n摘要: {summary['summary']}" for summary in summaries])
    
    prompt = f"請針對以下內容 '{combined_text[:3000]}' 寫出一個整體的總結，並在文章中插入適當的連結\n"

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    overall_summary=response.choices[0].message.content
    print(f"整體摘要：{overall_summary}")
    # 將整體摘要寫入檔案
    if not os.path.exists("summaries"):
        os.makedirs("summaries")
        print("✅ 已建立 summaries 資料夾")
    if overall_summary:
        summary = overall_summary.strip()
        print(f"🔍 正在寫入整體摘要到檔案..."   )
    filename = f"summaries/overall_summary.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{summary}\n")
    print(f"✅ 已將整體摘要寫入 {filename}")
    
    return overall_summary


if __name__ == "__main__":
    url = "https://supertaste.tvbs.com.tw/asia/"
    print(f"🔍 正在處理網站：{url}")
    # 生成各篇文章的摘要
    summaries = summarize_index(url)
    # 生成整體的摘要
    print("🔍 正在生成整體摘要...")
    overall_summary = generate_whole_summary(summaries)
    print(f"整體摘要：{overall_summary}")  

    # transplate summaries to different personas
    # persona_list = ["一般用戶", "年輕女性", "年輕男性", "中年女性", "中年男性", "高齡女性", "高齡男性"]
    # persona_list = [ "年輕女性", "年輕男性", "高齡女性", "高齡男性"]
    persona_list = [ "喜愛冒險的年輕女大學生", "喜愛冒險的年輕男大學生", "和閨蜜一起出遊的成熟女性", "帶小孩出國的成熟男性"]

    for persona in persona_list:
        print(f"🔊 正在為 {persona} 生成個人化摘要...")
        persona_summary = generate_persona_summary(overall_summary, persona)
        # 儲存個人化摘要到檔案
        filename = f"summaries/persona_summary_{persona}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"角色: {persona}\n摘要: {persona_summary}\n")
        print(f"✅ 已將 {persona} 的摘要儲存到 {filename}")
    print("✅ 摘要生成完成！")

    # 生成 podcast 風格，對話稿
    dialog = generate_dialog(overall_summary)
    # 儲存對話稿為文字檔
    dialog_filename = "dialog/dialog.txt"
    with open(dialog_filename, "w", encoding="utf-8") as f:
        f.write(dialog)
    print(f"✅ 已將對話稿儲存為 {dialog_filename}")


  
  