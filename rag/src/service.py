from typing import Optional, List, Any
from pydantic import BaseModel
from .api_models import RAGSearchRequest, RAGSearchResponse
from .interfaces import perform_rag_search

class BackendSearchRequest(BaseModel):
    """
    Represents the expected request shape from the backend API.
    """
    query: str
    document_ids: Optional[List[str]] = None
    top_k: int = 5

def search(request: Any) -> RAGSearchResponse:
    """
    Adapter boundary for the backend RAG API.
    Calls the internal RAG implementation without requiring the backend to rewrite it.
    """
    # Extract attributes (supports Pydantic models or generic objects)
    query = getattr(request, 'query', "")
    document_ids = getattr(request, 'document_ids', None)
    top_k = getattr(request, 'top_k', 5)

    # Normalize missing/null document_ids to an empty list
    normalized_ids = document_ids if document_ids is not None else []

    # Construct the existing internal RAG request model
    rag_request = RAGSearchRequest(
        query=query,
        document_ids=normalized_ids,
        top_k=top_k
    )
    
    # Call the existing RAG pipeline
    return perform_rag_search(rag_request)
