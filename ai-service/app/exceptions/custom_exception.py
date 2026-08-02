# Defines reusable custom exception classes.

class AIServiceException(Exception):
    """
    Base exception class for all AI Service specific exceptions.
    Provides standard attributes for message and associated HTTP status code.
    """
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatasetProcessingError(AIServiceException):
    """
    Raised when dataset reading, parsing, cleaning, or descriptive statistical
    calculations fail due to formatting or datatype constraints.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class EmbeddingError(AIServiceException):
    """
    Raised when text chunking, embedding generation, or vector database (ChromaDB)
    storage and retrieval operations fail.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class LLMError(AIServiceException):
    """
    Raised when prompt formatting, communication with Google Gemini, or response
    generation from the LLM fails.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=502)

class ReportGenerationError(AIServiceException):
    """
    Raised when assembling charts, tables, and AI insights into HTML or PDF reports fails.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=500)