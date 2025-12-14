from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from rag.retriever import get_retriever
from rag.prompt import RAG_PROMPT

def build_rag_chain(embedding_client):
    """
    Builds and returns the LangChain RAG pipeline:
    Retriever → Prompt → LLM → Output parser
    """

    retriever = get_retriever(embedding_client)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain
