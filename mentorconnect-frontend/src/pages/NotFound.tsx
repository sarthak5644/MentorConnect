import { Link } from 'react-router-dom';
import Button from '@/components/ui/Button';

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <p className="font-mono text-sm text-accent">404</p>
      <h1 className="mt-2 font-display text-3xl font-semibold text-ink-800 dark:text-ink-50">Page not found</h1>
      <p className="mt-2 text-ink-500 dark:text-ink-300">The page you're looking for doesn't exist.</p>
      <Link to="/" className="mt-6"><Button>Back home</Button></Link>
    </div>
  );
}