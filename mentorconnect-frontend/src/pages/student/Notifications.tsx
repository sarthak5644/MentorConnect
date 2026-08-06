import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell } from 'lucide-react';
import { notificationsApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Badge, Button, Pagination } from '@/components/ui';
import { formatDateTime, cn } from '@/lib/utils';

export default function StudentNotifications() {
  const [page, setPage] = useState(1);
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', page],
    queryFn: () => notificationsApi.list({ page, page_size: 15 }),
  });

  const markReadMutation = useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const markAllMutation = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Notifications</h1>
        <Button size="sm" variant="secondary" onClick={() => markAllMutation.mutate()}>Mark all read</Button>
      </div>

      {!data?.items.length ? (
        <EmptyState icon={Bell} title="No notifications" />
      ) : (
        <>
          <div className="mt-6 space-y-2">
            {data.items.map((n) => (
              <button
                key={n.id}
                onClick={() => !n.is_read && markReadMutation.mutate(n.id)}
                className={cn(
                  'w-full text-left session-card flex items-start justify-between gap-3',
                  !n.is_read && 'border-accent/40 bg-accent/5'
                )}
              >
                <div>
                  <p className="font-medium text-ink-800 dark:text-ink-50">{n.title}</p>
                  {n.body && <p className="text-sm text-ink-500 dark:text-ink-300 mt-0.5">{n.body}</p>}
                  <p className="text-xs text-ink-400 mt-1">{formatDateTime(n.created_at)}</p>
                </div>
                {!n.is_read && <Badge variant="info">new</Badge>}
              </button>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}