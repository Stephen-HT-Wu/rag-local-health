import openai
import requests
from dotenv import load_dotenv
load_dotenv()

prompt = "一隻穿著太空裝的貓咪正在月球上漫步"

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
with open('generated_image.png', 'wb') as f:
    f.write(img_data)
print("圖片已儲存為 generated_image.png")

