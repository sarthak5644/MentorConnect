import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ScrollText } from 'lucide-react';
import { adminApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Badge, Pagination, Input } from '@/components/ui';
import { debounce, formatDateTime } from '@/lib/utils';

export default function AdminAuditLogs() {
  const [page, setPage] = useState(1);
  const [action, setAction] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs', page, action],
    queryFn: () => adminApi.listAuditLogs({ page, page_size: 20, action: action || undefined }),
  });

  const onFilter = debounce((v: string) => { setAction(v); setPage(1); }, 400);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Audit logs</h1>
      <Input className="mt-4 max-w-xs" placeholder="Filter by action..." onChange={(e) => onFilter(e.target.value)} />

      {isLoading ? (
        <PageSpinner />
      ) : !data?.items.length ? (
        <div className="mt-6"><EmptyState icon={ScrollText} title="No audit logs found" /></div>
      ) : (
        <>
          <div className="mt-6 overflow-x-auto rounded-xl border border-ink-100 dark:border-ink-700">
            <table className="w-full text-sm">
              <thead className="bg-ink-50 dark:bg-ink-700 text-left text-ink-500 dark:text-ink-300">
                <tr>
                  <th className="px-4 py-2 font-medium">Action</th>
                  <th className="px-4 py-2 font-medium">Entity</th>
                  <th className="px-4 py-2 font-medium">Description</th>
                  <th className="px-4 py-2 font-medium">IP</th>
                  <th className="px-4 py-2 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((log) => (
                  <tr key={log.id} className="border-t border-ink-100 dark:border-ink-700">
                    <td className="px-4 py-2"><Badge>{log.action}</Badge></td>
                    <td className="px-4 py-2 font-mono text-xs text-ink-500">
                      {log.entity_type ? `${log.entity_type}#${log.entity_id}` : '—'}
                    </td>
                    <td className="px-4 py-2 text-ink-600 dark:text-ink-300">{log.description || '—'}</td>
                    <td className="px-4 py-2 font-mono text-xs text-ink-400">{log.ip_address || '—'}</td>
                    <td className="px-4 py-2 text-xs text-ink-400">{formatDateTime(log.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}