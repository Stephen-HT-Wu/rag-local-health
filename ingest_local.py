# 讀取文件（先放一個 txt 文件在同目錄，如: mydoc.txt）# ...existing code...
import glob
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma


from dotenv import load_dotenv
load_dotenv() 
# 載入環境變數 # .env 檔案中應包含 OPENAI_API_KEY
# 讀取多個 txt 文件
file_paths = glob.glob("./text/*.txt")
documents = []
for file_path in file_paths:
    loader = TextLoader(file_path, encoding="utf-8")
    documents.extend(loader.load())

# 分段處理
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = splitter.split_documents(documents)

# 向量化文件並儲存
# embedding = OpenAIEmbeddings()  # 需要 OpenAI API Key 環境變數
embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

vectorstore = Chroma.from_documents(docs, embedding, persist_directory="./bge-m3_mydb")
vectorstore.persist()

print("✅ 向量資料庫建立完成！")