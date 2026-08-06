import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-ink-100 dark:border-ink-700 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ink-400">
        <p>© {new Date().getFullYear()} MentorConnect. All rights reserved.</p>
        <div className="flex gap-6">
          <Link to="/about" className="hover:text-ink-700 dark:hover:text-ink-100">About</Link>
          <Link to="/mentors" className="hover:text-ink-700 dark:hover:text-ink-100">Find Mentors</Link>
          <Link to="/contact" className="hover:text-ink-700 dark:hover:text-ink-100">Contact</Link>
        </div>
      </div>
    </footer>
  );
}