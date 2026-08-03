"""
app/schemas/dashboard.py
----------------------------
Schemas for the Super Admin dashboard/analytics/reports endpoints.
"""

from typing import List, Dict
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """High-level KPI counters for the admin dashboard landing page."""
    total_users: int
    total_students: int
    total_mentors: int
    pending_mentor_approvals: int
    total_bookings: int
    completed_bookings: int
    total_mentorship_requests: int
    open_complaints: int
    blocked_users: int


class MonthlySignupPoint(BaseModel):
    month: str   # "2026-01"
    students: int
    mentors: int


class TopMentorPoint(BaseModel):
    mentor_id: int
    full_name: str
    average_rating: float
    total_sessions_completed: int


class AnalyticsReport(BaseModel):
    """Aggregated analytics data for charts/reports."""
    signups_by_month: List[MonthlySignupPoint]
    top_mentors: List[TopMentorPoint]
    bookings_by_status: Dict[str, int]
    complaints_by_status: Dict[str, int]
