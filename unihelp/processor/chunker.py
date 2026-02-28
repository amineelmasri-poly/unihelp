import re

class SemanticChunker:
    def __init__(self, target_size: int = 800, max_size: int = 1000, overlap: int = 150):
        self.target_size = target_size
        self.max_size = max_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        # Split text into paragraphs based on double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If a single paragraph is larger than max_size, we need to split it by sentences
            if len(para) > self.max_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= self.target_size:
                        current_chunk += (" " if current_chunk else "") + sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        # Start new chunk with overlap
                        # Find the logical overlap (last sentence or words of the previous chunk)
                        overlap_text = self._get_overlap_text(current_chunk)
                        current_chunk = overlap_text + sentence if overlap_text else sentence
            else:
                # Add paragraph to current_chunk
                if len(current_chunk) + len(para) + 2 <= self.target_size:
                    current_chunk += ("\n\n" if current_chunk else "") + para
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = overlap_text + para if overlap_text else para
                    
        if current_chunk:
            chunks.append(current_chunk)
            
        return [c.strip() for c in chunks if c.strip()]

    def _get_overlap_text(self, text: str) -> str:
        if len(text) <= self.overlap:
            return ""
        
        # Try to find a sentence boundary near the overlap length
        overlap_start = len(text) - self.overlap
        # Look for the first period after the overlap_start
        match = re.search(r'[.!?]\s+', text[overlap_start:])
        if match:
            return text[overlap_start + match.end():] + " "
        
        # Fallback: just return the last `overlap` characters
        return text[-self.overlap:] + " "
