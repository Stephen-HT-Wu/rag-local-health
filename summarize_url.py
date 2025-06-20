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
    prompt = f"請針對以下文章內容，為一位「{persona}」產出摘要，控制在 300 字內：\n{text[:3000]}"
    print(f"\n{prompt}\n")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
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
    
    # 生成前10篇摘要
    first_ten_links = links[:10]
    print(f"🔍 正在為 {len(first_ten_links)} 篇文章生成摘要")
    
    summaries = []
    for idx, link in enumerate(first_ten_links, 1):
        text = get_article_text(link)
        summary = generate_summary(text, persona)
        print(f"處理 {link} ...")
        print(f"摘要：{summary}")
        summaries.append({"url": link, "summary": summary})
        # 直接在這裡寫入摘要檔案
        filename = f"summaries/summary_{persona}_{idx}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"URL: {link}\n摘要: {summary}\n")
    return summaries





if __name__ == "__main__":
    url = "https://supertaste.tvbs.com.tw/asia/"
    print(f"🔍 正在處理網站：{url}")
    persona_list = ["一般用戶", "年輕女性", "年輕男性", "中年女性", "中年男性", "高齡女性", "高齡男性"]
    for persona in persona_list:
        print(f"🔍 正在為 {persona} 生成摘要...")
        results = summarize_index(url, persona=persona)
    print("✅ 摘要生成完成！")
  
  