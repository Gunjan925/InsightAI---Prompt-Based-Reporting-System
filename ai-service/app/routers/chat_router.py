# API endpoints for answering user questions using RAG and the LLM.
from fastapi import APIRouter, Depends, status
from app.schemas.request_schema import ChatQueryRequest
from app.schemas.response_schema import ChatResponse
from app.services.chat_service import ChatService

# Router configuration for dataset QA chats
router = APIRouter(prefix="/chat", tags=["Dataset QA Chat"])

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def ask_question(request: ChatQueryRequest) -> ChatResponse:
    """
    Accepts user question prompts regarding a dataset, searches the ChromaDB vector database
    for context, calls the Gemini model, and returns the grounded text response.
    """
    chat_service = ChatService()
    
    # Query ChatService for grounded RAG query response
    result = await chat_service.answer_query(
        dataset_id=request.dataset_id,
        query=request.query,
        top_k=request.top_k
    )
    
    return ChatResponse(
        response=result["response"],
        retrieved_context=result["retrieved_context"]
    )