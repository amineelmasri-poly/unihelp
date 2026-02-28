import re

class MetadataExtractor:
    @staticmethod
    def extract(text: str) -> dict:
        metadata = {
            "document_type": "Unknown",
            "date": None,
            "department": "Unknown"
        }
        
        # 1. Document Type heuristics
        doc_type_patterns = [
            r'(?i)\b(Arrêté|Décision|Procès-verbal|PV|Note\s+d\'information|Avis|Circulaire)\b'
        ]
        for pattern in doc_type_patterns:
            match = re.search(pattern, text)
            if match:
                # Capitalize the first letter
                metadata["document_type"] = match.group(0).capitalize()
                break
                
        # 2. Date heuristics
        # e.g., 12/05/2023, 12-05-2023, 12 mai 2023
        date_patterns = [
            r'\b\d{2}/\d{2}/\d{4}\b',
            r'\b\d{2}-\d{2}-\d{4}\b',
            r'\b\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}\b'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                metadata["date"] = match.group(0)
                break
                
        # 3. Department heuristics
        # e.g. "Département de l'informatique", "Faculté des Sciences"
        department_patterns = [
            r'(?i)(Département\s+d(?:e\s+|es\s+|u\s+|e\s+l\')?[a-zA-ZÀ-ÿ\s]+)(?:[\r\n,]|$)',
            r'(?i)(Faculté\s+d(?:e\s+|es\s+|u\s+|e\s+l\')?[a-zA-ZÀ-ÿ\s]+)(?:[\r\n,]|$)',
            r'(?i)(Service\s+d(?:e\s+|es\s+|u\s+|e\s+l\')?[a-zA-ZÀ-ÿ\s]+)(?:[\r\n,]|$)',
        ]
        for pattern in department_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["department"] = match.group(1).strip()
                break

        return metadata
