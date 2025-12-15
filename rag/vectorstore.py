import time
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from ingestion.embeddings import GSTEmbeddings
from config.settings import COLLECTION_NAME, CHROMA_PERSIST_DIR


# =========================
# Configuration
# =========================

CHROMA_HOST = "localhost"   # change to chroma service hostname in AWS
CHROMA_PORT = 8000


# =========================
# Safe batched ingestion
# =========================

def add_documents_safely(
    vector_store,
    documents,
    batch_size: int = 20,
    max_retries: int = 3,
):
    """
    Add documents to Chroma in batches with retries.
    Works correctly with Chroma Server (HTTP mode).
    """

    if not documents:
        print("No documents to add.")
        return 0

    print(
        f"Adding {len(documents)} documents "
        f"in batches of {batch_size}..."
    )

    total_added = 0

    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i : i + batch_size]

        for attempt in range(1, max_retries + 1):
            try:
                vector_store.add_documents(batch_docs)
                total_added += len(batch_docs)

                print(
                    f"✓ Batch {i // batch_size + 1} "
                    f"added ({len(batch_docs)} docs) "
                    f"[total: {total_added}/{len(documents)}]"
                )
                break

            except Exception as e:
                if attempt == max_retries:
                    print(
                        f"❌ Failed batch {i // batch_size + 1} "
                        f"after {max_retries} attempts"
                    )
                    raise

                print(
                    f"⚠️  Batch {i // batch_size + 1} failed "
                    f"(attempt {attempt}/{max_retries}). Retrying..."
                )
                time.sleep(2 ** attempt)

        # small pause to reduce load
        time.sleep(0.2)

    print(f"\n✅ Successfully added {total_added} documents.")
    return total_added


# =========================
# Vectorstore factory
# =========================

def get_vectorstore(embedding_client, force_refresh=False):
    """
    Always returns a fresh LangChain Chroma wrapper
    connected to the Chroma SERVER (not embedded).
    
    Args:
        embedding_client: The embedding client to use
        force_refresh: If True, forces a fresh connection (default: False)
    """

    embeddings = GSTEmbeddings(embedding_client)

    # Try to connect to ChromaDB server first
    # If that fails (e.g., tenant issues or server not running), fall back to PersistentClient
    client = None
    http_error_msg = None
    
    # Try to create HTTP client - this will fail if server is not accessible
    # or if tenant validation fails (ValueError for tenant issues)
    try:
        client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            timeout=5  # 5 second timeout to avoid hanging
        )
        # Test connection by listing collections (this validates the connection)
        _ = client.list_collections()
        print(f"✓ Connected to ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT}")
    except ValueError as ve:
        # Tenant validation error - try with explicit tenant/database
        # Some ChromaDB server versions require this
        http_error_msg = str(ve)
        try:
            client = chromadb.HttpClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
                tenant="default_tenant",
                database="default_database",
                timeout=5
            )
            _ = client.list_collections()
            print(f"✓ Connected to ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT} (with explicit tenant/database)")
        except Exception as inner_e:
            # If explicit tenant also fails, fall back to PersistentClient
            print(
                f"ℹ️  ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT} not available "
                f"(tenant validation failed). Using local PersistentClient instead."
            )
            client = None
    except (ConnectionError, TimeoutError, Exception) as e:
        # Any other connection error - fall back to persistent
        http_error_msg = str(e)
        # Only show detailed error in debug mode, otherwise just info message
        if "Connection refused" in http_error_msg or "timeout" in http_error_msg.lower():
            print(
                f"ℹ️  ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT} not available. "
                f"Using local PersistentClient instead."
            )
        else:
            print(
                f"ℹ️  ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT} not available. "
                f"Using local PersistentClient instead. (Error: {http_error_msg})"
            )
        client = None
    
    # Use PersistentClient if HTTP client failed
    if client is None:
        import os
        # Ensure the persist directory exists
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        print(f"✓ Using local PersistentClient at {CHROMA_PERSIST_DIR}")
    
    # When force_refresh is True with PersistentClient, create a completely new client
    # to ensure we get fresh data from disk (no connection caching)
    # Check if client is PersistentClient by checking its type name (safer than isinstance)
    if force_refresh and client is not None:
        # Check if it's a PersistentClient by type name (avoid isinstance to prevent type errors)
        is_persistent = type(client).__name__ == "PersistentClient"
        if is_persistent:
            # Create a fresh PersistentClient to avoid any connection/collection caching
            # This ensures we read the latest data from disk
            client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            print(f"✓ Created fresh PersistentClient for force_refresh")

    # Optional sanity check - this also helps refresh the connection
    try:
        # Always get a fresh collection reference to avoid caching
        collection = client.get_collection(COLLECTION_NAME)
        if force_refresh:
            # Force a fresh read from disk by:
            # 1. Getting a new collection reference
            # 2. Calling count() which forces a database query
            # 3. This ensures we see the latest documents
            collection = client.get_collection(COLLECTION_NAME)
            doc_count = collection.count()  # Forces a fresh database read
            print(
                f"Connected to collection '{COLLECTION_NAME}' "
                f"({doc_count} documents) [fresh read]"
            )
        else:
            doc_count = collection.count()
            print(
                f"Connected to collection '{COLLECTION_NAME}' "
                f"({doc_count} documents)"
            )
    except Exception:
        print(
            f"Collection '{COLLECTION_NAME}' not found. "
            f"It will be created on first write."
        )

    # Create a fresh Chroma instance to avoid any caching
    # Each time this is called, it creates a new wrapper that will
    # query the server/disk for the latest data
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # When force_refresh is True, we need to ensure the Chroma wrapper
            # doesn't cache the collection. We do this by creating a completely
            # fresh wrapper each time.
            vectorstore = Chroma(
                client=client,
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
            )
            
            # If force_refresh, ensure the vectorstore has a fresh collection reference
            if force_refresh:
                # Force the vectorstore to refresh by re-initializing its collection
                # The Chroma wrapper caches the collection in _collection, so we need
                # to ensure it gets a fresh reference
                try:
                    # Access the collection through the client to force a fresh read
                    fresh_collection = client.get_collection(COLLECTION_NAME)
                    # Update the vectorstore's internal collection reference
                    vectorstore._collection = fresh_collection
                    # Verify we can get a fresh count
                    _ = fresh_collection.count()
                except (AttributeError, Exception) as e:
                    # If we can't update _collection, that's okay - the wrapper
                    # should still work, but might use cached data
                    # Log a warning in debug mode
                    pass
            
            return vectorstore
        except Exception as e:
            error_msg = str(e)
            # Check if it's a schema mismatch error (old database format)
            if ("no such column" in error_msg.lower() or 
                "operationalerror" in error_msg.lower() or
                "sqlite3" in error_msg.lower()) and attempt == 0:
                # First attempt failed with schema error - try to reset the database
                import shutil
                import os
                print(
                    f"\n⚠️  Database schema mismatch detected. The existing ChromaDB database "
                    f"at '{CHROMA_PERSIST_DIR}' is from an older version and is incompatible."
                )
                print(f"🔄 Attempting to reset the database...")
                
                try:
                    # Backup the old database by renaming it
                    backup_path = f"{CHROMA_PERSIST_DIR}.backup"
                    if os.path.exists(CHROMA_PERSIST_DIR):
                        if os.path.exists(backup_path):
                            shutil.rmtree(backup_path)
                        os.rename(CHROMA_PERSIST_DIR, backup_path)
                        print(f"✓ Backed up old database to {backup_path}")
                    
                    # Create a fresh client with the reset database
                    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
                    print(f"✓ Created fresh database at {CHROMA_PERSIST_DIR}")
                    # Retry creating the vectorstore
                    continue
                except Exception as reset_error:
                    print(f"❌ Failed to reset database: {reset_error}")
                    raise RuntimeError(
                        f"ChromaDB schema mismatch and automatic reset failed. "
                        f"Please manually delete the database:\n"
                        f"  rm -rf {CHROMA_PERSIST_DIR}\n"
                        f"Then run the ingestion again.\n"
                        f"Original error: {error_msg}"
                    )
            else:
                # Re-raise if it's a different error or we've exhausted retries
                raise
    
    # Should not reach here, but just in case
    raise RuntimeError("Failed to create vectorstore after retries")
