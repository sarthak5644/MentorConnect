import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ClipboardList, CalendarCheck, Bell, Star, Users } from 'lucide-react';
import { dashboardApi } from '@/api/endpoints';
import { PageSpinner, Card } from '@/components/ui';
import { useAuth } from '@/context/AuthContext';

export default function MentorDashboard() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({ queryKey: ['mentor-dashboard'], queryFn: dashboardApi.getMentorDashboard });

  if (isLoading) return <PageSpinner />;

  const stats = [
    { label: 'Pending requests', value: data?.pending_requests ?? 0, icon: ClipboardList, to: '/mentor/requests' },
    { label: 'Upcoming bookings', value: data?.upcoming_bookings ?? 0, icon: CalendarCheck, to: '/mentor/availability' },
    { label: 'Students mentored', value: data?.total_students_mentored ?? 0, icon: Users, to: '/mentor/reviews' },
    { label: 'Average rating', value: (data?.average_rating ?? 0).toFixed(1), icon: Star, to: '/mentor/reviews' },
  ];

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">
        Welcome back, {user?.full_name.split(' ')[0]}
      </h1>
      <p className="mt-1 text-ink-500 dark:text-ink-300">Here's your mentorship activity at a glance.</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon, to }) => (
          <Link key={label} to={to}>
            <Card>
              <Icon className="h-5 w-5 text-mentor" />
              <p className="mt-3 font-mono text-2xl font-semibold text-ink-800 dark:text-ink-50">{value}</p>
              <p className="text-sm text-ink-500 dark:text-ink-300">{label}</p>
            </Card>
          </Link>
        ))}
      </div>

      <Link to="/mentor/notifications" className="mt-8 session-card flex items-center gap-4 hover:border-mentor">
        <Bell className="h-6 w-6 text-mentor" />
        <div>
          <p className="font-medium text-ink-800 dark:text-ink-50">{data?.unread_notifications ?? 0} unread notifications</p>
          <p className="text-sm text-ink-500 dark:text-ink-300">Stay on top of requests and messages.</p>
        </div>
      </Link>
    </div>
  );
}