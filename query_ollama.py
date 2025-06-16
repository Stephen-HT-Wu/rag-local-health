import sys
from langchain.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

import time


load_dotenv()

# Get model name from command line argument, default to "yi"
model_name = sys.argv[1] if len(sys.argv) > 1 else "yi"
query = sys.argv[2] if len(sys.argv) > 2 else "請問抗三高的原則？"

print(f"\n 🔍 Using model: {model_name}")
print(f"\n 🔍 Query: {query}")

#embedding = OpenAIEmbeddings()  # Or HuggingFaceEmbeddings for local
embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

db = Chroma(persist_directory="./bge-m3_mydb", embedding_function=embedding)
retriever = db.as_retriever(search_kwargs={"k": 3})

# Use Ollama as the LLM
llm = Ollama(model=model_name)  # You can change to any model you have pulled with Ollama

qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

#query = "請問抗三高的原則？"
start = time.time()
result = qa.run(query)
print(f"⏱️ 回答用時：{round(time.time() - start, 2)} 秒")

relevant_docs = retriever.get_relevant_documents(query)
print("\n📄 檢索到的段落：")
for i, doc in enumerate(relevant_docs, 1):
    print(f"\n--- Chunk {i} ---\n{doc.page_content}\n")

print("\n🔍 查詢結果：")
print(result)
