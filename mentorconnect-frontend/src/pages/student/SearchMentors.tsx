import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Search, SlidersHorizontal } from 'lucide-react';
import { mentorsApi, categoriesApi } from '@/api/endpoints';
import { MentorSearchFilters } from '@/types';
import { Select, Pagination, PageSpinner, EmptyState, Badge, Button } from '@/components/ui';
import { debounce, initials } from '@/lib/utils';

export default function StudentSearchMentors() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<MentorSearchFilters>({ page: 1, page_size: 9 });

  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.list });
  const { data, isLoading } = useQuery({ queryKey: ['mentors-search', filters], queryFn: () => mentorsApi.search(filters) });

  const onSearch = debounce((value: string) => setFilters((f) => ({ ...f, keyword: value, page: 1 })), 400);

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Search mentors</h1>

      <div className="mt-4 grid gap-3 sm:grid-cols-4 session-card">
        <div className="relative sm:col-span-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-300" />
          <input className="input-field pl-9" placeholder="Search by name or headline..." onChange={(e) => onSearch(e.target.value)} />
        </div>
        <Select onChange={(e) => setFilters((f) => ({ ...f, field_id: e.target.value ? Number(e.target.value) : undefined, page: 1 }))}>
          <option value="">All fields</option>
          {categories?.flatMap((c) => c.fields ?? []).map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
        </Select>
        <Select onChange={(e) => setFilters((f) => ({ ...f, page: 1 }))} defaultValue="rating">
          <option value="rating">Top rated</option>
          <option value="experience">Most experienced</option>
          <option value="price_low">Price: low to high</option>
          <option value="price_high">Price: high to low</option>
        </Select>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : !data?.items.length ? (
        <EmptyState icon={SlidersHorizontal} title="No mentors found" description="Try adjusting your filters." />
      ) : (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((m) => (
              <div key={m.id} className="session-card">
                <div className="flex h-11 w-11 items-center justify-center rounded-full bg-accent/10 text-sm font-medium text-accent">
                  {initials(m.designation || m.headline || 'Mentor')}
                </div>
                <p className="mt-3 font-medium text-ink-800 dark:text-ink-50">{m.designation || m.headline || `Mentor #${m.id}`}</p>
                <p className="text-sm text-ink-400 line-clamp-1">{m.headline}</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {m.expertise_fields.slice(0, 2).map((f) => <Badge key={f.id}>{f.name}</Badge>)}
                </div>
                <p className="mt-2 text-xs font-mono text-accent">★ {m.average_rating.toFixed(1)} · ${m.hourly_rate}/hr</p>
                <div className="mt-3 flex gap-2">
                  <Button size="sm" variant="secondary" onClick={() => navigate(`/mentors/${m.id}`)}>View profile</Button>
                  <Button size="sm" onClick={() => navigate(`/student/book/${m.id}`)}>Book</Button>
                </div>
              </div>
            ))}
          </div>
          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={(p) => setFilters((f) => ({ ...f, page: p }))} />
        </>
      )}
    </div>
  );
}
