import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { PageSpinner } from '@/components/ui';
import PublicLayout from '@/components/layout/PublicLayout';
import DashboardLayout from '@/components/layout/DashboardLayout';
import ProtectedRoute from '@/routes/ProtectedRoute';
import PublicOnlyRoute from '@/routes/PublicOnlyRoute';
import { RoleName } from '@/types';
import { studentSidebarItems } from '@/components/layout/StudentSidebarItems';
import { mentorSidebarItems } from '@/components/layout/MentorSidebarItems';
import { adminSidebarItems } from '@/components/layout/AdminSidebarItems';

// Public pages
const Home = lazy(() => import('@/pages/public/Home'));
const About = lazy(() => import('@/pages/public/About'));
const MentorListing = lazy(() => import('@/pages/public/MentorListing'));
const MentorProfilePublic = lazy(() => import('@/pages/public/MentorProfilePublic'));
const Contact = lazy(() => import('@/pages/public/Contact'));

// Auth pages
const Login = lazy(() => import('@/pages/auth/Login'));
const Register = lazy(() => import('@/pages/auth/Register'));
const ForgotPassword = lazy(() => import('@/pages/auth/ForgotPassword'));
const ResetPassword = lazy(() => import('@/pages/auth/ResetPassword'));
const Unauthorized = lazy(() => import('@/pages/Unauthorized'));
const NotFound = lazy(() => import('@/pages/NotFound'));

// Student pages
const StudentDashboard = lazy(() => import('@/pages/student/Dashboard'));
const StudentSearchMentors = lazy(() => import('@/pages/student/SearchMentors'));
const StudentBookMentor = lazy(() => import('@/pages/student/BookMentor'));
const StudentRequests = lazy(() => import('@/pages/student/MyRequests'));
const StudentBookings = lazy(() => import('@/pages/student/Bookings'));
const StudentChat = lazy(() => import('@/pages/student/Chat'));
const StudentNotifications = lazy(() => import('@/pages/student/Notifications'));
const StudentRatings = lazy(() => import('@/pages/student/Ratings'));
const StudentProfile = lazy(() => import('@/pages/student/Profile'));

// Mentor pages
const MentorDashboard = lazy(() => import('@/pages/mentor/Dashboard'));
const MentorProfile = lazy(() => import('@/pages/mentor/Profile'));
const MentorQualifications = lazy(() => import('@/pages/mentor/Qualifications'));
const MentorAchievements = lazy(() => import('@/pages/mentor/Achievements'));
const MentorDocuments = lazy(() => import('@/pages/mentor/Documents'));
const MentorAvailability = lazy(() => import('@/pages/mentor/Availability'));
const MentorRequests = lazy(() => import('@/pages/mentor/MentorshipRequests'));
const MentorChat = lazy(() => import('@/pages/mentor/Chat'));
const MentorNotifications = lazy(() => import('@/pages/mentor/Notifications'));
const MentorReviews = lazy(() => import('@/pages/mentor/Reviews'));

// Admin pages
const AdminAnalytics = lazy(() => import('@/pages/admin/Analytics'));
const AdminMentorApproval = lazy(() => import('@/pages/admin/MentorApproval'));
const AdminStudents = lazy(() => import('@/pages/admin/StudentManagement'));
const AdminMentors = lazy(() => import('@/pages/admin/MentorManagement'));
const AdminCategories = lazy(() => import('@/pages/admin/Categories'));
const AdminReports = lazy(() => import('@/pages/admin/Reports'));
const AdminComplaints = lazy(() => import('@/pages/admin/Complaints'));
const AdminNotifications = lazy(() => import('@/pages/admin/Notifications'));
const AdminAuditLogs = lazy(() => import('@/pages/admin/AuditLogs'));

export default function App() {
  return (
    <Suspense fallback={<PageSpinner />}>
      <Routes>
        {/* Public */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/mentors" element={<MentorListing />} />
          <Route path="/mentors/:id" element={<MentorProfilePublic />} />
          <Route path="/contact" element={<Contact />} />

          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
          </Route>

          <Route path="/unauthorized" element={<Unauthorized />} />
        </Route>

        {/* Student */}
        <Route element={<ProtectedRoute allowedRoles={[RoleName.STUDENT]} />}>
          <Route element={<DashboardLayout items={studentSidebarItems} />}>
            <Route path="/student/dashboard" element={<StudentDashboard />} />
            <Route path="/student/search" element={<StudentSearchMentors />} />
            <Route path="/student/book/:mentorId" element={<StudentBookMentor />} />
            <Route path="/student/requests" element={<StudentRequests />} />
            <Route path="/student/bookings" element={<StudentBookings />} />
            <Route path="/student/chat" element={<StudentChat />} />
            <Route path="/student/chat/:chatId" element={<StudentChat />} />
            <Route path="/student/notifications" element={<StudentNotifications />} />
            <Route path="/student/ratings" element={<StudentRatings />} />
            <Route path="/student/profile" element={<StudentProfile />} />
          </Route>
        </Route>

        {/* Mentor */}
        <Route element={<ProtectedRoute allowedRoles={[RoleName.MENTOR]} />}>
          <Route element={<DashboardLayout items={mentorSidebarItems} />}>
            <Route path="/mentor/dashboard" element={<MentorDashboard />} />
            <Route path="/mentor/profile" element={<MentorProfile />} />
            <Route path="/mentor/qualifications" element={<MentorQualifications />} />
            <Route path="/mentor/achievements" element={<MentorAchievements />} />
            <Route path="/mentor/documents" element={<MentorDocuments />} />
            <Route path="/mentor/availability" element={<MentorAvailability />} />
            <Route path="/mentor/requests" element={<MentorRequests />} />
            <Route path="/mentor/chat" element={<MentorChat />} />
            <Route path="/mentor/chat/:chatId" element={<MentorChat />} />
            <Route path="/mentor/notifications" element={<MentorNotifications />} />
            <Route path="/mentor/reviews" element={<MentorReviews />} />
          </Route>
        </Route>

        {/* Admin */}
        <Route element={<ProtectedRoute allowedRoles={[RoleName.SUPER_ADMIN]} />}>
          <Route element={<DashboardLayout items={adminSidebarItems} />}>
            <Route path="/admin/analytics" element={<AdminAnalytics />} />
            <Route path="/admin/mentor-approval" element={<AdminMentorApproval />} />
            <Route path="/admin/students" element={<AdminStudents />} />
            <Route path="/admin/mentors" element={<AdminMentors />} />
            <Route path="/admin/categories" element={<AdminCategories />} />
            <Route path="/admin/reports" element={<AdminReports />} />
            <Route path="/admin/complaints" element={<AdminComplaints />} />
            <Route path="/admin/notifications" element={<AdminNotifications />} />
            <Route path="/admin/audit-logs" element={<AdminAuditLogs />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}