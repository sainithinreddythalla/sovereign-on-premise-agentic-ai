import unittest

class TestRAGImports(unittest.TestCase):
    def test_imports(self):
        try:
            from rag.src.api_models import SearchResult, RAGSearchRequest, RAGSearchResponse
            from rag.src.config import CHUNK_SIZE
            from rag.src.interfaces import process_document, perform_rag_search
            # We don't import embeddings or vector_store here to avoid requiring the models
            # to be downloaded just for a simple test.
            imported = True
        except ImportError as e:
            imported = False
            print(f"ImportError: {e}")
            
        self.assertTrue(imported)

if __name__ == '__main__':
    unittest.main()
