import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Users, Search } from 'lucide-react';
import { adminApi } from '@/api/endpoints';
import { UserStatus } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, Pagination, Modal, Textarea, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { debounce, initials, formatDate } from '@/lib/utils';

const statusVariant: Record<UserStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [UserStatus.ACTIVE]: 'success',
  [UserStatus.BLOCKED]: 'danger',
  [UserStatus.PENDING]: 'warning',
  [UserStatus.DEACTIVATED]: 'default',
};

export default function AdminStudentManagement() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [blockId, setBlockId] = useState<number | null>(null);
  const [reason, setReason] = useState('');
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['admin-students', page, search],
    queryFn: () => adminApi.listStudents({ page, page_size: 12, search }),
  });

  const blockMutation = useMutation({
    mutationFn: () => adminApi.blockUser(blockId!, reason),
    onSuccess: () => {
      showToast('Student blocked', 'success');
      qc.invalidateQueries({ queryKey: ['admin-students'] });
      setBlockId(null); setReason('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const unblockMutation = useMutation({
    mutationFn: (id: number) => adminApi.unblockUser(id),
    onSuccess: () => {
      showToast('Student unblocked', 'success');
      qc.invalidateQueries({ queryKey: ['admin-students'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const onSearch = debounce((v: string) => { setSearch(v); setPage(1); }, 400);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Students</h1>

      <div className="mt-4 relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-300" />
        <input className="input-field pl-9" placeholder="Search students..." onChange={(e) => onSearch(e.target.value)} />
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : !data?.items.length ? (
        <div className="mt-6"><EmptyState icon={Users} title="No students found" /></div>
      ) : (
        <>
          <div className="mt-6 space-y-2">
            {data.items.map((u) => (
              <div key={u.id} className="session-card flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/10 text-xs font-medium text-accent">
                    {initials(u.full_name)}
                  </div>
                  <div>
                    <p className="font-medium text-ink-800 dark:text-ink-50">{u.full_name}</p>
                    <p className="text-xs text-ink-400">{u.email} · joined {formatDate(u.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={statusVariant[u.status]}>{u.status}</Badge>
                  {u.status === UserStatus.BLOCKED ? (
                    <Button size="sm" onClick={() => unblockMutation.mutate(u.id)}>Unblock</Button>
                  ) : (
                    <Button size="sm" variant="danger" onClick={() => setBlockId(u.id)}>Block</Button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}

      <Modal isOpen={!!blockId} onClose={() => setBlockId(null)} title="Block student" size="sm">
        <Textarea label="Reason" value={reason} onChange={(e) => setReason(e.target.value)} />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setBlockId(null)}>Back</Button>
          <Button variant="danger" isLoading={blockMutation.isPending} onClick={() => blockMutation.mutate()}>Confirm block</Button>
        </div>
      </Modal>
    </div>
  );
}