import os
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from unihelp.core.config import settings
from unihelp.core.logging import setup_logger

logger = setup_logger(__name__)

class EmailGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
        
        self.templates = {
            "attestation": "Demande d'attestation de scolarité",
            "reclamation": "Réclamation de notes",
            "stage": "Demande de stage",
            "bourse": "Demande de bourse",
            "absence": "Justificatif d'absence",
            "reinscription": "Réinscription"
        }
        
        self.prompt = PromptTemplate(
            input_variables=["template_type", "student_info", "context"],
            template="""Tu es un assistant administratif aidant un étudiant de l'IIT/NAU Tunisia à rédiger un email officiel.

Type de demande: {template_type}
Informations de l'étudiant: {student_info}
Contexte/Règles de l'université: {context}

Rédige un email complet et formel, prêt à être envoyé par l'étudiant à l'administration.
L'email doit inclure:
- Un "Objet:" clair et professionnel.
- Une formule de politesse d'introduction adaptée.
- Le corps du message, clair, précis et incluant toutes les informations pertinentes de l'étudiant.
- Une checklist (sous forme de liste à puces "Pièces jointes:") listant les documents nécessaires selon les règles de l'université (s'il y en a).
- Une formule de politesse de fin.

L'email doit être en français.

Email généré:
"""
        )

    def get_supported_templates(self) -> Dict[str, str]:
        return self.templates

    def generate(self, template_key: str, student_info: str, rag_context: str = "") -> str:
        if template_key not in self.templates:
            raise ValueError(f"Template type '{template_key}' is not supported.")
            
        logger.info(f"Generating email for template: {template_key}")
        template_name = self.templates[template_key]
        
        chain = self.prompt | self.llm
        result = chain.invoke({
            "template_type": template_name,
            "student_info": student_info,
            "context": rag_context
        })
        
        return result.content
