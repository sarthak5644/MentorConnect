import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ClipboardList } from 'lucide-react';
import { mentorshipRequestsApi } from '@/api/endpoints';
import { MentorshipRequestStatus } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, Pagination, Modal, Textarea, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDate, initials } from '@/lib/utils';

const statusVariant: Record<MentorshipRequestStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [MentorshipRequestStatus.PENDING]: 'warning',
  [MentorshipRequestStatus.ACCEPTED]: 'success',
  [MentorshipRequestStatus.REJECTED]: 'danger',
  [MentorshipRequestStatus.CANCELLED]: 'default',
};

export default function MentorMentorshipRequests() {
  const [page, setPage] = useState(1);
  const [rejectId, setRejectId] = useState<number | null>(null);
  const [reason, setReason] = useState('');
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['mentor-requests', page],
    queryFn: () => mentorshipRequestsApi.listMine({ page, page_size: 10 }),
  });

  const respondMutation = useMutation({
    mutationFn: ({ id, status, note }: { id: number; status: MentorshipRequestStatus.ACCEPTED | MentorshipRequestStatus.REJECTED; note?: string }) =>
      mentorshipRequestsApi.respond(id, { status, response_note: note }),
    onSuccess: () => {
      showToast('Request updated', 'success');
      qc.invalidateQueries({ queryKey: ['mentor-requests'] });
      setRejectId(null);
      setReason('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Mentorship requests</h1>

      {!data?.items.length ? (
        <EmptyState icon={ClipboardList} title="No requests yet" />
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {data.items.map((r) => (
              <div key={r.id} className="session-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-mentor/10 text-sm font-medium text-mentor">
                    {initials(r.student.user.full_name)}
                  </div>
                  <div>
                    <p className="font-medium text-ink-800 dark:text-ink-50">{r.student.user.full_name}</p>
                    <p className="text-sm text-ink-400 line-clamp-1">{r.message}</p>
                    <p className="text-xs text-ink-400 mt-0.5">{formatDate(r.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
                  {r.status === MentorshipRequestStatus.PENDING && (
                    <>
                      <Button size="sm" onClick={() => respondMutation.mutate({ id: r.id, status: MentorshipRequestStatus.ACCEPTED })}>
                        Accept
                      </Button>
                      <Button size="sm" variant="danger" onClick={() => setRejectId(r.id)}>Reject</Button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}

      <Modal isOpen={!!rejectId} onClose={() => setRejectId(null)} title="Reject request" size="sm">
        <Textarea label="Reason (optional)" value={reason} onChange={(e) => setReason(e.target.value)} />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setRejectId(null)}>Back</Button>
          <Button
            variant="danger"
            isLoading={respondMutation.isPending}
            onClick={() => respondMutation.mutate({ id: rejectId!, status: MentorshipRequestStatus.REJECTED, note: reason })}
          >
            Confirm reject
          </Button>
        </div>
      </Modal>
    </div>
  );
}