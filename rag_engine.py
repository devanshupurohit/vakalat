import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import os
from typing import List, Dict
import fitz  # PyMuPDF

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vakalat.log"),
        logging.StreamHandler()
    ]
)

class RAGEngine:
    def __init__(self, ipc_pdf_path: str = "./data/ipc_book.pdf", persist_directory: str = "./tfidf_db"):
        self.persist_directory = persist_directory
        self.ipc_pdf_path = ipc_pdf_path
        
        # Initialize TF-IDF vectorizer
        logging.info("Initializing TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize storage paths
        self.vectorizer_path = os.path.join(persist_directory, "vectorizer.pkl")
        self.metadata_path = os.path.join(persist_directory, "metadata.pkl")
        
        # Load or create vectorizer and storage
        if os.path.exists(self.vectorizer_path) and os.path.exists(self.metadata_path):
            self._load_index()
            logging.info(f"Loaded existing TF-IDF index from {persist_directory}")
        else:
            self._create_index()
            self._load_ipc_book()
            logging.info(f"Created new TF-IDF index with IPC book")
    
    def _create_index(self):
        self.documents = []  # List of document texts
        self.metadatas = []  # List of metadata dictionaries
        self.tfidf_matrix = None  # TF-IDF matrix
    
    def _save_index(self):
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadatas': self.metadatas,
                'tfidf_matrix': self.tfidf_matrix
            }, f)
        
        logging.info(f"Saved TF-IDF index to {self.vectorizer_path}")
    
    def _load_index(self):
        with open(self.vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        with open(self.metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadatas = data['metadatas']
            self.tfidf_matrix = data['tfidf_matrix']
        
        logging.info(f"Loaded TF-IDF index with {len(self.documents)} documents")
    
    def _load_ipc_book(self):
        try:
            if not os.path.exists(self.ipc_pdf_path):
                logging.error(f"IPC book not found at {self.ipc_pdf_path}")
                return
            
            logging.info(f"Loading IPC book from {self.ipc_pdf_path}")
            text = self.extract_text_from_pdf(self.ipc_pdf_path)
            
            if not text:
                logging.error("Failed to extract text from IPC book")
                return
            
            # Chunk the text
            chunks = self.chunk_text(text)
            logging.info(f"Chunked IPC book into {len(chunks)} chunks")
            
            # Add chunks to documents
            for i, chunk in enumerate(chunks):
                self.documents.append(chunk)
                self.metadatas.append({
                    "source": self.ipc_pdf_path,
                    "chunk_index": str(i),
                    "total_chunks": str(len(chunks))
                })
            
            # Build TF-IDF matrix
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            
            # Save to disk
            self._save_index()
            
            logging.info(f"Successfully indexed IPC book with {len(chunks)} chunks")
            
        except Exception as e:
            logging.error(f"Error loading IPC book: {e}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def retrieve_relevant_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        try:
            if not self.documents or self.tfidf_matrix is None:
                logging.warning("No documents in index")
                return []
            
            # Transform query to TF-IDF
            query_tfidf = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_tfidf, self.tfidf_matrix).flatten()
            
            # Get top n results
            top_indices = similarities.argsort()[-n_results:][::-1]
            
            # Format results
            retrieved_docs = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include relevant documents
                    doc = self.documents[idx]
                    metadata = self.metadatas[idx]
                    
                    retrieved_docs.append({
                        'content': doc,
                        'metadata': metadata,
                        'distance': 1 - similarities[idx]  # Convert similarity to distance
                    })
            
            logging.info(f"Retrieved {len(retrieved_docs)} IPC sections for query: {query[:50]}...")
            return retrieved_docs
            
        except Exception as e:
            logging.error(f"Error retrieving documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        try:
            return {
                'document_count': len(self.documents),
                'collection_name': 'IPC Legal Knowledge Base',
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logging.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}


# Initialize global RAG engine instance
rag_engine = None

def get_rag_engine() -> RAGEngine:
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine
