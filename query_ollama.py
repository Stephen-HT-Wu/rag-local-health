from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings  # Or switch to HuggingFaceEmbeddings if you want local embeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
load_dotenv()

embedding = OpenAIEmbeddings()  # Or HuggingFaceEmbeddings for local
db = Chroma(persist_directory="./mydb", embedding_function=embedding)
retriever = db.as_retriever(search_kwargs={"k": 3})

# Use Ollama as the LLM
llm = Ollama(model="yi")  # You can change to any model you have pulled with Ollama

qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

query = "請問抗三高的原則？"
result = qa.run(query)

relevant_docs = retriever.get_relevant_documents(query)
print("\n📄 檢索到的段落：")
for i, doc in enumerate(relevant_docs, 1):
    print(f"\n--- Chunk {i} ---\n{doc.page_content}\n")

print("\n🔍 查詢結果：")
print(result)