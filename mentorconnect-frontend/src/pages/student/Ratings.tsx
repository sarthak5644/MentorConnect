import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Star } from 'lucide-react';
import { ratingsApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Pagination } from '@/components/ui';
import { formatDate } from '@/lib/utils';

export default function StudentRatings() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useQuery({
    queryKey: ['my-ratings', page],
    queryFn: () => ratingsApi.listMine({ page, page_size: 10 }),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">My reviews</h1>

      {!data?.items.length ? (
        <EmptyState icon={Star} title="No reviews yet" description="Reviews you leave for mentors will appear here." />
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {data.items.map((r) => (
              <div key={r.id} className="session-card">
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className={`h-4 w-4 ${i < r.score ? 'text-accent fill-accent' : 'text-ink-200'}`} />
                  ))}
                  <span className="ml-2 text-xs text-ink-400">{formatDate(r.created_at)}</span>
                </div>
                {r.review && <p className="mt-2 text-sm text-ink-600 dark:text-ink-300">{r.review}</p>}
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}