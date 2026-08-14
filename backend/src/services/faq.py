from langchain_openai import OpenAIEmbeddings
from openai import OpenAIError
from sqlmodel import select
from src.database import get_session
from src.models import FAQ


# We use embeddings instead of putting all of the questions in the llm context
# Stopping the context window from being saturated.
def get_faq_answer (query: str) -> str:
    """
    Retrieves relevant FAQ answers based on vector similarity to the user's query.

    Generates an embedding for the input query using OpenAI, queries the database 
    for the top 2 matching FAQs via cosine distance, and formats the results 
    into a response string.

    Args:
        query (str): The user's question or search prompt.

    Returns:
        str: A formatted string containing the most relevant FAQ questions and 
            answers, or an error/not-found message if unretrievable.
    """
    # Initialize the embedder.
    embedder = OpenAIEmbeddings(model = "text-embedding-3-small")

    # Embed the provided text.
    try:
        query_embedding = embedder.embed_query(query)

    except OpenAIError:
        return "Error processing the embedding for the query."

    with next(get_session()) as session:
        # We compare the embedding from the prompt to the info in the database.
        statement = select(FAQ).order_by(FAQ.embedding.cosine_distance(query_embedding)).limit(2)
    
        resultados = session.exec(statement).all()

        if not resultados:
            return "Could not find any relevant information regarding the question."

        output = "Oficial information found in Unicaja FAQs: \n"

        for faq in resultados:
            output += f"\n- Question: {faq.pregunta}\n Answer: {faq.respuesta}\n"

        return output