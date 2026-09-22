import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Optional, List
from pydantic import BaseModel

# Mock heavy ML dependencies to allow tests to run without GPU/ChromaDB
sys.modules['fitz'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

from rag.src.service import search, BackendSearchRequest
from rag.src.api_models import RAGSearchResponse, SearchResult

class MockBackendRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    top_k: int = 5

class TestServiceBoundary(unittest.TestCase):
    
    @patch('rag.src.service.perform_rag_search')
    def test_search_normalizes_null_document_ids(self, mock_perform):
        # Setup mock response
        mock_response = RAGSearchResponse(results=[])
        mock_perform.return_value = mock_response
        
        # Request with null document_ids
        req = MockBackendRequest(query="test query", document_ids=None, top_k=3)
        res = search(req)
        
        # Verify call to the internal interface
        mock_perform.assert_called_once()
        called_req = mock_perform.call_args[0][0]
        
        # Verify query, normalized ids, and top_k
        self.assertEqual(called_req.query, "test query")
        self.assertEqual(called_req.document_ids, [])
        self.assertEqual(called_req.top_k, 3)
        
        # Verify response is unchanged
        self.assertEqual(res, mock_response)

    @patch('rag.src.service.perform_rag_search')
    def test_search_passes_provided_document_ids(self, mock_perform):
        mock_perform.return_value = RAGSearchResponse(results=[])
        
        req = MockBackendRequest(query="another query", document_ids=["doc1", "doc2"], top_k=10)
        search(req)
        
        called_req = mock_perform.call_args[0][0]
        self.assertEqual(called_req.query, "another query")
        self.assertEqual(called_req.document_ids, ["doc1", "doc2"])
        self.assertEqual(called_req.top_k, 10)


    @patch('rag.src.retriever.search_vector_store')
    def test_search_service_boundary_validation(self, mock_search):
        mock_search.return_value = []
        req = MockBackendRequest(query="backend validation test")
        res = search(req)
        self.assertIsInstance(res, RAGSearchResponse)
        self.assertEqual(len(res.results), 0)
        try:
            validated = RAGSearchResponse.model_validate(res)
            self.assertIsInstance(validated, RAGSearchResponse)
        except Exception as e:
            self.fail(f"Double-validation type mismatch occurred: {e}")

if __name__ == '__main__':
    unittest.main()
