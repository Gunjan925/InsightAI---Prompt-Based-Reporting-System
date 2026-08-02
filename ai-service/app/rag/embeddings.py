# Generates embeddings using a local embedding model (e.g., Sentence Transformers).
import logging
from app.config.settings import settings
from app.exceptions.custom_exception import EmbeddingError

logger = logging.getLogger("ai_service")

# Lazy loading cache for sentence-transformers model
# to load(download) the model only once.
_embedding_model_instance = None

def _get_embedding_model():
    """
    Lazily loads the local SentenceTransformer model.
    This avoids blocking application startup if the model files are not yet cached
    or if the dependencies are being configured in the background.
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer model: {settings.EMBEDDING_MODEL_NAME}")
            _embedding_model_instance = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Local SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers embedding model: {e}")
            raise EmbeddingError(f"Failed to initialize sentence-transformers embedding model: {str(e)}")
    return _embedding_model_instance

class EmbeddingGenerator:
    """
    Responsible for generating high-dimensional dense vector representations
    of dataset rows and queries for the semantic retrieval pipeline.
    """
    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generates vector embeddings for a list of string elements.
        """
        try:
            model = _get_embedding_model()
            embeddings = model.encode(texts, show_progress_bar=False)
            # converts the generated embeddings into normal Python lists.
            if hasattr(embeddings, "tolist"):
                return embeddings.tolist()
            return [list(map(float, emb)) for emb in embeddings]
        except Exception as e:
            logger.error(f"Error encoding list of texts to embeddings: {e}")
            raise EmbeddingError(f"Failed to encode text embeddings: {str(e)}")

    def get_embedding(self, text: str) -> list[float]:
        """
        Generates vector embedding for a single query or text block.
        """
        try:
            model = _get_embedding_model()
            embeddings = model.encode([text], show_progress_bar=False)
            if hasattr(embeddings, "tolist"):
                return embeddings[0].tolist()
            return list(map(float, embeddings[0]))
        except Exception as e:
            logger.error(f"Error encoding single text to embedding: {e}")
            raise EmbeddingError(f"Failed to encode query embedding: {str(e)}")