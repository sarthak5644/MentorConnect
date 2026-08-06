import { useRef } from 'react';

interface OtpInputProps {
  value: string;
  onChange: (val: string) => void;
  length?: number;
}

export default function OtpInput({ value, onChange, length = 6 }: OtpInputProps) {
  const refs = useRef<(HTMLInputElement | null)[]>([]);
  const digits = value.split('').concat(Array(length).fill('')).slice(0, length);

  const setDigit = (idx: number, val: string) => {
    if (!/^\d*$/.test(val)) return;
    const next = digits.slice();
    next[idx] = val.slice(-1);
    onChange(next.join('').replace(/\s/g, ''));
    if (val && idx < length - 1) refs.current[idx + 1]?.focus();
  };

  const onKeyDown = (idx: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[idx] && idx > 0) refs.current[idx - 1]?.focus();
  };

  return (
    <div className="flex gap-2">
      {digits.map((d, i) => (
        <input
          key={i}
          ref={(el) => (refs.current[i] = el)}
          value={d}
          onChange={(e) => setDigit(i, e.target.value)}
          onKeyDown={(e) => onKeyDown(i, e)}
          maxLength={1}
          inputMode="numeric"
          className="h-12 w-11 rounded-lg border border-ink-200 dark:border-ink-600 bg-white dark:bg-ink-800 text-center text-lg font-mono focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
        />
      ))}
    </div>
  );
}