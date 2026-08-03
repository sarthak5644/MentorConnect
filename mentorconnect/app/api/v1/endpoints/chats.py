"""
app/api/v1/endpoints/chats.py
---------------------------------
Endpoints for chat threads and messaging between students and mentors.
"""

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.chat_service import ChatService
from app.schemas.common import ApiResponse
from app.schemas.chat import MessageCreateRequest, MessageOut, ChatOut

router = APIRouter(prefix="/chats", tags=["Chat & Messaging"])


@router.get(
    "/by-request/{mentorship_request_id}", response_model=ApiResponse[ChatOut],
    summary="Get the chat thread for an accepted mentorship request",
)
def get_chat_for_request(
    mentorship_request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    chat = service.get_chat_for_request(mentorship_request_id, current_user)
    return ApiResponse(data=chat)


@router.get(
    "/{chat_id}/messages", response_model=ApiResponse[List[MessageOut]],
    summary="List messages in a chat (marks them read)",
)
def list_messages(
    chat_id: int, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    messages = service.list_messages(chat_id, current_user, (page - 1) * page_size, page_size)
    return ApiResponse(data=messages)


@router.post("/{chat_id}/messages", response_model=ApiResponse[MessageOut], summary="Send a text message")
def send_message(
    chat_id: int, payload: MessageCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    message = service.send_text_message(chat_id, current_user, payload.content)
    return ApiResponse(message="Message sent.", data=message)


@router.post(
    "/{chat_id}/messages/attachment", response_model=ApiResponse[MessageOut],
    summary="Send an image/file attachment message",
)
async def send_attachment(
    chat_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db)
    message = await service.send_attachment_message(chat_id, current_user, file)
    return ApiResponse(message="Attachment sent.", data=message)
