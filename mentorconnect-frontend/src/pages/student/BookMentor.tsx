import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CalendarClock } from 'lucide-react';
import { mentorsApi, availabilityApi, bookingsApi, mentorshipRequestsApi } from '@/api/endpoints';
import { SlotStatus } from '@/types';
import { PageSpinner, Button, Textarea, EmptyState, useToast, Badge } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDateTime, initials } from '@/lib/utils';

export default function StudentBookMentor() {
  const { mentorId } = useParams<{ mentorId: string }>();
  const id = Number(mentorId);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const qc = useQueryClient();

  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const [requestMessage, setRequestMessage] = useState('');

  const { data: mentor, isLoading: mentorLoading } = useQuery({
    queryKey: ['mentor', id],
    queryFn: () => mentorsApi.getById(id),
    enabled: !!id,
  });

  const { data: slots, isLoading: slotsLoading } = useQuery({
    queryKey: ['mentor-slots', id],
    queryFn: () => availabilityApi.listMentorSlots(id),
    enabled: !!id,
  });

  const requestMutation = useMutation({
    mutationFn: () => mentorshipRequestsApi.create({ mentor_id: id, message: requestMessage }),
    onSuccess: () => {
      showToast('Mentorship request sent!', 'success');
      qc.invalidateQueries({ queryKey: ['mentorship-requests'] });
      navigate('/student/requests');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const bookMutation = useMutation({
    mutationFn: () => {
      if (!selectedSlotId) throw new Error('Select a slot first');
      return bookingsApi.create({ slot_id: selectedSlotId, notes });
    },
    onSuccess: () => {
      showToast('Booking confirmed!', 'success');
      qc.invalidateQueries({ queryKey: ['bookings'] });
      navigate('/student/bookings');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (mentorLoading || slotsLoading) return <PageSpinner />;
  if (!mentor) return <EmptyState icon={CalendarClock} title="Mentor not found" />;

  const availableSlots = (slots ?? []).filter((s) => s.status === SlotStatus.AVAILABLE);

  return (
    <div className="max-w-3xl">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 text-lg font-medium text-accent">
          {initials(mentor.designation || mentor.headline || 'Mentor')}
        </div>
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">{mentor.designation || mentor.headline || `Mentor #${mentor.id}`}</h1>
          <p className="text-sm text-ink-500 dark:text-ink-300">{mentor.headline}</p>
        </div>
      </div>

      <div className="mt-8 session-card">
        <h2 className="font-display text-lg font-medium text-ink-800 dark:text-ink-50 mb-2">1. Send a mentorship request</h2>
        <p className="text-sm text-ink-500 dark:text-ink-300 mb-3">
          Introduce yourself and your goals. The mentor must accept before you can book a session.
        </p>
        <Textarea
          placeholder="Hi! I'm looking for guidance on..."
          value={requestMessage}
          onChange={(e) => setRequestMessage(e.target.value)}
        />
        <Button className="mt-3" onClick={() => requestMutation.mutate()} isLoading={requestMutation.isPending}>
          Send request
        </Button>
      </div>

      <div className="mt-6 session-card">
        <h2 className="font-display text-lg font-medium text-ink-800 dark:text-ink-50 mb-3">2. Or book an open slot directly</h2>
        {!availableSlots.length ? (
          <p className="text-sm text-ink-400">No open slots right now. Try sending a request instead.</p>
        ) : (
          <div className="grid gap-2 sm:grid-cols-2">
            {availableSlots.map((slot) => (
              <button
                key={slot.id}
                onClick={() => setSelectedSlotId(slot.id)}
                className={`rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                  selectedSlotId === slot.id
                    ? 'border-accent bg-accent/10 text-accent'
                    : 'border-ink-200 dark:border-ink-600 hover:border-accent'
                }`}
              >
                {formatDateTime(slot.start_time)}
                <Badge className="ml-2" variant="success">open</Badge>
              </button>
            ))}
          </div>
        )}
        {selectedSlotId && (
          <div className="mt-4">
            <Textarea label="Notes for this session (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
            <Button className="mt-3" onClick={() => bookMutation.mutate()} isLoading={bookMutation.isPending}>
              Confirm booking
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
