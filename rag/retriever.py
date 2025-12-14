from rag.vectorstore import get_vectorstore

def get_retriever(embedding_client, k: int = 4):
    vectordb = get_vectorstore(embedding_client)
    return vectordb.as_retriever(search_kwargs={"k": k})
