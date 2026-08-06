import { useQuery } from '@tanstack/react-query';
import { Flag } from 'lucide-react';
import { adminApi } from '@/api/endpoints';
import { PageSpinner, Card } from '@/components/ui';

export default function AdminReports() {
  const { data, isLoading } = useQuery({ queryKey: ['admin-analytics'], queryFn: adminApi.getAnalytics });
  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Reports</h1>
      <p className="mt-1 text-ink-500 dark:text-ink-300">Summary metrics for platform activity.</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Card>
          <Flag className="h-5 w-5 text-accent" />
          <p className="mt-3 font-mono text-2xl font-semibold text-ink-800 dark:text-ink-50">
            {data?.total_completed_sessions ?? 0}
          </p>
          <p className="text-sm text-ink-500 dark:text-ink-300">Completed mentorship sessions</p>
        </Card>
        <Card>
          <Flag className="h-5 w-5 text-accent" />
          <p className="mt-3 font-mono text-2xl font-semibold text-ink-800 dark:text-ink-50">
            {data?.open_complaints ?? 0}
          </p>
          <p className="text-sm text-ink-500 dark:text-ink-300">Open complaints requiring review</p>
        </Card>
      </div>
      <p className="mt-6 text-sm text-ink-400">
        This view uses the shared analytics endpoint. A dedicated reports/export endpoint isn't defined in the
        current API contract — connect one when available for CSV/PDF exports.
      </p>
    </div>
  );
}