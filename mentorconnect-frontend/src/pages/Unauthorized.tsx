import { Link } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';
import Button from '@/components/ui/Button';

export default function Unauthorized() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <ShieldAlert className="h-10 w-10 text-danger" />
      <h1 className="mt-3 font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Access denied</h1>
      <p className="mt-2 text-ink-500 dark:text-ink-300">You don't have permission to view this page.</p>
      <Link to="/" className="mt-6"><Button>Back home</Button></Link>
    </div>
  );
}