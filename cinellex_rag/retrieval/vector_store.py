from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config.data_config import VECTOR_STORE_PATH

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = FAISS.load_local(
    str(VECTOR_STORE_PATH),
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

retriever = vector_store.as_retriever()