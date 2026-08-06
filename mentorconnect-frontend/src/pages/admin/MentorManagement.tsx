import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Briefcase, Search } from 'lucide-react';
import { adminApi } from '@/api/endpoints';
import { MentorApprovalStatus, UserStatus } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, Pagination, Select, Modal, Textarea, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { debounce, initials } from '@/lib/utils';

const approvalVariant: Record<MentorApprovalStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [MentorApprovalStatus.PENDING]: 'warning',
  [MentorApprovalStatus.APPROVED]: 'success',
  [MentorApprovalStatus.REJECTED]: 'danger',
};

export default function AdminMentorManagement() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [approvalFilter, setApprovalFilter] = useState<MentorApprovalStatus | ''>('');
  const [blockId, setBlockId] = useState<number | null>(null);
  const [reason, setReason] = useState('');
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['admin-mentors', page, search, approvalFilter],
    queryFn: () => adminApi.listMentors({ page, page_size: 12, search, approval_status: approvalFilter || undefined }),
  });

  const blockMutation = useMutation({
    mutationFn: () => adminApi.blockUser(blockId!, reason),
    onSuccess: () => {
      showToast('Mentor blocked', 'success');
      qc.invalidateQueries({ queryKey: ['admin-mentors'] });
      setBlockId(null); setReason('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const unblockMutation = useMutation({
    mutationFn: (userId: number) => adminApi.unblockUser(userId),
    onSuccess: () => {
      showToast('Mentor unblocked', 'success');
      qc.invalidateQueries({ queryKey: ['admin-mentors'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const onSearch = debounce((v: string) => { setSearch(v); setPage(1); }, 400);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Mentors</h1>

      <div className="mt-4 flex flex-wrap gap-3">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-300" />
          <input className="input-field pl-9" placeholder="Search mentors..." onChange={(e) => onSearch(e.target.value)} />
        </div>
        <Select className="max-w-xs" onChange={(e) => { setApprovalFilter(e.target.value as MentorApprovalStatus | ''); setPage(1); }}>
          <option value="">All statuses</option>
          <option value={MentorApprovalStatus.PENDING}>Pending</option>
          <option value={MentorApprovalStatus.APPROVED}>Approved</option>
          <option value={MentorApprovalStatus.REJECTED}>Rejected</option>
        </Select>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : !data?.items.length ? (
        <div className="mt-6"><EmptyState icon={Briefcase} title="No mentors found" /></div>
      ) : (
        <>
          <div className="mt-6 space-y-2">
            {data.items.map((m) => (
              <div key={m.id} className="session-card flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/10 text-xs font-medium text-accent">
                    {initials(m.user.full_name)}
                  </div>
                  <div>
                    <p className="font-medium text-ink-800 dark:text-ink-50">{m.user.full_name}</p>
                    <p className="text-xs text-ink-400">{m.user.email} · ★ {m.average_rating.toFixed(1)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={approvalVariant[m.approval_status]}>{m.approval_status}</Badge>
                  {m.user.status === UserStatus.BLOCKED ? (
                    <Button size="sm" onClick={() => unblockMutation.mutate(m.user.id)}>Unblock</Button>
                  ) : (
                    <Button size="sm" variant="danger" onClick={() => setBlockId(m.user.id)}>Block</Button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}

      <Modal isOpen={!!blockId} onClose={() => setBlockId(null)} title="Block mentor" size="sm">
        <Textarea label="Reason" value={reason} onChange={(e) => setReason(e.target.value)} />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setBlockId(null)}>Back</Button>
          <Button variant="danger" isLoading={blockMutation.isPending} onClick={() => blockMutation.mutate()}>Confirm block</Button>
        </div>
      </Modal>
    </div>
  );
}