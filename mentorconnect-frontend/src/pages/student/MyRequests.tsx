import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ClipboardList } from 'lucide-react';
import { mentorshipRequestsApi } from '@/api/endpoints';
import { MentorshipRequestStatus } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, Pagination, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDate, initials } from '@/lib/utils';

const statusVariant: Record<MentorshipRequestStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [MentorshipRequestStatus.PENDING]: 'warning',
  [MentorshipRequestStatus.ACCEPTED]: 'success',
  [MentorshipRequestStatus.REJECTED]: 'danger',
  [MentorshipRequestStatus.CANCELLED]: 'default',
};

export default function StudentMyRequests() {
  const [page, setPage] = useState(1);
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['mentorship-requests', page],
    queryFn: () => mentorshipRequestsApi.listMine({ page, page_size: 10 }),
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => mentorshipRequestsApi.cancel(id),
    onSuccess: () => {
      showToast('Request cancelled', 'success');
      qc.invalidateQueries({ queryKey: ['mentorship-requests'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">My requests</h1>

      {!data?.items.length ? (
        <EmptyState icon={ClipboardList} title="No requests yet" description="Requests you send to mentors will appear here." />
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {data.items.map((r) => (
              <div key={r.id} className="session-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-sm font-medium text-accent">
                    {initials(r.mentor.designation || r.mentor.headline || 'Mentor')}
                  </div>
                  <div>
                    <p className="font-medium text-ink-800 dark:text-ink-50">{r.mentor.designation || r.mentor.headline || `Mentor #${r.mentor.id}`}</p>
                    <p className="text-sm text-ink-400 line-clamp-1">{r.message}</p>
                    <p className="text-xs text-ink-400 mt-0.5">{formatDate(r.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
                  {r.status === MentorshipRequestStatus.PENDING && (
                    <Button size="sm" variant="danger" onClick={() => cancelMutation.mutate(r.id)}>Cancel</Button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
