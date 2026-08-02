# Stores and manages embeddings in ChromaDB.
import logging
import chromadb
from app.config.settings import settings
from app.exceptions.custom_exception import EmbeddingError

logger = logging.getLogger("ai_service")

# Lazy loading instance cache for ChromaDB client
_chroma_client_instance = None

def _get_chroma_client():
    """
    Lazily initializes the persistent ChromaDB client using the path configured in settings.
    """
    global _chroma_client_instance
    if _chroma_client_instance is None:
        try:
            logger.info(f"Initializing persistent ChromaDB client at: {settings.CHROMA_DB_PATH}")
            _chroma_client_instance = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        except Exception as e:
            logger.error(f"Failed to connect to local ChromaDB: {e}")
            raise EmbeddingError(f"Vector database initialization failed: {str(e)}")
    return _chroma_client_instance

# This class is responsible for managing vector storage in ChromaDB. It performs three main tasks:
# Create a valid collection name
# Store embeddings for a dataset
# Delete embeddings when a dataset is deleted
class VectorStoreManager:
    """
    Manages the lifecycle of high-dimensional vectors stored in ChromaDB.
    Creates isolated collection spaces for datasets to enable precise semantic queries.
    """
    def __init__(self):
        self.client = _get_chroma_client()

    def _get_safe_collection_name(self, name: str) -> str:
        """
        Sanitizes name to conform with ChromaDB collection standards:
        - Between 3 and 63 characters long
        - Alphanumeric, underscores, or hyphens only
        - Must start and end with alphanumeric characters
        """
        sanitized = "".join(c for c in name if c.isalnum() or c in ("-", "_")) # ChromaDB has naming rules for collections: Length: 3–63 character Only letters, numbers, _ and  Must start and end with an alphanumeric character. Keeps only: A–Z, a–z, 0–9, _, -
        if len(sanitized) < 3: # if len is less than 3 than give name like
            sanitized = f"dataset_col_{sanitized}"
        sanitized = sanitized[:63]
        if not sanitized[0].isalnum(): # Collection cannot start with _,-
            sanitized = "col_" + sanitized[1:]
        if not sanitized[-1].isalnum(): # Collection cannot end with _,-
            sanitized = sanitized[:-1] + "1"
        return sanitized

    def store_dataset_chunks(self, dataset_id: str, chunks: list[dict], embeddings: list[list[float]]) -> None:
        """
        Saves textual blocks along with their corresponding vector embeddings to ChromaDB.
        Recreates the collection if it exists to refresh indices.
        """
        collection_name = self._get_safe_collection_name(dataset_id)
        try:
            # Delete existing collection to avoid merging old data
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted pre-existing ChromaDB collection: {collection_name}")
            except Exception:
                pass

            # Create clean collection, optimizing search space with cosine similarity
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"} # This tells ChromaDB to use Cosine Similarity for searching.
            )

            ids = [f"chunk_{i}" for i in range(len(chunks))]
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            # Ingest documents in chunk batches to prevent network/memory spikes
            batch_size = 500
            for i in range(0, len(chunks), batch_size):
                limit = min(i + batch_size, len(chunks))
                collection.add(
                    ids=ids[i:limit],
                    embeddings=embeddings[i:limit],
                    documents=documents[i:limit],
                    metadatas=metadatas[i:limit]
                )
            logger.info(f"Successfully stored {len(chunks)} vector records in collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error executing collection save to ChromaDB: {e}")
            raise EmbeddingError(f"Vector storage update failed: {str(e)}")

    def delete_dataset_collection(self, dataset_id: str) -> None:
        """
        Deletes the ChromaDB collection associated with a given dataset ID.
        """
        collection_name = self._get_safe_collection_name(dataset_id)
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted vector collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Could not delete collection '{collection_name}': {e}")