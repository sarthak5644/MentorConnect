import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Star } from 'lucide-react';
import { ratingsApi } from '@/api/endpoints';
import { Modal, Textarea, Button, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

interface RateBookingModalProps {
  bookingId: number | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function RateBookingModal({ bookingId, onClose, onSuccess }: RateBookingModalProps) {
  const [score, setScore] = useState(0);
  const [review, setReview] = useState('');
  const { showToast } = useToast();

  const mutation = useMutation({
    mutationFn: () => ratingsApi.create({ booking_id: bookingId!, score, review }),
    onSuccess: () => {
      showToast('Thanks for your feedback!', 'success');
      onSuccess();
      onClose();
      setScore(0);
      setReview('');
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  return (
    <Modal isOpen={!!bookingId} onClose={onClose} title="Rate your session" size="sm">
      <div className="flex justify-center gap-2 mb-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <button key={i} onClick={() => setScore(i + 1)}>
            <Star className={`h-8 w-8 ${i < score ? 'text-accent fill-accent' : 'text-ink-200'}`} />
          </button>
        ))}
      </div>
      <Textarea label="Review (optional)" value={review} onChange={(e) => setReview(e.target.value)} />
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="secondary" onClick={onClose}>Cancel</Button>
        <Button disabled={score === 0} isLoading={mutation.isPending} onClick={() => mutation.mutate()}>
          Submit
        </Button>
      </div>
    </Modal>
  );
}