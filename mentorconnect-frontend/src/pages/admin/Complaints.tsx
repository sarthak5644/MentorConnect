import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { MessageCircleWarning } from 'lucide-react';
import { complaintsApi } from '@/api/endpoints';
import { ComplaintStatus } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, Pagination, Select, Modal, Textarea, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDate } from '@/lib/utils';

const statusVariant: Record<ComplaintStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [ComplaintStatus.OPEN]: 'warning',
  [ComplaintStatus.IN_REVIEW]: 'info' as any,
  [ComplaintStatus.RESOLVED]: 'success',
  [ComplaintStatus.DISMISSED]: 'default',
};

export default function AdminComplaints() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<ComplaintStatus | ''>('');
  const [resolveId, setResolveId] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['admin-complaints', page, statusFilter],
    queryFn: () => complaintsApi.listAll({ page, page_size: 10, status: statusFilter || undefined }),
  });

  const resolveMutation = useMutation({
    mutationFn: (status: ComplaintStatus) => complaintsApi.resolve(resolveId!, { status, admin_notes: notes }),
    onSuccess: () => {
      showToast('Complaint updated', 'success');
      qc.invalidateQueries({ queryKey: ['admin-complaints'] });
      setResolveId(null); setNotes('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Complaints</h1>

      <Select className="mt-4 max-w-xs" onChange={(e) => { setStatusFilter(e.target.value as ComplaintStatus | ''); setPage(1); }}>
        <option value="">All statuses</option>
        <option value={ComplaintStatus.OPEN}>Open</option>
        <option value={ComplaintStatus.IN_REVIEW}>In review</option>
        <option value={ComplaintStatus.RESOLVED}>Resolved</option>
        <option value={ComplaintStatus.DISMISSED}>Dismissed</option>
      </Select>

      {!data?.items.length ? (
        <div className="mt-6"><EmptyState icon={MessageCircleWarning} title="No complaints found" /></div>
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {data.items.map((c) => (
              <div key={c.id} className="session-card">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium text-ink-800 dark:text-ink-50">{c.subject}</p>
                    <p className="text-sm text-ink-500 dark:text-ink-300 mt-1">{c.description}</p>
                    <p className="text-xs text-ink-400 mt-1">{formatDate(c.created_at)}</p>
                  </div>
                  <Badge variant={statusVariant[c.status] as any}>{c.status}</Badge>
                </div>
                {c.status === ComplaintStatus.OPEN || c.status === ComplaintStatus.IN_REVIEW ? (
                  <Button size="sm" className="mt-3" onClick={() => setResolveId(c.id)}>Review / resolve</Button>
                ) : c.admin_notes ? (
                  <p className="mt-2 text-xs text-ink-400">Admin notes: {c.admin_notes}</p>
                ) : null}
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}

      <Modal isOpen={!!resolveId} onClose={() => setResolveId(null)} title="Resolve complaint" size="sm">
        <Textarea label="Admin notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
        <div className="mt-4 flex flex-wrap justify-end gap-2">
          <Button variant="secondary" onClick={() => resolveMutation.mutate(ComplaintStatus.IN_REVIEW)}>Mark in review</Button>
          <Button variant="secondary" onClick={() => resolveMutation.mutate(ComplaintStatus.DISMISSED)}>Dismiss</Button>
          <Button onClick={() => resolveMutation.mutate(ComplaintStatus.RESOLVED)} isLoading={resolveMutation.isPending}>Resolve</Button>
        </div>
      </Modal>
    </div>
  );
}