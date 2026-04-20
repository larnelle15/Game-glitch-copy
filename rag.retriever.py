"""
rag_retriever.py
RAG (Retrieval-Augmented Generation) module for Game Glitch Investigator.
Searches the glitch knowledge base for relevant bug patterns before
passing context to the AI agent.
"""
 
from rag_knowledge_base import GLITCH_KNOWLEDGE_BASE
 
 
def retrieve_relevant_docs(query: str, top_k: int = 3) -> list[dict]:
    """
    Simple keyword-based retrieval over the glitch knowledge base.
    Scores each document by how many of its tags/title words appear in the query.
    Returns the top_k most relevant documents.
    """
    query_lower = query.lower()
    scored = []
 
    for doc in GLITCH_KNOWLEDGE_BASE:
        score = 0
        # Score tag matches
        for tag in doc["tags"]:
            if tag in query_lower:
                score += 2
        # Score title word matches
        for word in doc["title"].lower().split():
            if word in query_lower:
                score += 1
        # Score description keyword matches
        desc_words = ["state", "reset", "hint", "score", "comparison",
                      "string", "integer", "type", "range", "input", "validation",
                      "difficulty", "session", "streamlit", "logic", "bug", "fix"]
        for word in desc_words:
            if word in query_lower and word in doc["description"].lower():
                score += 1
 
        scored.append((score, doc))
 
    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [doc for score, doc in scored[:top_k] if score > 0]
 
    # Always return at least 1 doc (most general) if nothing matched
    if not top_docs:
        top_docs = [GLITCH_KNOWLEDGE_BASE[0]]
 
    return top_docs
 
 
def format_docs_for_prompt(docs: list[dict]) -> str:
    """Format retrieved docs into a string for the AI prompt."""
    if not docs:
        return "No relevant knowledge base entries found."
 
    lines = ["=== RETRIEVED GLITCH KNOWLEDGE BASE ENTRIES ===\n"]
    for doc in docs:
        lines.append(f"[{doc['id']}] {doc['title']}")
        lines.append(f"Description: {doc['description']}")
        lines.append(f"Fix: {doc['fix']}")
        lines.append(f"Bad Example:\n  {doc['example_bad']}")
        lines.append(f"Good Example:\n  {doc['example_good']}")
        lines.append("")
    return "\n".join(lines)
 
 
def retrieve_and_format(query: str, top_k: int = 3) -> str:
    """Convenience function: retrieve + format in one call."""
    docs = retrieve_relevant_docs(query, top_k=top_k)
    return format_docs_for_prompt(docs)
 