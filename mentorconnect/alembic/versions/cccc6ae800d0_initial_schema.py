"""Initial schema: all MentorConnect tables

Revision ID: cccc6ae800d0
Revises:
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cccc6ae800d0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # roles
    # ------------------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.Enum("super_admin", "mentor", "student", name="rolename"),
                   nullable=False, unique=True, index=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False, unique=True, index=True),
        sa.Column("mobile_number", sa.String(length=20), nullable=True, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False, index=True),
        sa.Column("status", sa.Enum("active", "blocked", "pending", "deactivated", name="userstatus"),
                   nullable=False, server_default="pending", index=True),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_mobile_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("profile_image_url", sa.String(length=500), nullable=True),
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("blocked_at", sa.DateTime(), nullable=True),
        sa.Column("blocked_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # categories / fields (taxonomy)
    # ------------------------------------------------------------------
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "fields",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("name", sa.String(length=100), nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # students
    # ------------------------------------------------------------------
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                   nullable=False, unique=True, index=True),
        sa.Column("institution_name", sa.String(length=200), nullable=True),
        sa.Column("education_level", sa.String(length=100), nullable=True),
        sa.Column("field_of_study", sa.String(length=150), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("bio", sa.String(length=1000), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("interests", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # mentors
    # ------------------------------------------------------------------
    op.create_table(
        "mentors",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                   nullable=False, unique=True, index=True),
        sa.Column("headline", sa.String(length=200), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("years_of_experience", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_organization", sa.String(length=200), nullable=True),
        sa.Column("designation", sa.String(length=150), nullable=True),
        sa.Column("qualifications", sa.Text(), nullable=True),
        sa.Column("achievements", sa.Text(), nullable=True),
        sa.Column("hourly_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("portfolio_url", sa.String(length=500), nullable=True),
        sa.Column("approval_status", sa.Enum("pending", "approved", "rejected", name="mentorapprovalstatus"),
                   nullable=False, server_default="pending", index=True),
        sa.Column("approved_by_admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("average_rating", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_ratings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_sessions_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_accepting_requests", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # mentor_fields (many-to-many association)
    op.create_table(
        "mentor_fields",
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("field_id", sa.Integer(), sa.ForeignKey("fields.id", ondelete="CASCADE"), primary_key=True),
    )

    # ------------------------------------------------------------------
    # mentor_documents
    # ------------------------------------------------------------------
    op.create_table(
        "mentor_documents",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("status", sa.Enum("pending", "verified", "rejected", name="documentstatus"),
                   nullable=False, server_default="pending", index=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # mentor_availability_slots
    # ------------------------------------------------------------------
    op.create_table(
        "mentor_availability_slots",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("start_time", sa.DateTime(), nullable=False, index=True),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.Enum("available", "booked", "blocked", name="slotstatus"),
                   nullable=False, server_default="available", index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("mentor_id", "start_time", name="uq_mentor_slot_start"),
    )

    # ------------------------------------------------------------------
    # mentorship_requests
    # ------------------------------------------------------------------
    op.create_table(
        "mentorship_requests",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("pending", "accepted", "rejected", "cancelled", name="mentorshiprequeststatus"),
                   nullable=False, server_default="pending", index=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("response_note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # bookings
    # ------------------------------------------------------------------
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("slot_id", sa.Integer(), sa.ForeignKey("mentor_availability_slots.id", ondelete="CASCADE"),
                   nullable=False, unique=True, index=True),
        sa.Column("status", sa.Enum("scheduled", "completed", "cancelled", "no_show", name="bookingstatus"),
                   nullable=False, server_default="scheduled", index=True),
        sa.Column("meeting_link", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("cancellation_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # chats / messages
    # ------------------------------------------------------------------
    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("mentorship_request_id", sa.Integer(),
                   sa.ForeignKey("mentorship_requests.id", ondelete="CASCADE"),
                   nullable=False, unique=True, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("chat_id", sa.Integer(), sa.ForeignKey("chats.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("message_type", sa.Enum("text", "image", "file", name="messagetype"),
                   nullable=False, server_default="text"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("attachment_path", sa.String(length=500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("type", sa.Enum(
            "mentorship_request", "booking", "chat_message", "system", "account", "complaint",
            name="notificationtype",
        ), nullable=False, index=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false(), index=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # ratings
    # ------------------------------------------------------------------
    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="CASCADE"),
                   nullable=False, unique=True, index=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("mentor_id", sa.Integer(), sa.ForeignKey("mentors.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("review", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score_range"),
    )

    # ------------------------------------------------------------------
    # complaints
    # ------------------------------------------------------------------
    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("against_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id"), nullable=True),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("open", "in_review", "resolved", "dismissed", name="complaintstatus"),
                   nullable=False, server_default="open", index=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("resolved_by_admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # otp_verifications
    # ------------------------------------------------------------------
    op.create_table(
        "otp_verifications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                   nullable=True, index=True),
        sa.Column("destination", sa.String(length=150), nullable=False, index=True),
        sa.Column("channel", sa.Enum("email", "sms", name="otpchannel"), nullable=False),
        sa.Column("purpose", sa.Enum(
            "email_verification", "mobile_verification", "password_reset", "login_2fa", name="otppurpose",
        ), nullable=False, index=True),
        sa.Column("hashed_otp", sa.String(length=255), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # captcha_sessions
    # ------------------------------------------------------------------
    op.create_table(
        "captcha_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("session_id", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("hashed_answer", sa.String(length=255), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # audit_logs
    # ------------------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("action", sa.Enum(
            "create", "update", "delete", "login", "logout", "approve", "reject", "block", "unblock", "other",
            name="auditaction",
        ), nullable=False, index=True),
        sa.Column("entity_type", sa.String(length=100), nullable=True, index=True),
        sa.Column("entity_id", sa.Integer(), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ------------------------------------------------------------------
    # refresh_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                   nullable=False, index=True),
        sa.Column("token_hash", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    # Drop in strict reverse-dependency order to satisfy FK constraints.
    op.drop_table("refresh_tokens")
    op.drop_table("audit_logs")
    op.drop_table("captcha_sessions")
    op.drop_table("otp_verifications")
    op.drop_table("complaints")
    op.drop_table("ratings")
    op.drop_table("notifications")
    op.drop_table("messages")
    op.drop_table("chats")
    op.drop_table("bookings")
    op.drop_table("mentorship_requests")
    op.drop_table("mentor_availability_slots")
    op.drop_table("mentor_documents")
    op.drop_table("mentor_fields")
    op.drop_table("mentors")
    op.drop_table("students")
    op.drop_table("fields")
    op.drop_table("categories")
    op.drop_table("users")
    op.drop_table("roles")

    # Drop enum types (PostgreSQL would need this; MySQL stores enums inline so this is a no-op there,
    # but kept for cross-database portability if the project is ever migrated to PostgreSQL).
    for enum_name in [
        "rolename", "userstatus", "mentorapprovalstatus", "documentstatus", "slotstatus",
        "mentorshiprequeststatus", "bookingstatus", "messagetype", "notificationtype",
        "complaintstatus", "otpchannel", "otppurpose", "auditaction",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
