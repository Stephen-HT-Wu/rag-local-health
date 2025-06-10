from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
# query.py
# 載入環境變數，# .env 檔案中應包含 OPENAI_API_KEY
from dotenv import load_dotenv
load_dotenv() 
# 載入向量資料庫
embedding = OpenAIEmbeddings()
# 使用 Chroma 作為向量資料庫
db = Chroma(persist_directory="./mydb", embedding_function=embedding)
# 構建檢索器
retriever = db.as_retriever(search_kwargs={"k": 3})
# 查詢向量資料庫
llm = OpenAI(temperature=0)
# 使用 LangChain 的 RetrievalQA 來處理查詢
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
# 查詢示例
query = "請問抗三高的原則？"
# 執行查詢
result = qa.run(query)
# 輸出檢索到的段落和查詢結果
relevant_docs = retriever.get_relevant_documents(query)
print("\n📄 檢索到的段落：")
for i, doc in enumerate(relevant_docs, 1):
    print(f"\n--- Chunk {i} ---\n{doc.page_content}\n")
     
print("\n🔍 查詢結果：")
print(result)
