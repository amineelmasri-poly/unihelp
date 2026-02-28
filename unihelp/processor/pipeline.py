import json
import os
from datetime import datetime
from .extractors import get_extractor
from .cleaner import TextCleaner
from .metadata import MetadataExtractor
from .chunker import SemanticChunker

class DocumentPipeline:
    def __init__(self, target_chunk_size: int = 800, max_chunk_size: int = 1000, chunk_overlap: int = 150):
        self.cleaner = TextCleaner()
        self.metadata_extractor = MetadataExtractor()
        self.chunker = SemanticChunker(
            target_size=target_chunk_size, 
            max_size=max_chunk_size, 
            overlap=chunk_overlap
        )

    def process_file(self, file_path: str) -> dict:
        """Processes a single document and returns the structured output."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Processing: {file_path}")
        
        # 1. Extract text
        extractor = get_extractor(file_path)
        raw_text = extractor.extract(file_path)
        
        # 2. Clean text and detect language
        cleaned_text = self.cleaner.clean(raw_text)
        language = self.cleaner.detect_language(cleaned_text)
        
        # 3. Extract metadata
        metadata = self.metadata_extractor.extract(cleaned_text)
        
        # Add basic file info
        file_name = os.path.basename(file_path)
        metadata["source_file"] = file_name
        metadata["processed_at"] = datetime.now().isoformat()
        
        # 4. Chunk text
        chunks = self.chunker.chunk(cleaned_text)
        
        # Construct final output
        result = {
            "file": file_name,
            "language": language,
            "metadata": metadata,
            "total_chunks": len(chunks),
            "chunks": [
                {
                    "chunk_id": i,
                    "content": chunk,
                    "char_count": len(chunk)
                }
                for i, chunk in enumerate(chunks)
            ]
        }
        
        return result

    def process_and_save(self, file_path: str, output_path: str = None) -> str:
        """Processes a file and saves the result to a JSON file."""
        result = self.process_file(file_path)
        
        if output_path is None:
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_processed.json"
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return output_path
