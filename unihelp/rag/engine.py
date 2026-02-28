import os
from dateutil import parser as date_parser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from unihelp.rag.vector_store import VectorStore
from unihelp.core.config import settings
from unihelp.core.logging import setup_logger

logger = setup_logger(__name__)

class RAGEngine:
    def __init__(self):
        self.vector_store = VectorStore()
        
        # We use a robust model like GPT-4o-mini or GPT-3.5-turbo 
        # based on availability. Assuming the user has a standard setup.
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,  # Low temp for factual answers
            api_key=settings.OPENAI_API_KEY
        )
        
        # Simple prompt that enforces grounding and multi-lingual behavior
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are UniHelp, an administrative assistant for IIT/NAU Tunisia.
Your goal is to answer student administrative questions accurately and professionally.
You MUST base your answer ONLY on the provided Context.
If the Context does not contain the answer, gracefully say "Désolé, je n'ai pas trouvé l'information exacte dans la base de données de l'université."
Answer in the SAME LANGUAGE as the user's question.

Context: 
{context}

Guidelines:
- Cite your sources where possible by referring to the document type and department.
- Be concise but helpful.
- For dates, be exact.
- Do not make up any policies."""),
            ("human", "{question}")
        ])
        
    def _format_docs(self, docs):
        formatted = []
        sources = []
        for i, doc in enumerate(docs):
            content = doc["page_content"]
            meta = doc["metadata"]
            
            # Format metadata
            source_desc = f"[Source {i+1}: {meta.get('document_type', 'Document')} from {meta.get('department', 'University')}]"
            sources.append({
                "id": i+1,
                "file": meta.get("source", "Unknown"),
                "department": meta.get("department", ""),
                "date": meta.get("date", "")
            })
            
            formatted.append(f"{source_desc}\n{content}")
            
        return "\n\n".join(formatted), sources

    def answer(self, question: str, k: int = 4):
        logger.info(f"Answering query: {question}")
        
        # 1. Retrieve raw documents
        docs = self.vector_store.similarity_search(question, k=k)
        
        if not docs:
            logger.warning("No context found for query.")
            return {
                "answer": "Désolé, je ne trouve aucun document relatif à votre demande.",
                "sources": []
            }
            
        # 2. Format documents into prompt context
        context_str, sources = self._format_docs(docs)
        
        # 3. Generate Answer
        chain = self.prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": context_str, "question": question})
        
        return {
            "answer": response,
            "sources": sources
        }
