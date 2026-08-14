import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Star } from 'lucide-react';
import { mentorsApi, ratingsApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Button } from '@/components/ui';
import { formatDate } from '@/lib/utils';
import { Rating } from '@/types';

const PAGE_SIZE = 10;

// Backend's /ratings/mentor/{id} returns a plain array (no total/total_pages),
// so we can't build page-number pagination — a simple "load more" that keeps
// fetching until a short page comes back is the closest honest equivalent.
export default function MentorReviews() {
  const [page, setPage] = useState(1);
  const [allRatings, setAllRatings] = useState<Rating[]>([]);
  const { data: profileData, isLoading: profileLoading } = useQuery({ queryKey: ['mentor-profile'], queryFn: mentorsApi.getMyProfile });
  const profile = profileData?.profile;

  const { data: ratings, isLoading, isFetching } = useQuery({
    queryKey: ['mentor-reviews', profile?.id, page],
    queryFn: () => ratingsApi.listForMentor(profile!.id, { page, page_size: PAGE_SIZE }),
    enabled: !!profile?.id,
  });

  useEffect(() => {
    if (!ratings) return;
    setAllRatings((prev) => (page === 1 ? ratings : [...prev, ...ratings]));
  }, [ratings, page]);

  if (profileLoading || (isLoading && page === 1)) return <PageSpinner />;

  const hasMore = (ratings?.length ?? 0) >= PAGE_SIZE;

  return (
    <div>
      <div className="flex items-center gap-3">
        <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Reviews</h1>
        <span className="text-sm font-mono text-accent">★ {profile?.average_rating.toFixed(1)} ({profile?.total_ratings})</span>
      </div>

      {!allRatings.length ? (
        <EmptyState icon={Star} title="No reviews yet" />
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {allRatings.map((r) => (
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
          {hasMore && (
            <Button className="mt-4" variant="secondary" isLoading={isFetching} onClick={() => setPage((p) => p + 1)}>
              Load more
            </Button>
          )}
        </>
      )}
    </div>
  );
}
