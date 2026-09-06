from sentence_transformers import SentenceTransformer
from typing import List
from .config import EMBEDDING_MODEL_NAME

class EmbeddingService:
    def __init__(self):
        # We load the model locally
        # This will download the model to the local cache if not already present
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single string of text.
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of strings.
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

# Singleton instance
embedding_service = EmbeddingService()

def get_embedding_service() -> EmbeddingService:
    return embedding_service
