import os
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from unihelp.core.config import settings
from unihelp.core.logging import setup_logger

logger = setup_logger(__name__)

class VectorStore:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.model_name = settings.EMBEDDING_MODEL_NAME
        
        logger.info(f"Initializing embedding model: {self.model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        
        logger.info(f"Connecting to ChromaDB at {self.persist_dir}")
        self.db = Chroma(
            collection_name="unihelp_docs",
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str] = None):
        """Add text chunks with their associated metadata to the vector store."""
        logger.info(f"Adding {len(texts)} chunks to ChromaDB")
        self.db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        # Note: In newer explicit langchain_chroma, persistence is handled automatically

    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top k chunks representing context for the query."""
        logger.info(f"Searching for: '{query}' (k={k})")
        docs = self.db.similarity_search(query, k=k)
        
        results = []
        for doc in docs:
            results.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        return results

    def get_collection_stats(self):
        return {
            "count": self.db._collection.count()
        }
