import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CalendarClock, Plus, Trash2 } from 'lucide-react';
import { availabilityApi } from '@/api/endpoints';
import { SlotStatus } from '@/types';
import { Input, Button, PageSpinner, EmptyState, Badge, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';
import { formatDateTime } from '@/lib/utils';

const statusVariant: Record<SlotStatus, 'default' | 'success' | 'warning'> = {
  [SlotStatus.AVAILABLE]: 'success',
  [SlotStatus.BOOKED]: 'warning',
  [SlotStatus.BLOCKED]: 'default',
};

export default function MentorAvailability() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  const { data: slots, isLoading } = useQuery({ queryKey: ['my-slots'], queryFn: availabilityApi.listMySlots });

  const createMutation = useMutation({
    mutationFn: () => availabilityApi.create({ start_time: start, end_time: end }),
    onSuccess: () => {
      showToast('Slot created', 'success');
      setStart(''); setEnd('');
      qc.invalidateQueries({ queryKey: ['my-slots'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => availabilityApi.delete(id),
    onSuccess: () => {
      showToast('Slot removed', 'success');
      qc.invalidateQueries({ queryKey: ['my-slots'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div className="max-w-2xl">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Availability</h1>

      <div className="mt-6 session-card grid gap-3 sm:grid-cols-[1fr_1fr_auto] items-end">
        <Input label="Start time" type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} />
        <Input label="End time" type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} />
        <Button
          disabled={!start || !end}
          isLoading={createMutation.isPending}
          onClick={() => createMutation.mutate()}
        >
          <Plus className="h-4 w-4" /> Add slot
        </Button>
      </div>

      {!slots?.length ? (
        <div className="mt-6"><EmptyState icon={CalendarClock} title="No slots yet" description="Add availability so students can book sessions." /></div>
      ) : (
        <div className="mt-6 space-y-2">
          {slots.map((s) => (
            <div key={s.id} className="session-card flex items-center justify-between">
              <div>
                <p className="font-medium text-ink-800 dark:text-ink-50">{formatDateTime(s.start_time)}</p>
                <p className="text-xs text-ink-400">to {formatDateTime(s.end_time)}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={statusVariant[s.status]}>{s.status}</Badge>
                {s.status === SlotStatus.AVAILABLE && (
                  <Button size="sm" variant="danger" onClick={() => deleteMutation.mutate(s.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}