"""PDF loading and chunking functionality for GST regulations."""

from pathlib import Path
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import boto3
import tempfile
import os


class PDFLoader:
    """Handles PDF loading and text chunking for GST regulation documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF loader with chunking parameters.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        
    def load_from_file(self, file_path: str) -> List[Document]:
        """
        Load and chunk PDF from local file path.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of chunked documents
        """
        print(f"Loading PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                'source_file': Path(file_path).name,
                'file_type': 'pdf',
                'document_type': 'gst_regulation'
            })
        
        # Split into chunks
        chunked_docs = self.text_splitter.split_documents(documents)
        print(f"Split into {len(chunked_docs)} chunks")
        
        return chunked_docs
        
    def load_from_s3(self, bucket: str, key: str) -> List[Document]:
        """
        Load and chunk PDF from S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            List of chunked documents
        """
        s3_client = boto3.client('s3')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            s3_client.download_fileobj(bucket, key, tmp_file)
            tmp_file.flush()
            
            documents = self.load_from_file(tmp_file.name)
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            # Add S3 metadata to documents
            for doc in documents:
                doc.metadata.update({
                    'source_bucket': bucket,
                    'source_key': key,
                })
                
            return documents
            
    def extract_metadata(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Extract metadata from loaded documents.
        
        Args:
            documents: List of documents
            
        Returns:
            Extracted metadata dictionary
        """
        if not documents:
            return {}
            
        return {
            'total_chunks': len(documents),
            'source': documents[0].metadata.get('source_file', 'unknown'),
            'total_characters': sum(len(doc.page_content) for doc in documents)
        }


# Utility functions for backward compatibility
def process_all_pdfs(pdf_directory: str) -> List[Document]:
    """Load all PDFs found under a directory (recursive), returning LangChain Documents."""
    loader = PDFLoader()
    all_documents = []
    pdf_dir = Path(pdf_directory)
    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process")

    for pdf_file in pdf_files:
        try:
            documents = loader.load_from_file(str(pdf_file))
            all_documents.extend(documents)
            print(f"  ✓ Loaded {pdf_file.name}: {len(documents)} chunks")
        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {e}")

    print(f"\nTotal chunks loaded: {len(all_documents)}")
    return all_documents


def split_documents(documents: List[Document], chunk_size=1000, chunk_overlap=200):
    """Split documents into chunks (for backward compatibility)."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(split_docs)} chunks")
    if split_docs:
        print("Example chunk preview:")
        print(split_docs[0].page_content[:200], "...")
        print(split_docs[0].metadata)
    return split_docs