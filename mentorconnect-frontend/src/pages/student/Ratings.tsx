import { Star } from 'lucide-react';
import { EmptyState } from '@/components/ui';

// The backend has no endpoint to list a student's own submitted ratings
// (no GET /ratings/me) — only /ratings/mentor/{id}, which lists a mentor's
// reviews. This page can't be built honestly until that endpoint exists;
// showing it here rather than a fake/broken list, and pointing to Bookings
// where rating actually happens.
export default function StudentRatings() {
  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">My reviews</h1>
      <div className="mt-6">
        <EmptyState
          icon={Star}
          title="Not available yet"
          description="The backend doesn't currently expose a list of your own submitted reviews. You can still rate mentors from your Bookings page."
        />
      </div>
    </div>
  );
}
