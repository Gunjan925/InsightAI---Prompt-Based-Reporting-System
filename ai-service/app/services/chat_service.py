# Handles the question-answering workflow using retrieval and the LLM.
import logging
from app.rag.embeddings import EmbeddingGenerator
from app.rag.retrieval import retrieve_context
from app.llm.llm_client import call_gemini
from app.exceptions.custom_exception import LLMError, EmbeddingError

logger = logging.getLogger("ai_service")

class ChatService:
    """
    Coordinates chat Q&A interactions.
    Translates user questions into semantic vectors, retrieves relevant data rows,
    and prompts Gemini to answer the query grounded in the retrieved dataset context.
    """
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()

    async def answer_query(self, dataset_id: str, query: str, top_k: int = 8) -> dict:
        """
        Answers a user question about a dataset by retrieving vector context and calling Gemini.
        Returns the text response and list of retrieved context segments.
        """
        logger.info(f"Received Q&A request for dataset '{dataset_id}': '{query}'")

        try:
            # 1. Generate query embedding vector representation
            query_embedding = self.embedding_generator.get_embedding(query)

            # 2. Retrieve relevant database rows from ChromaDB
            retrieved_chunks = retrieve_context(
                dataset_id=dataset_id,
                query_text=query,
                query_embedding=query_embedding,
                top_k=top_k
            )

            # 3. Format the context blocks for prompt construction
            context_blocks = []
            for idx, doc in enumerate(retrieved_chunks):
                context_blocks.append(f"Snippet {idx+1}:\n{doc['text']}")
            context_str = "\n\n".join(context_blocks)

            # 4. Construct prompt optimized for grounded QA responses
            prompt = f"""
                    You are an intelligent data analysis assistant. You are answering a user's question about a structured dataset.
                    Below is the subset of row records retrieved from the database as relevant context to answer the question.

                    ### DATA CONTEXT SNIPPETS
                    {context_str}

                    ### USER QUESTION
                    "{query}"

                    ### ANSWER INSTRUCTIONS
                    - Answer the user's question accurately based ONLY on the provided context snippets above.
                    - If the snippets do not contain enough information to answer the question, state that clearly. Do not make up facts.
                    - Keep your answer clear, precise, and professional.
                    - Use bullet points or markdown bolding to format the answer for easy reading.
                    """

            # 5. Execute Gemini LLM call
            response_text = await call_gemini(prompt, model_name="gemini-1.5-flash", temperature=0.1)

            return {
                "response": response_text,
                "retrieved_context": retrieved_chunks
            }

        except (EmbeddingError, LLMError):
            raise
        except Exception as e:
            logger.error(f"Error executing ChatService Q&A query: {e}")
            raise LLMError(f"Failed to process chat query: {str(e)}")