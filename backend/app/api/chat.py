from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.config.database import get_db
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.models.chat_session import ChatSession, ChatMessage
from app.services.ai_client import AiClient

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatAskRequest(BaseModel):
    file_id: int
    query: str
    session_id: Optional[int] = None

class CreateSessionRequest(BaseModel):
    file_id: int
    title: Optional[str] = "New Discussion"

@router.get("/sessions/{file_id}", status_code=status.HTTP_200_OK)
def get_file_chat_sessions(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all saved chat sessions and messages for a specific dataset file from MySQL.
    """
    sessions = db.query(ChatSession).filter(
        ChatSession.file_id == file_id,
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()

    result = []
    for s in sessions:
        messages = [{
            "id": f"msg_{m.id}",
            "sender": m.sender,
            "text": m.text,
            "timestamp": m.created_at.strftime("%H:%M")
        } for m in s.messages]

        result.append({
            "id": s.id,
            "title": s.title,
            "updatedAt": s.updated_at.isoformat(),
            "messages": messages
        })

    return result

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_chat_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session for a dataset file in MySQL.
    """
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == request.file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    session = ChatSession(
        user_id=current_user.id,
        file_id=request.file_id,
        title=request.title or "New Discussion"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "title": session.title,
        "updatedAt": session.updated_at.isoformat(),
        "messages": []
    }

@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a chat session and its messages from MySQL.
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"message": "Chat session deleted successfully"}

@router.post("/ask", status_code=status.HTTP_200_OK)
async def ask_chat_question(
    request: ChatAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts a dataset file_id and a user question query.
    Saves user and bot messages into MySQL database under the chat session.
    """
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == request.file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file not found or access denied."
        )

    # Get or create active session
    session = None
    if request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == request.session_id,
            ChatSession.user_id == current_user.id
        ).first()

    if not session:
        # Create a new session if none exists
        session_title = request.query[:30] + "..." if len(request.query) > 30 else request.query
        session = ChatSession(
            user_id=current_user.id,
            file_id=request.file_id,
            title=session_title
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    elif session.title == "New Discussion" and request.query:
        session.title = request.query[:30] + "..." if len(request.query) > 30 else request.query
        db.commit()

    # Save user message to DB
    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        text=request.query
    )
    db.add(user_msg)
    db.commit()

    # Ensure dataset RAG index is primed
    await AiClient.generate_dashboard_from_ai_service(
        filename=db_file.filename,
        file_content=db_file.file_content,
        mime_type=db_file.mime_type
    )

    # Ask the question via AI Service
    chat_result = await AiClient.ask_chat_ai_service(
        dataset_id=db_file.filename,
        query=request.query
    )

    bot_response_text = chat_result.get("response", "No response generated.")

    # Save bot message to DB
    bot_msg = ChatMessage(
        session_id=session.id,
        sender="bot",
        text=bot_response_text
    )
    db.add(bot_msg)
    db.commit()

    return {
        "session_id": session.id,
        "response": bot_response_text,
        "retrieved_context": chat_result.get("retrieved_context", [])
    }
