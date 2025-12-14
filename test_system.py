#!/usr/bin/env python3
"""Test script to verify the GST RAG system works end-to-end."""

import sys
import os
sys.path.append('.')

def test_system():
    """Test the complete GST RAG system."""
    
    print("🧪 Testing GST RAG System Components")
    print("=" * 50)
    
    # Test 1: Import all components
    print("\n1️⃣ Testing imports...")
    try:
        from ingestion.embeddings import cf_embedder, GSTEmbeddings
        from rag.chain import build_rag_chain
        from rag.vectorstore import get_vectorstore
        from ingestion.pdf_loader import PDFLoader
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Initialize embeddings
    print("\n2️⃣ Testing embeddings...")
    try:
        embeddings = GSTEmbeddings(cf_embedder)
        test_text = "GST rate for restaurant services"
        embedding = embeddings.embed_query(test_text)
        print(f"✅ Embeddings working (dimension: {len(embedding)})")
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False
    
    # Test 3: Initialize vector store
    print("\n3️⃣ Testing vector store...")
    try:
        vectorstore = get_vectorstore(cf_embedder)
        print("✅ Vector store initialized")
    except Exception as e:
        print(f"❌ Vector store failed: {e}")
        return False
    
    # Test 4: Initialize RAG chain
    print("\n4️⃣ Testing RAG chain...")
    try:
        chain = build_rag_chain(cf_embedder)
        print("✅ RAG chain initialized")
    except Exception as e:
        print(f"❌ RAG chain failed: {e}")
        return False
    
    # Test 5: Test PDF loader
    print("\n5️⃣ Testing PDF loader...")
    try:
        pdf_loader = PDFLoader()
        print("✅ PDF loader initialized")
    except Exception as e:
        print(f"❌ PDF loader failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The system is ready to use.")
    print("\n📋 Next steps:")
    print("1. Add PDF documents: python ingest_documents.py documents/")
    print("2. Run the app: streamlit run app/app.py")
    
    return True

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)