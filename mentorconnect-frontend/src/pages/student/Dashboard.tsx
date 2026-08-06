import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ClipboardList, CalendarCheck, Bell, MessageSquare, Search } from 'lucide-react';
import { dashboardApi } from '@/api/endpoints';
import { PageSpinner, Card } from '@/components/ui';
import { useAuth } from '@/context/AuthContext';

export default function StudentDashboard() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({ queryKey: ['student-dashboard'], queryFn: dashboardApi.getStudentDashboard });

  if (isLoading) return <PageSpinner />;

  const stats = [
    { label: 'Active requests', value: data?.active_requests ?? 0, icon: ClipboardList, to: '/student/requests' },
    { label: 'Upcoming bookings', value: data?.upcoming_bookings ?? 0, icon: CalendarCheck, to: '/student/bookings' },
    { label: 'Unread messages', value: data?.unread_messages ?? 0, icon: MessageSquare, to: '/student/chat' },
    { label: 'Notifications', value: data?.unread_notifications ?? 0, icon: Bell, to: '/student/notifications' },
  ];

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">
        Welcome back, {user?.full_name.split(' ')[0]}
      </h1>
      <p className="mt-1 text-ink-500 dark:text-ink-300">Here's what's happening with your mentorship journey.</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon, to }) => (
          <Link key={label} to={to}>
            <Card>
              <Icon className="h-5 w-5 text-accent" />
              <p className="mt-3 font-mono text-2xl font-semibold text-ink-800 dark:text-ink-50">{value}</p>
              <p className="text-sm text-ink-500 dark:text-ink-300">{label}</p>
            </Card>
          </Link>
        ))}
      </div>

      <Link to="/student/search" className="mt-8 session-card flex items-center gap-4 hover:border-accent">
        <Search className="h-6 w-6 text-accent" />
        <div>
          <p className="font-medium text-ink-800 dark:text-ink-50">Looking for guidance?</p>
          <p className="text-sm text-ink-500 dark:text-ink-300">Search verified mentors by field, rating, and price.</p>
        </div>
      </Link>
    </div>
  );
}