import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Star } from 'lucide-react';
import { mentorsApi, ratingsApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Pagination } from '@/components/ui';
import { formatDate } from '@/lib/utils';

export default function MentorReviews() {
  const [page, setPage] = useState(1);
  const { data: profile, isLoading: profileLoading } = useQuery({ queryKey: ['mentor-profile'], queryFn: mentorsApi.getMyProfile });
  const { data, isLoading } = useQuery({
    queryKey: ['mentor-reviews', profile?.id, page],
    queryFn: () => ratingsApi.listForMentor(profile!.id, { page, page_size: 10 }),
    enabled: !!profile?.id,
  });

  if (profileLoading || isLoading) return <PageSpinner />;

  return (
    <div>
      <div className="flex items-center gap-3">
        <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Reviews</h1>
        <span className="text-sm font-mono text-accent">★ {profile?.average_rating.toFixed(1)} ({profile?.total_ratings})</span>
      </div>

      {!data?.items.length ? (
        <EmptyState icon={Star} title="No reviews yet" />
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