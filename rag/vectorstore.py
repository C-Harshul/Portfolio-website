import uuid
from langchain_community.vectorstores import Chroma
from ingestion.embeddings import GSTEmbeddings
from config.settings import CHROMA_PERSIST_DIR, COLLECTION_NAME


# ChromaDB Compaction Error Fix - Alternative approach with batching

def add_documents_safely(vector_store, documents, embeddings=None, batch_size=20):
    """
    Safely add documents to ChromaDB with batching to avoid compaction errors
    """
    import time
    
    print(f"Adding {len(documents)} documents in batches of {batch_size} to avoid compaction errors...")
    
    total_added = 0
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        
        # Use LangChain's add_documents method instead of direct ChromaDB API
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add documents using LangChain's method
                doc_ids = vector_store.add_documents(batch_docs)
                total_added += len(batch_docs)
                print(f"✓ Batch {i//batch_size + 1}: Added {len(batch_docs)} documents. Total: {total_added}/{len(documents)}")
                break
                
            except Exception as e:
                if "compaction" in str(e).lower() or "hnsw" in str(e).lower():
                    print(f"⚠️  Compaction error in batch {i//batch_size + 1}, attempt {attempt + 1}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
                    if attempt == max_retries - 1:
                        print(f"❌ Failed to add batch {i//batch_size + 1} after {max_retries} attempts")
                        print(f"Error: {e}")
                        return total_added
                else:
                    print(f"❌ Unexpected error in batch {i//batch_size + 1}: {e}")
                    return total_added
        
        # Small delay between batches to reduce load
        time.sleep(0.5)
    
    print(f"\n✅ Successfully added {total_added} documents to vector store!")
    return total_added

def get_vectorstore(embedding_client):
    embeddings = GSTEmbeddings(embedding_client)

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
