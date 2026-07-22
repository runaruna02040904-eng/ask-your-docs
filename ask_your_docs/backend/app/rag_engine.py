import os
import torch
from transformers import AutoTokenizer, AutoModel
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from typing import TypedDict, List

# ---------- 自定义嵌入（基于本地 transformers 模型）----------
class LocalEmbeddings:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)
        # 获取嵌入维度（从模型配置中读取）
        self.dim = self.model.config.hidden_size

    def _embed(self, texts):
        # 对文本进行 tokenize 并计算 mean pooling
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            # mean pooling
            attention_mask = inputs["attention_mask"]
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
                input_mask_expanded.sum(1), min=1e-9
            )
        return embeddings.numpy()

    def embed_documents(self, texts):
        return self._embed(texts).tolist()

    def embed_query(self, text):
        return self._embed([text]).tolist()[0]

# 实例化嵌入模型（使用我们本地文件夹）
embeddings = LocalEmbeddings(model_path=r"D:\models\all-MiniLM-L6-v2")

# ---------- 大模型：DeepSeek ----------
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL,
    temperature=0,
)

PERSIST_DIR = "./chroma_data"
os.makedirs(PERSIST_DIR, exist_ok=True)

# ---------- 以下所有函数与原代码完全相同 ----------
def add_document_to_vectorstore(text: str, user_id: int, filename: str = "upload"):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    chunks = text_splitter.create_documents([text])
    for chunk in chunks:
        chunk.metadata["source"] = filename

    vectorstore = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    vectorstore.add_documents(chunks)
    return len(chunks)

def retrieve_context(question: str, user_id: int, k: int = 3) -> str:
    vectorstore = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)
    context = "\n\n".join([d.page_content for d in docs])
    return context

class ChatState(TypedDict):
    question: str
    user_id: int
    context: str
    answer: str
    history: List

def retrieve_node(state: ChatState) -> ChatState:
    state["context"] = retrieve_context(state["question"], state["user_id"])
    return state

def generate_node(state: ChatState) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="你是一个基于文档的智能助手。请严格使用以下上下文回答问题。如果上下文无法回答，请说'文档中没有相关信息'。\n上下文：\n{context}"),
        HumanMessage(content="{question}")
    ])
    chain = prompt | llm
    response = chain.invoke({
        "context": state["context"],
        "question": state["question"]
    })
    state["answer"] = response.content
    return state

workflow = StateGraph(ChatState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
chat_graph = workflow.compile()