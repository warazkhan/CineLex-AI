import sys
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
from config.data_config import VECTOR_STORE_PATH
from utils.llm_utils import generate

# ------------------------------
# Load FAISS vector store
# ------------------------------
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local(str(VECTOR_STORE_PATH), embeddings=embedding_model, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever()

print("RAG Agent ready! Type 'exit' to quit.\n")

def clean_doc_text(text: str) -> str:
    lines = text.split(", ")
    seen = set()
    clean_lines = []
    for line in lines:
        if line not in seen:
            clean_lines.append(line)
            seen.add(line)
    return ", ".join(clean_lines)

while True:
    query = input("Enter your question: ").strip()
    if query.lower() in {"exit", "quit"}:
        break

    # Retrieve top 5 relevant documents
    docs = retriever.get_relevant_documents(query)[:5]

    # Deduplicate by title and clean text
    context_list = []
    seen_titles = set()
    for doc in docs:
        title = doc.metadata.get("title", None)
        if title and title not in seen_titles:
            cleaned_text = clean_doc_text(doc.page_content)
            context_list.append(cleaned_text)
            seen_titles.add(title)

    context = "\n".join(context_list)

    prompt = f"""
Answer the question using ONLY the facts below.
List each movie exactly once.
Write a single concise sentence per movie.
Do not repeat movies or invent information.

Facts:
{context}

Question: {query}
"""

    answer = generate(prompt, max_new_tokens=200)
    print(f"\nAnswer: {answer}\n")
