# Retrieves the most relevant chunks based on the user's query.
import logging
from app.rag.vector_store import _get_chroma_client, VectorStoreManager
from app.exceptions.custom_exception import EmbeddingError

logger = logging.getLogger("ai_service")

def retrieve_context(dataset_id: str, query_text: str, query_embedding: list[float], top_k: int = 10) -> list[dict]:
    """
    Queries ChromaDB to retrieve the top_k most semantically similar text blocks
    matching the query embedding for a specific dataset ID.
    Returns list of dicts with 'text', 'metadata', and 'distance'.
    """
    try:
        client = _get_chroma_client() # Gets the ChromaDB client. Equivalent to connecting to a database.
        v_manager = VectorStoreManager() # Creates the helper class responsible for vector database operations.
        collection_name = v_manager._get_safe_collection_name(dataset_id) # Every uploaded dataset has its own collection.
        
        try:
            # Load the targeted collection
            collection = client.get_collection(name=collection_name)
        except Exception as e:
            logger.warning(f"Target vector collection '{collection_name}' not found: {e}")
            return []

        # Query similarities using the pre-computed query embedding
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            
            for doc, meta, dist in zip(docs, metadatas, distances):
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": float(dist)
                })
                
        logger.info(f"Retrieved {len(formatted_results)} context chunks for search query from ChromaDB.")
        return formatted_results
    except Exception as e:
        logger.error(f"Error executing semantic query against ChromaDB: {e}")
        raise EmbeddingError(f"Vector search retrieval failed: {str(e)}")