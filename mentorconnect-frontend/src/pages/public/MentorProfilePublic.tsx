import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Briefcase, MapPin, Star, Linkedin, Globe } from 'lucide-react';
import { mentorsApi, ratingsApi } from '@/api/endpoints';
import { PageSpinner, Badge, EmptyState } from '@/components/ui';
import { useAuth } from '@/context/AuthContext';
import { initials, formatDate } from '@/lib/utils';

export default function MentorProfilePublic() {
  const { id } = useParams<{ id: string }>();
  const mentorId = Number(id);
  const { isAuthenticated, role } = useAuth();

  const { data: mentor, isLoading } = useQuery({
    queryKey: ['mentor', mentorId],
    queryFn: () => mentorsApi.getById(mentorId),
    enabled: !!mentorId,
  });

  const { data: ratings } = useQuery({
    queryKey: ['mentor-ratings', mentorId],
    queryFn: () => ratingsApi.listForMentor(mentorId, { page: 1, page_size: 10 }),
    enabled: !!mentorId,
  });

  if (isLoading) return <PageSpinner />;
  if (!mentor) return <EmptyState icon={Briefcase} title="Mentor not found" />;

  const bookHref = isAuthenticated && role === 'student' ? `/student/book/${mentor.id}` : '/login';

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-12">
      <div className="session-card flex flex-col sm:flex-row gap-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-accent/10 text-2xl font-medium text-accent shrink-0">
          {initials(mentor.user.full_name)}
        </div>
        <div className="flex-1">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">{mentor.user.full_name}</h1>
              <p className="text-ink-500 dark:text-ink-300">{mentor.headline}</p>
            </div>
            <Link to={bookHref} className="btn-primary">Book a session</Link>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-ink-500 dark:text-ink-300">
            <span className="flex items-center gap-1"><Star className="h-4 w-4 text-accent" /> {mentor.average_rating.toFixed(1)} ({mentor.total_ratings} reviews)</span>
            <span className="flex items-center gap-1"><Briefcase className="h-4 w-4" /> {mentor.years_of_experience}y experience</span>
            {mentor.city && <span className="flex items-center gap-1"><MapPin className="h-4 w-4" /> {mentor.city}, {mentor.country}</span>}
            <span className="font-mono text-accent">${mentor.hourly_rate}/hr</span>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {mentor.expertise_fields.map((f) => <Badge key={f.id} variant="info">{f.name}</Badge>)}
          </div>
          <div className="mt-3 flex gap-3">
            {mentor.linkedin_url && (
              <a href={mentor.linkedin_url} target="_blank" rel="noreferrer" className="text-ink-400 hover:text-accent">
                <Linkedin className="h-4 w-4" />
              </a>
            )}
            {mentor.portfolio_url && (
              <a href={mentor.portfolio_url} target="_blank" rel="noreferrer" className="text-ink-400 hover:text-accent">
                <Globe className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>
      </div>

      {mentor.bio && (
        <div className="session-card mt-6">
          <h2 className="font-display text-lg font-medium text-ink-800 dark:text-ink-50 mb-2">About</h2>
          <p className="text-ink-600 dark:text-ink-300 leading-relaxed">{mentor.bio}</p>
        </div>
      )}

      {mentor.qualifications?.length > 0 && (
        <div className="session-card mt-6">
          <h2 className="font-display text-lg font-medium text-ink-800 dark:text-ink-50 mb-3">Qualifications</h2>
          <ul className="space-y-2">
            {mentor.qualifications.map((q, i) => (
              <li key={i} className="text-sm text-ink-600 dark:text-ink-300">
                <span className="font-medium text-ink-800 dark:text-ink-50">{q.degree}</span> — {q.institute} ({q.year})
              </li>
            ))}
          </ul>
        </div>
      )}

      {mentor.achievements?.length > 0 && (
        <div className="session-card mt-6">
          <h2 className="font-display text-lg font-medium text-ink-800 dark:text-ink-50 mb-3">Achievements</h2>
          <ul className="space-y-3">
            {mentor.achievements.map((a, i) => (
              <li key={i}>
                <p className="text-sm font-medium text-ink-800 dark:text-ink-50">{a.title} ({a.year})</p>
                <p className="text-sm text-ink-500 dark:text-ink-300">{a.description}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="session-card mt-6">
        <h2 className="font-display text-lg font-medium text-ink-800 dark:text-ink-50 mb-3">Reviews</h2>
        {!ratings?.items.length ? (
          <p className="text-sm text-ink-400">No reviews yet.</p>
        ) : (
          <ul className="space-y-4">
            {ratings.items.map((r) => (
              <li key={r.id} className="border-b border-ink-100 dark:border-ink-700 pb-3 last:border-0">
                <div className="flex items-center gap-2">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className={`h-3.5 w-3.5 ${i < r.score ? 'text-accent fill-accent' : 'text-ink-200'}`} />
                  ))}
                  <span className="text-xs text-ink-400">{formatDate(r.created_at)}</span>
                </div>
                {r.review && <p className="mt-1 text-sm text-ink-600 dark:text-ink-300">{r.review}</p>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}