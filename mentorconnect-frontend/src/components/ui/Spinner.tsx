import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Spinner({ className, size = 24 }: { className?: string; size?: number }) {
  return <Loader2 className={cn('animate-spin text-accent', className)} size={size} />;
}

export function PageSpinner() {
  return (
    <div className="flex h-64 w-full items-center justify-center">
      <Spinner size={32} />
    </div>
  );
}