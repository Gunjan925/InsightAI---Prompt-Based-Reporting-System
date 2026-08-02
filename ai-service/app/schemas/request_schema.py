# Defines and validates incoming API requests using Pydantic models.
from pydantic import BaseModel, Field

class ChatQueryRequest(BaseModel):
    """
    Validates a natural language question query against a specific dataset collection context.
    """
    dataset_id: str = Field(..., description="Unique identifier/filename of the dataset")
    query: str = Field(..., description="The user's natural language question about the dataset")
    top_k: int = Field(default=8, ge=1, le=20, description="Number of context rows to retrieve via vector search")

class DashboardRequest(BaseModel):
    """
    Validates requests to perform preprocessing and return dashboard details.
    """
    dataset_id: str = Field(..., description="Unique identifier of the dataset")