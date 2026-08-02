# Creates, updates and manages the vector database for uploaded datasets.
import logging
import pandas as pd
from app.rag.text_converter import convert_dataframe_to_text_chunks
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStoreManager
from app.exceptions.custom_exception import EmbeddingError

logger = logging.getLogger("ai_service")

class RagService:
    """
    Coordinates RAG pipeline elements for uploaded datasets.
    Ingests tabular data, generates dense embeddings, and commits to ChromaDB.
    """
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store_manager = VectorStoreManager()

    def build_rag_pipeline(self, dataset_id: str, df: pd.DataFrame) -> None:
        """
        Creates and stores dense vector embeddings of a dataset in ChromaDB.
        1. Translates rows and schemas into text chunks.
        2. Encodes text chunks into high-dimensional vectors.
        3. Persists chunks and embeddings in dataset-specific ChromaDB collections.
        """
        if df.empty:
            logger.warning(f"Empty dataframe provided for dataset '{dataset_id}'. Skipping RAG generation.")
            return

        try:
            logger.info(f"Building RAG pipeline for dataset '{dataset_id}' with {len(df)} rows.")

            # 1. Transform DataFrame rows to descriptive text documents
            chunks = convert_dataframe_to_text_chunks(df)
            logger.info(f"Converted dataset into {len(chunks)} text chunks.")

            # 2. Extract string content from chunks and compute dense vector embeddings
            texts_to_embed = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_generator.get_embeddings(texts_to_embed)
            logger.info("Generated dense vector representations for all chunks.")

            # 3. Store chunks, metadata, and embeddings in persistent ChromaDB storage
            self.vector_store_manager.store_dataset_chunks(
                dataset_id=dataset_id,
                chunks=chunks,
                embeddings=embeddings
            )
            logger.info(f"RAG pipeline built and verified for dataset '{dataset_id}'.")

        except EmbeddingError:
            raise
        except Exception as e:
            logger.error(f"Failed to build RAG pipeline for dataset '{dataset_id}': {e}")
            raise EmbeddingError(f"RAG indexing pipeline execution failed: {str(e)}")

    def purge_dataset_index(self, dataset_id: str) -> None:
        """
        Deletes the ChromaDB collection associated with the dataset.
        """
        try:
            self.vector_store_manager.delete_dataset_collection(dataset_id)
            logger.info(f"Successfully purged vector index for '{dataset_id}'")
        except Exception as e:
            logger.error(f"Error purging vector index: {e}")