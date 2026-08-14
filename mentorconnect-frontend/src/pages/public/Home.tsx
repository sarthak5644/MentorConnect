import { Link } from 'react-router-dom';
import { ArrowRight, Users, ShieldCheck, MessageSquare } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { mentorsApi } from '@/api/endpoints';
import { PageSpinner } from '@/components/ui';
import { initials } from '@/lib/utils';

export default function Home() {
  const { data, isLoading } = useQuery({
    queryKey: ['featured-mentors'],
    queryFn: () => mentorsApi.search({ page: 1, page_size: 4 }),
  });

  return (
    <div>
      <section className="mx-auto max-w-7xl px-4 sm:px-6 py-20 sm:py-28">
        <div className="max-w-2xl">
          <p className="font-mono text-sm text-accent">field notes for your next chapter</p>
          <h1 className="mt-3 font-display text-4xl sm:text-5xl font-semibold leading-tight text-ink-800 dark:text-ink-50">
            Find a mentor who's already walked your path.
          </h1>
          <p className="mt-4 text-lg text-ink-500 dark:text-ink-300">
            MentorConnect pairs students with verified, experienced mentors for real guidance — 1:1 sessions,
            honest feedback, and a relationship that outlasts a single conversation.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/mentors" className="btn-primary">
              Browse mentors <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/register" className="btn-secondary">Become a mentor</Link>
          </div>
        </div>
      </section>

      <section className="border-y border-ink-100 dark:border-ink-700 bg-white dark:bg-ink-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 py-14 grid gap-8 sm:grid-cols-3">
          {[
            { icon: ShieldCheck, title: 'Verified mentors', desc: 'Every mentor is document-checked and admin-approved.' },
            { icon: Users, title: 'Real matching', desc: 'Filter by field, rating, and experience to find the right fit.' },
            { icon: MessageSquare, title: 'Built-in chat & booking', desc: 'Message, schedule, and meet — all in one place.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title}>
              <Icon className="h-6 w-6 text-accent" />
              <h3 className="mt-3 font-display text-lg font-medium text-ink-800 dark:text-ink-50">{title}</h3>
              <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 sm:px-6 py-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Top rated mentors</h2>
          <Link to="/mentors" className="text-sm font-medium text-accent hover:underline">View all</Link>
        </div>
        {isLoading ? (
          <PageSpinner />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {data?.items.map((m) => (
              <Link key={m.id} to={`/mentors/${m.id}`} className="session-card block">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-sm font-medium text-accent">
                  {initials(m.designation || m.headline || 'Mentor')}
                </div>
                <p className="mt-3 font-medium text-ink-800 dark:text-ink-50">{m.designation || m.headline || `Mentor #${m.id}`}</p>
                <p className="text-sm text-ink-400 line-clamp-1">{m.headline}</p>
                <p className="mt-2 text-xs font-mono text-accent">★ {m.average_rating.toFixed(1)} ({m.total_ratings})</p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
