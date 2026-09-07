from typing import List
from .api_models import RAGSearchRequest, RAGSearchResponse, DocumentProcessResponse
from .document_processor import process_and_store_document
from .retriever import search_vector_store

def process_document(file_path: str, document_id: str, filename: str) -> DocumentProcessResponse:
    """
    Process a document (PDF, Image, etc), extract text, chunk it, and store in vector DB.
    """
    return process_and_store_document(file_path, document_id, filename)

def perform_rag_search(request: RAGSearchRequest) -> RAGSearchResponse:
    """
    Search the vector DB based on the query and filtered by document_ids.
    """
    results = search_vector_store(request.query, request.document_ids, request.top_k)
    return RAGSearchResponse(results=results)
