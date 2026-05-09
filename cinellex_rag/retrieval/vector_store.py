from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config.data_config import CHROMA_STORE_PATH

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="cinellex",
    embedding_function=embedding_model,
    persist_directory=str(CHROMA_STORE_PATH)
)

retriever = vector_store.as_retriever()