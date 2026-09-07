# Handles the question-answering workflow using retrieval and the LLM.
import logging
from app.rag.embeddings import EmbeddingGenerator
from app.rag.retrieval import retrieve_context
from app.llm.llm_client import call_gemini
from app.exceptions.custom_exception import LLMError, EmbeddingError

logger = logging.getLogger("ai_service")

# Common generic greetings and conversational phrases
GENERIC_GREETINGS = {
    'hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening',
    'who are you', 'what are you', 'what can you do', 'help', 'test', 'testing', 'ok', 'okay', 'yes', 'no'
}

def _is_generic_greeting(query: str) -> bool:
    """Helper to detect simple greetings, generic conversational words, or extremely short queries."""
    cleaned = query.strip().lower()
    cleaned_words = cleaned.translate(str.maketrans('', '', '!?.,')).strip()
    if cleaned_words in GENERIC_GREETINGS or len(cleaned_words) < 3:
        return True
    return False

class ChatService:
    """
    Coordinates chat Q&A interactions with two-stage early relevance filtering:
    - Stage 1: Fast rule-based heuristic filter (detects generic greetings / conversational queries).
    - Stage 2: RAG Vector similarity distance filter (detects out-of-domain queries).
    - Stage 3: Grounded Gemini LLM answer execution (only reached for genuine dataset queries).
    """
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()

    async def answer_query(self, dataset_id: str, query: str, top_k: int = 8) -> dict:
        """
        Answers a user question about a dataset with early detection of unrelated prompts to optimize token utilization.
        """
        logger.info(f"Received Q&A request for dataset '{dataset_id}': '{query}'")

        try:
            # ── STAGE 1: Fast Rule-Based Greeting / Conversational Filter ─────
            if _is_generic_greeting(query):
                logger.info(f"Stage 1 filter triggered for generic prompt: '{query}'. Bypassing LLM call.")
                return {
                    "response": "Hello! I am your InsightAI Data Assistant. Please ask any specific questions about your uploaded dataset (such as column trends, statistical summaries, top records, or anomalies), and I will analyze the dataset for you!",
                    "retrieved_context": []
                }

            # ── STAGE 2: Vector Search & Semantic Relevance Filter ───────────
            # 1. Generate query embedding vector
            query_embedding = self.embedding_generator.get_embedding(query)

            # 2. Retrieve relevant database rows from ChromaDB
            retrieved_chunks = retrieve_context(
                dataset_id=dataset_id,
                query_text=query,
                query_embedding=query_embedding,
                top_k=top_k
            )

            # Check semantic distance threshold (L2 distance > 1.35 indicates no correlation to dataset records)
            MAX_RELEVANT_DISTANCE = 1.35
            min_dist = retrieved_chunks[0].get("distance", 2.0) if retrieved_chunks else 2.0

            if not retrieved_chunks or min_dist > MAX_RELEVANT_DISTANCE:
                logger.info(f"Stage 2 filter triggered for out-of-domain query: '{query}' (min_dist: {min_dist:.4f}). Bypassing LLM call.")
                return {
                    "response": f"I couldn't find any relevant data in this dataset related to your question: \"{query}\".\n\n- **Tip**: Please ask questions specifically related to the dataset's attributes, numbers, or trends (e.g. *\"What are the top sales months?\"* or *\"Show metric averages\"*).",
                    "retrieved_context": []
                }

            # ── STAGE 3: Execute Grounded Gemini LLM Call ─────────────────────
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
            response_text = await call_gemini(prompt, model_name="gemini-3.6-flash", temperature=0.1)

            return {
                "response": response_text,
                "retrieved_context": retrieved_chunks
            }

        except (EmbeddingError, LLMError):
            raise
        except Exception as e:
            logger.error(f"Error executing ChatService Q&A query: {e}")
            raise LLMError(f"Failed to process chat query: {str(e)}")