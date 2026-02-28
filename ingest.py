import os
import glob
import json
from unihelp.processor.pipeline import DocumentPipeline
from unihelp.rag.vector_store import VectorStore
from unihelp.core.logging import setup_logger

logger = setup_logger(__name__)

def ingest_data(raw_data_dir: str = "data/raw"):
    # 1. Initialize Pipeline and Vector DB
    pipeline = DocumentPipeline()
    try:
        vector_store = VectorStore()
    except Exception as e:
        logger.error(f"Failed to initialize Vector Store: {e}")
        return

    # 2. Find documents
    files = glob.glob(os.path.join(raw_data_dir, "**", "*.*"), recursive=True)
    supported_exts = {".pdf", ".docx", ".xlsx", ".txt"}
    files_to_process = [f for f in files if os.path.splitext(f)[1].lower() in supported_exts]

    logger.info(f"Found {len(files_to_process)} documents to process and ingest.")

    total_chunks_added = 0

    # 3. Process and ingest each file
    for filepath in files_to_process:
        try:
            logger.info(f"Processing {filepath}...")
            # Use our custom processor
            processed_data = pipeline.process_file(filepath)
            
            # Prepare for ingestion
            texts = []
            metadatas = []
            ids = []
            
            base_meta = processed_data.get("metadata", {})
            file_lang = processed_data.get("language", "unknown")
            
            for chunk in processed_data.get("chunks", []):
                content = chunk.get("content", "").strip()
                if not content:
                    continue
                    
                chunk_id = f"{base_meta.get('source_file')}_chunk_{chunk.get('chunk_id')}"
                
                # We blend the document level metadata with chunk level stuff
                meta = {
                    "source": base_meta.get('source_file', 'unknown'),
                    "document_type": base_meta.get('document_type', 'unknown'),
                    "department": base_meta.get('department', 'unknown'),
                    "date": base_meta.get('date', 'unknown') or 'unknown',
                    "language": file_lang
                }
                
                texts.append(content)
                metadatas.append(meta)
                ids.append(chunk_id)
                
            if texts:
                vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
                total_chunks_added += len(texts)
                logger.info(f"Successfully ingested {len(texts)} chunks from {filepath}")
                
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(f"Ingestion complete. Total chunks added: {total_chunks_added}")
    
    # Print stats
    stats = vector_store.get_collection_stats()
    logger.info(f"ChromaDB Collection now contains {stats['count']} total chunks.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest_data()
