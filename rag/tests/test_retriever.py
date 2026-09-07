import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock ML dependencies
sys.modules['fitz'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

from rag.src.retriever import search_vector_store
from rag.src.api_models import SearchResult, RAGSearchRequest

class TestRetrieverMetadata(unittest.TestCase):
    @patch('rag.src.retriever.get_vector_store')
    def test_search_vector_store_preserves_metadata(self, mock_get_store):
        mock_store = MagicMock()
        mock_get_store.return_value = mock_store
        
        # Mock realistic vector-store output
        mock_store.search.return_value = {
            "documents": [["Safety requirement text", "Another text"]],
            "metadatas": [[
                {
                    "document_id": "doc_001",
                    "filename": "Safety_Manual.pdf",
                    "page": 12
                },
                {
                    "document_id": "doc_002",
                    "filename": "Other_Manual.pdf",
                    "page": 15
                }
            ]],
            "distances": [[0.1, 0.2]]
        }
        
        results = search_vector_store("safety", document_ids=["doc_001", "doc_002"], top_k=5)
        
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], SearchResult)
        
        # Verify metadata exactly matches
        self.assertEqual(results[0].document_id, "doc_001")
        self.assertEqual(results[0].filename, "Safety_Manual.pdf")
        self.assertEqual(results[0].page, 12)
        self.assertEqual(results[0].text, "Safety requirement text")
        self.assertAlmostEqual(results[0].score, 0.9)
        
        self.assertEqual(results[1].document_id, "doc_002")
        self.assertEqual(results[1].filename, "Other_Manual.pdf")
        self.assertEqual(results[1].page, 15)
        self.assertEqual(results[1].text, "Another text")
        self.assertAlmostEqual(results[1].score, 0.8)
        
        # Verify document filtering and top_k are passed correctly
        mock_store.search.assert_called_once_with("safety", ["doc_001", "doc_002"], 5)
        
    @patch('rag.src.retriever.get_vector_store')
    def test_search_vector_store_empty(self, mock_get_store):
        mock_store = MagicMock()
        mock_get_store.return_value = mock_store
        
        # Test empty string query
        results_empty_query = search_vector_store("   ")
        self.assertEqual(results_empty_query, [])
        self.assertEqual(mock_store.search.call_count, 0)
        
        # Test empty vector store response
        mock_store.search.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        results_empty_db = search_vector_store("missing", document_ids=None, top_k=5)
        self.assertEqual(results_empty_db, [])

    @patch('rag.src.interfaces.search_vector_store')
    def test_perform_rag_search_empty(self, mock_search):
        from rag.src.interfaces import perform_rag_search
        from rag.src.api_models import RAGSearchRequest
        
        mock_search.return_value = []
        req = RAGSearchRequest(query="empty", document_ids=[], top_k=5)
        res = perform_rag_search(req)
        
        self.assertEqual(res.results, [])

if __name__ == '__main__':
    unittest.main()
