import { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { authApi } from '@/api/endpoints';
import { Input } from '@/components/ui';

interface CaptchaFieldProps {
  sessionId: string;
  answer: string;
  onSessionIdChange: (id: string) => void;
  onAnswerChange: (val: string) => void;
  error?: string;
}

export default function CaptchaField({ sessionId, answer, onSessionIdChange, onAnswerChange, error }: CaptchaFieldProps) {
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchCaptcha = async () => {
    setLoading(true);
    try {
      const res = await authApi.getCaptcha();
      setImage(res.image_base64);
      onSessionIdChange(res.session_id);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCaptcha();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <label className="label-text">Security check</label>
      <div className="flex items-center gap-2 mb-2">
        {image ? (
          <img
            src={`data:image/png;base64,${image}`}
            alt="captcha"
            className="h-12 w-40 rounded-md border border-ink-200 dark:border-ink-600 object-cover"
          />
        ) : (
          <div className="h-12 w-40 animate-pulse rounded-md bg-ink-100 dark:bg-ink-700" />
        )}
        <button
          type="button"
          onClick={fetchCaptcha}
          disabled={loading}
          className="rounded-md p-2 text-ink-400 hover:text-accent hover:bg-ink-50 dark:hover:bg-ink-700"
          aria-label="Refresh captcha"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
      <input type="hidden" value={sessionId} readOnly />
      <Input
        placeholder="Enter the text shown above"
        value={answer}
        onChange={(e) => onAnswerChange(e.target.value)}
        error={error}
      />
    </div>
  );
}