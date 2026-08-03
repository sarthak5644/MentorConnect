"""
app/services/chat_service.py
--------------------------------
Business logic for chat threads and messaging between students and mentors.
Access is restricted to the two participants of the underlying mentorship_request.
"""

from typing import List, Optional
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.models.chat import Chat, Message
from app.models.user import User
from app.models.enums import MessageType, NotificationType
from app.repositories.chat_repository import ChatRepository, MessageRepository
from app.repositories.mentorship_request_repository import MentorshipRequestRepository
from app.services.notification_service import NotificationService
from app.services.file_upload_service import FileUploadService
from app.utils.sanitizer import sanitize_text


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.message_repo = MessageRepository(db)
        self.request_repo = MentorshipRequestRepository(db)
        self.notification_service = NotificationService(db)

    def _get_chat_and_verify_access(self, chat_id: int, user: User) -> Chat:
        chat = self.chat_repo.get(chat_id)
        if chat is None:
            raise NotFoundException("Chat not found.")

        mentorship_request = self.request_repo.get(chat.mentorship_request_id)
        if mentorship_request is None:
            raise NotFoundException("Associated mentorship request not found.")

        student_user_id = mentorship_request.student.user_id if mentorship_request.student else None
        mentor_user_id = mentorship_request.mentor.user_id if mentorship_request.mentor else None

        if user.id not in (student_user_id, mentor_user_id):
            raise ForbiddenException("You do not have access to this chat.")

        return chat

    def get_other_participant_user_id(self, chat: Chat, sender_id: int) -> Optional[int]:
        mentorship_request = self.request_repo.get(chat.mentorship_request_id)
        if mentorship_request is None:
            return None
        student_user_id = mentorship_request.student.user_id if mentorship_request.student else None
        mentor_user_id = mentorship_request.mentor.user_id if mentorship_request.mentor else None
        return mentor_user_id if sender_id == student_user_id else student_user_id

    def send_text_message(self, chat_id: int, sender: User, content: str) -> Message:
        chat = self._get_chat_and_verify_access(chat_id, sender)
        if not chat.is_active:
            raise BadRequestException("This chat thread is no longer active.")

        message = self.message_repo.create({
            "chat_id": chat.id,
            "sender_id": sender.id,
            "message_type": MessageType.TEXT,
            "content": sanitize_text(content),
            "is_read": False,
        })

        chat.last_message_at = datetime.utcnow()
        self.db.add(chat)
        self.db.commit()

        recipient_id = self.get_other_participant_user_id(chat, sender.id)
        if recipient_id:
            self.notification_service.notify(
                recipient_id, NotificationType.CHAT_MESSAGE, f"New message from {sender.full_name}",
                body=content[:200], reference_id=chat.id,
            )
        return message

    async def send_attachment_message(self, chat_id: int, sender: User, file: UploadFile) -> Message:
        chat = self._get_chat_and_verify_access(chat_id, sender)
        if not chat.is_active:
            raise BadRequestException("This chat thread is no longer active.")

        relative_path, _size = await FileUploadService.upload_chat_attachment(file)
        msg_type = MessageType.IMAGE if file.content_type and "image" in file.content_type else MessageType.FILE

        message = self.message_repo.create({
            "chat_id": chat.id,
            "sender_id": sender.id,
            "message_type": msg_type,
            "attachment_path": relative_path,
            "is_read": False,
        })

        chat.last_message_at = datetime.utcnow()
        self.db.add(chat)
        self.db.commit()

        recipient_id = self.get_other_participant_user_id(chat, sender.id)
        if recipient_id:
            self.notification_service.notify(
                recipient_id, NotificationType.CHAT_MESSAGE, f"New attachment from {sender.full_name}",
                reference_id=chat.id,
            )
        return message

    def list_messages(self, chat_id: int, user: User, skip: int = 0, limit: int = 50) -> List[Message]:
        chat = self._get_chat_and_verify_access(chat_id, user)
        self.message_repo.mark_all_read(chat.id, user.id)
        return self.message_repo.list_by_chat(chat.id, skip, limit)

    def get_chat_for_request(self, mentorship_request_id: int, user: User) -> Chat:
        chat = self.chat_repo.get_by_mentorship_request(mentorship_request_id)
        if chat is None:
            raise NotFoundException("No chat thread exists for this mentorship request yet.")
        return self._get_chat_and_verify_access(chat.id, user)
