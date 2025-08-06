from llama_index.core import PromptTemplate

QA_PROMPT = PromptTemplate(
    """You are an AI assistant that answers questions strictly based on the provided resume content.
    Follow these rules:
    1. Only use information from the resume
    2. Be concise and factual
    3. If the answer isn't in the resume, say "This information is not in the resume"
    4. Never make up details

    Context:
    {context_str}

    Question: {query_str}
    
    Answer: """
)

EXPERIENCE_PROMPT = PromptTemplate(
    """Extract only the relevant professional experience from the resume that matches this query.
    Include: job titles, companies, durations, and key responsibilities.
    
    Query: {query_str}
    
    Resume Content:
    {context_str}
    
    Relevant Experience: """
)