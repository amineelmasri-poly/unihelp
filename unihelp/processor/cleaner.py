import re
from langdetect import detect, DetectorFactory

# Set seed for reproducible langdetect results
DetectorFactory.seed = 0

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        # Remove common headers/footers numbers like "Page X of Y" or solitary page numbers
        text = re.sub(r'(?i)^\s*page\s+\d+\s*(of\s+\d+)?\s*$', '', text, flags=re.MULTILINE)
        
        # Replace 3 or more newlines with double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()

    @staticmethod
    def detect_language(text: str) -> str:
        try:
            # Langdetect might throw an exception if the text contains no characters
            if not text.strip():
                return "unknown"
            return detect(text)
        except Exception:
            return "unknown"
