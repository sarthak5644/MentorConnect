import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { UserCheck } from 'lucide-react';
import { adminApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Button, Pagination, Modal, Textarea, useToast, Badge } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { initials } from '@/lib/utils';

export default function AdminMentorApproval() {
  const [page, setPage] = useState(1);
  const [rejectId, setRejectId] = useState<number | null>(null);
  const [reason, setReason] = useState('');
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['pending-mentors', page],
    queryFn: () => adminApi.listPendingMentors({ page, page_size: 10 }),
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => adminApi.approveMentor(id),
    onSuccess: () => {
      showToast('Mentor approved', 'success');
      qc.invalidateQueries({ queryKey: ['pending-mentors'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const rejectMutation = useMutation({
    mutationFn: () => adminApi.rejectMentor(rejectId!, reason),
    onSuccess: () => {
      showToast('Mentor rejected', 'success');
      qc.invalidateQueries({ queryKey: ['pending-mentors'] });
      setRejectId(null);
      setReason('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Mentor approvals</h1>

      {!data?.items.length ? (
        <EmptyState icon={UserCheck} title="No pending approvals" />
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {data.items.map((m) => (
              <div key={m.id} className="session-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-sm font-medium text-accent">
                    {initials(m.designation || `Mentor ${m.id}`)}
                  </div>
                  <div>
                    <p className="font-medium text-ink-800 dark:text-ink-50">Mentor #{m.id} (user #{m.user_id})</p>
                    <p className="text-sm text-ink-400">{m.headline || m.designation || "No headline"}</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {m.expertise_fields.slice(0, 3).map((f) => <Badge key={f.id}>{f.name}</Badge>)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button size="sm" onClick={() => approveMutation.mutate(m.id)}>Approve</Button>
                  <Button size="sm" variant="danger" onClick={() => setRejectId(m.id)}>Reject</Button>
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}

      <Modal isOpen={!!rejectId} onClose={() => setRejectId(null)} title="Reject mentor application" size="sm">
        <Textarea label="Rejection reason" value={reason} onChange={(e) => setReason(e.target.value)} />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setRejectId(null)}>Back</Button>
          <Button variant="danger" isLoading={rejectMutation.isPending} onClick={() => rejectMutation.mutate()}>
            Confirm reject
          </Button>
        </div>
      </Modal>
    </div>
  );
}
