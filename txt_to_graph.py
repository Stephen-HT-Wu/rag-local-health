import openai
import requests
from dotenv import load_dotenv
import sys # 用於從命令行獲取輸入
import re # 用於簡化檔名

load_dotenv()

# Get prompt from command line argument, or use default if not provided
prompt = sys.argv[1] if len(sys.argv) > 1 else "一隻穿著太空裝的貓咪正在月球上漫步"


# For openai>=1.0.0
response = openai.images.generate(
    model="dall-e-3",  # or "dall-e-2"
    prompt=prompt,
    n=1,
    size="1024x1024"
)

image_url = response.data[0].url
print("圖片連結:", image_url)

img_data = requests.get(image_url).content

# 以 prompt 生成簡化檔名（移除特殊字元，取前10字）
def simplify_filename(text):
    text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)  # 僅保留中英文與數字
    text = '-'.join(text.split())  # 以 "-" 連接詞
    return text[:30] if len(text) > 30 else text  # 可依需求調整長度

filename = f"{simplify_filename(prompt)}.png"

# 儲存圖片
with open(filename, 'wb') as f:
    f.write(img_data)
print(f"圖片已儲存為 {filename}")
