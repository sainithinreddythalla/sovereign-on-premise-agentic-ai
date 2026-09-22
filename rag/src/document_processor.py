import fitz  # PyMuPDF
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
from .api_models import DocumentProcessResponse
from .config import CHUNK_SIZE, CHUNK_OVERLAP
from .vector_store import get_vector_store

def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text from a PDF file page by page.
    Returns a list of dicts containing text and page number.
    """
    doc = fitz.open(file_path)
    pages_data = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text.strip():
            pages_data.append({
                "text": text,
                "page": page_num + 1
            })
            
    doc.close()
    return pages_data

def chunk_text(pages_data: List[Dict[str, Any]], document_id: str, filename: str) -> tuple[List[str], List[Dict[str, Any]], List[str]]:
    """
    Chunks text using LangChain's RecursiveCharacterTextSplitter.
    Preserves metadata (document_id, filename, page).
    Returns (chunks, metadatas, ids).
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = []
    metadatas = []
    ids = []
    
    for data in pages_data:
        page_chunks = text_splitter.split_text(data["text"])
        for i, chunk in enumerate(page_chunks):
            chunks.append(chunk)
            metadatas.append({
                "document_id": document_id,
                "filename": filename,
                "page": data["page"]
            })
            ids.append(f"{document_id}_p{data['page']}_c{i}")
            
    return chunks, metadatas, ids

def process_and_store_document(file_path: str, document_id: str, filename: str) -> DocumentProcessResponse:
    """
    End-to-end processing of a document: extract, chunk, and store in Vector DB.
    """
    # 1. Extract
    pages_data = extract_text_from_pdf(file_path)
    
    # 2. Chunk
    chunks, metadatas, ids = chunk_text(pages_data, document_id, filename)
    
    # 3. Store in Vector DB
    if chunks:
        vector_store = get_vector_store()
        vector_store.delete_document(document_id)
        vector_store.add_chunks(document_id, chunks, metadatas, ids)
        
    return DocumentProcessResponse(
        document_id=document_id,
        filename=filename,
        status="completed",
        chunks_processed=len(chunks)
    )
