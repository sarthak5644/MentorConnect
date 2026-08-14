import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CalendarCheck } from 'lucide-react';
import { bookingsApi } from '@/api/endpoints';
import { BookingStatus } from '@/types';
import { PageSpinner, EmptyState, Badge, Button, Pagination, Modal, Textarea, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDateTime } from '@/lib/utils';
import RateBookingModal from '@/components/student/RateBookingModal';

const statusVariant: Record<BookingStatus, 'default' | 'success' | 'warning' | 'danger'> = {
  [BookingStatus.SCHEDULED]: 'warning',
  [BookingStatus.COMPLETED]: 'success',
  [BookingStatus.CANCELLED]: 'danger',
  [BookingStatus.NO_SHOW]: 'default',
};

// The backend has no /ratings/me endpoint, so there's no way to ask "has
// this booking been rated?" from the server. We track it locally instead:
// once a rating succeeds, remember the booking id (in this browser) so the
// Rate button disappears for it. If they rate twice from a different
// device/browser, the backend correctly rejects the second attempt with a
// 409, surfaced as a normal error toast.
const RATED_STORAGE_KEY = 'mc_rated_booking_ids';
function loadRatedIds(): Set<number> {
  try {
    return new Set(JSON.parse(localStorage.getItem(RATED_STORAGE_KEY) ?? '[]'));
  } catch {
    return new Set();
  }
}

export default function StudentBookings() {
  const [page, setPage] = useState(1);
  const [cancelId, setCancelId] = useState<number | null>(null);
  const [cancelReason, setCancelReason] = useState('');
  const [rateBookingId, setRateBookingId] = useState<number | null>(null);
  const [ratedIds, setRatedIds] = useState<Set<number>>(loadRatedIds);
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['bookings', page],
    queryFn: () => bookingsApi.listMine({ page, page_size: 10 }),
  });

  const cancelMutation = useMutation({
    mutationFn: () => bookingsApi.cancel(cancelId!, { cancellation_reason: cancelReason }),
    onSuccess: () => {
      showToast('Booking cancelled', 'success');
      qc.invalidateQueries({ queryKey: ['bookings'] });
      setCancelId(null);
      setCancelReason('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">My bookings</h1>

      {!data?.items.length ? (
        <EmptyState icon={CalendarCheck} title="No bookings yet" description="Book a session with a mentor to see it here." />
      ) : (
        <>
          <div className="mt-6 space-y-3">
            {data.items.map((b) => (
              <div key={b.id} className="session-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-ink-800 dark:text-ink-50">{formatDateTime(b.slot.start_time)}</p>
                  {b.notes && <p className="text-sm text-ink-400 mt-0.5">{b.notes}</p>}
                  {b.meeting_link && (
                    <a href={b.meeting_link} target="_blank" rel="noreferrer" className="text-sm text-accent hover:underline">
                      Join meeting
                    </a>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={statusVariant[b.status]}>{b.status}</Badge>
                  {b.status === BookingStatus.SCHEDULED && (
                    <Button size="sm" variant="danger" onClick={() => setCancelId(b.id)}>Cancel</Button>
                  )}
                  {b.status === BookingStatus.COMPLETED && !ratedIds.has(b.id) && (
                    <Button size="sm" onClick={() => setRateBookingId(b.id)}>Rate</Button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}

      <Modal isOpen={!!cancelId} onClose={() => setCancelId(null)} title="Cancel booking" size="sm">
        <Textarea
          label="Reason for cancellation"
          value={cancelReason}
          onChange={(e) => setCancelReason(e.target.value)}
        />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setCancelId(null)}>Back</Button>
          <Button variant="danger" isLoading={cancelMutation.isPending} onClick={() => cancelMutation.mutate()}>
            Confirm cancel
          </Button>
        </div>
      </Modal>

      <RateBookingModal
        bookingId={rateBookingId}
        onClose={() => setRateBookingId(null)}
        onSuccess={() => {
          if (rateBookingId != null) {
            const next = new Set(ratedIds).add(rateBookingId);
            setRatedIds(next);
            localStorage.setItem(RATED_STORAGE_KEY, JSON.stringify([...next]));
          }
          qc.invalidateQueries({ queryKey: ['bookings'] });
        }}
      />
    </div>
  );
}
