import { useQuery } from '@tanstack/react-query';
import { Users, Briefcase, UserCheck, CalendarCheck, CheckCircle2, Flag, TrendingUp } from 'lucide-react';
import { adminApi } from '@/api/endpoints';
import { PageSpinner, Card } from '@/components/ui';

export default function AdminAnalytics() {
  const { data, isLoading } = useQuery({ queryKey: ['admin-analytics'], queryFn: adminApi.getAnalytics });
  if (isLoading) return <PageSpinner />;

  const stats = [
    { label: 'Total students', value: data?.total_students ?? 0, icon: Users },
    { label: 'Total mentors', value: data?.total_mentors ?? 0, icon: Briefcase },
    { label: 'Pending approvals', value: data?.pending_mentor_approvals ?? 0, icon: UserCheck },
    { label: 'Total bookings', value: data?.total_bookings ?? 0, icon: CalendarCheck },
    { label: 'Completed sessions', value: data?.total_completed_sessions ?? 0, icon: CheckCircle2 },
    { label: 'Open complaints', value: data?.open_complaints ?? 0, icon: Flag },
    { label: 'New users (30d)', value: data?.new_users_last_30_days ?? 0, icon: TrendingUp },
  ];

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Analytics</h1>
      <p className="mt-1 text-ink-500 dark:text-ink-300">Platform-wide overview.</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <Icon className="h-5 w-5 text-accent" />
            <p className="mt-3 font-mono text-2xl font-semibold text-ink-800 dark:text-ink-50">{value}</p>
            <p className="text-sm text-ink-500 dark:text-ink-300">{label}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}