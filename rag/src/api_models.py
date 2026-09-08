from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class SearchResult(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    text: str
    score: float

class RAGSearchRequest(BaseModel):
    query: str
    document_ids: List[str]
    top_k: int = 5

class RAGSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    results: List[SearchResult]

class DocumentChunk(BaseModel):
    text: str
    metadata: dict

class DocumentProcessResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks_processed: int
