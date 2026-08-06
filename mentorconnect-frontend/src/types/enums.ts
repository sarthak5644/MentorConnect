export enum RoleName {
  SUPER_ADMIN = 'super_admin',
  MENTOR = 'mentor',
  STUDENT = 'student',
}

export enum UserStatus {
  ACTIVE = 'active',
  BLOCKED = 'blocked',
  PENDING = 'pending',
  DEACTIVATED = 'deactivated',
}

export enum MentorApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export enum DocumentStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
}

export enum SlotStatus {
  AVAILABLE = 'available',
  BOOKED = 'booked',
  BLOCKED = 'blocked',
}

export enum MentorshipRequestStatus {
  PENDING = 'pending',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled',
}

export enum BookingStatus {
  SCHEDULED = 'scheduled',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  NO_SHOW = 'no_show',
}

export enum NotificationType {
  MENTORSHIP_REQUEST = 'mentorship_request',
  BOOKING = 'booking',
  CHAT_MESSAGE = 'chat_message',
  SYSTEM = 'system',
  ACCOUNT = 'account',
  COMPLAINT = 'complaint',
}

export enum ComplaintStatus {
  OPEN = 'open',
  IN_REVIEW = 'in_review',
  RESOLVED = 'resolved',
  DISMISSED = 'dismissed',
}

export enum OtpPurpose {
  EMAIL_VERIFICATION = 'email_verification',
  MOBILE_VERIFICATION = 'mobile_verification',
  PASSWORD_RESET = 'password_reset',
  LOGIN_2FA = 'login_2fa',
}

export enum OtpChannel {
  EMAIL = 'email',
  SMS = 'sms',
}

export enum MessageType {
  TEXT = 'text',
  IMAGE = 'image',
  FILE = 'file',
}