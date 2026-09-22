import chromadb
from typing import List, Dict, Any, Optional
from chromadb.config import Settings
from .config import VECTOR_DB_DIR
from .embeddings import get_embedding_service

class VectorStore:
    def __init__(self):
        # Initialize local persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_service = get_embedding_service()

    def delete_document(self, document_id: str):
        """
        Delete all chunks for a given document_id to prevent duplicates.
        """
        self.collection.delete(where={"document_id": document_id})

    def add_chunks(self, document_id: str, chunks: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Embed and add chunks to the vector database.
        """
        embeddings = self.embedding_service.generate_embeddings(chunks)
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5):
        """
        Search for relevant chunks.
        """
        query_embedding = self.embedding_service.generate_embedding(query)
        
        where_clause = None
        if document_ids:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}
                
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )
        return results

# Singleton instance
vector_store = VectorStore()

def get_vector_store() -> VectorStore:
    return vector_store
