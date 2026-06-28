import sys
import logging
from rag_engine import get_rag_engine, initialize_sample_knowledge_base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def test_rag_engine():
    """Test the RAG engine initialization and retrieval."""
    print("=" * 60)
    print("Testing RAG Engine for VAKALAT Legal Assistant")
    print("=" * 60)
    
    try:
        # Initialize RAG engine
        print("\n1. Initializing RAG Engine...")
        rag_engine = get_rag_engine()
        print("✓ RAG Engine initialized successfully")
        
        # Initialize sample knowledge base
        print("\n2. Initializing Sample Knowledge Base...")
        initialize_sample_knowledge_base()
        print("✓ Sample knowledge base initialized")
        
        # Get collection statistics
        print("\n3. Getting Collection Statistics...")
        stats = rag_engine.get_collection_stats()
        print(f"✓ Collection Stats:")
        print(f"  - Document Count: {stats.get('document_count', 0)}")
        print(f"  - Collection Name: {stats.get('collection_name', 'N/A')}")
        print(f"  - Storage: {stats.get('persist_directory', 'N/A')}")
        
        # Test retrieval with different queries
        test_queries = [
            ("Can my landlord evict me without notice?", "Tenant"),
            ("What are my rights under consumer protection?", "Consumer"),
            ("How do I file for divorce?", "Family"),
            ("What is cybercrime punishment?", "Cyber")
        ]
        
        print("\n4. Testing Document Retrieval...")
        for query, category in test_queries:
            print(f"\n  Query: {query}")
            print(f"  Category: {category}")
            results = rag_engine.retrieve_relevant_documents(query, n_results=2, category_filter=category)
            print(f"  ✓ Retrieved {len(results)} documents")
            for i, doc in enumerate(results):
                print(f"    Document {i+1}: {doc['content'][:100]}...")
                print(f"    Source: {doc['metadata'].get('source', 'Unknown')}")
                print(f"    Distance: {doc['distance']:.4f}")
        
        # Test without category filter
        print("\n5. Testing Retrieval without Category Filter...")
        general_query = "What are legal rights in India?"
        results = rag_engine.retrieve_relevant_documents(general_query, n_results=3)
        print(f"✓ Retrieved {len(results)} documents for general query")
        
        print("\n" + "=" * 60)
        print("✓ All RAG Engine Tests Passed Successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_legal_analysis_integration():
    """Test integration with legal analysis module."""
    print("\n" + "=" * 60)
    print("Testing Legal Analysis Integration with RAG")
    print("=" * 60)
    
    try:
        from brain_of_the_lawyer import analyze_legal_query_with_images
        
        print("\n1. Testing Legal Query Analysis with RAG context...")
        query = "Can my landlord evict me without notice?"
        category = "Tenant"
        
        response = analyze_legal_query_with_images(
            category=category,
            query=query,
            image_paths=[],
            document_paths=[],
            chat_history=[]
        )
        
        print(f"✓ Legal analysis completed")
        print(f"\nQuery: {query}")
        print(f"Response: {response[:300]}...")
        
        print("\n" + "=" * 60)
        print("✓ Legal Analysis Integration Test Passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Integration Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting RAG Integration Tests...\n")
    
    # Test RAG engine
    rag_test_passed = test_rag_engine()
    
    # Test legal analysis integration
    integration_test_passed = test_legal_analysis_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"RAG Engine Test: {'✓ PASSED' if rag_test_passed else '✗ FAILED'}")
    print(f"Integration Test: {'✓ PASSED' if integration_test_passed else '✗ FAILED'}")
    
    if rag_test_passed and integration_test_passed:
        print("\n✓ All tests passed! RAG integration is working correctly.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        sys.exit(1)
