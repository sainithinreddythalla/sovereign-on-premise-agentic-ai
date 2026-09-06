from typing import List, Optional
from .api_models import SearchResult
from .vector_store import get_vector_store

def search_vector_store(query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> List[SearchResult]:
    """
    Searches the vector store and formats the response as SearchResult objects.
    """
    if not query.strip():
        return []
        
    vector_store = get_vector_store()
    raw_results = vector_store.search(query, document_ids, top_k)
    
    search_results = []
    
    if raw_results and raw_results["documents"] and len(raw_results["documents"]) > 0:
        # ChromaDB returns a list of lists for queries
        documents = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0] if raw_results["distances"] else [0.0] * len(documents)
        
        for doc, meta, distance in zip(documents, metadatas, distances):
            # We configured ChromaDB with cosine distance. 
            # Cosine similarity = 1 - cosine distance
            score = 1.0 - distance
            
            result = SearchResult(
                document_id=meta.get("document_id", "unknown"),
                filename=meta.get("filename", "unknown"),
                page=meta.get("page"),
                text=doc,
                score=score
            )
            search_results.append(result)
            
    return search_results
