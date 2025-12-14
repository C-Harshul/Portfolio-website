from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a GST compliance assistant. "
        "Answer strictly using the provided context."
    ),
    (
        "user",
        "Context:\n{context}\n\nQuestion:\n{question}"
    )
])
