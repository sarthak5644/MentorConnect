import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GraduationCap, Plus, Trash2 } from 'lucide-react';
import { mentorsApi } from '@/api/endpoints';
import { parseJsonList } from '@/utils/parseJsonList';
import { Qualification } from '@/types';
import { Input, Button, PageSpinner, EmptyState, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

export default function MentorQualifications() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data: profile, isLoading } = useQuery({ queryKey: ['mentor-profile'], queryFn: mentorsApi.getMyProfile });
  const [items, setItems] = useState<Qualification[]>([]);

  useEffect(() => {
    if (profile) setItems(parseJsonList<Qualification>(profile.profile.qualifications));
  }, [profile]);

  const mutation = useMutation({
    mutationFn: () => mentorsApi.updateQualifications(items),
    onSuccess: () => {
      showToast('Qualifications saved', 'success');
      qc.invalidateQueries({ queryKey: ['mentor-profile'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  const update = (idx: number, field: keyof Qualification, value: string | number) => {
    setItems((prev) => prev.map((q, i) => (i === idx ? { ...q, [field]: value } : q)));
  };

  const remove = (idx: number) => setItems((prev) => prev.filter((_, i) => i !== idx));
  const add = () => setItems((prev) => [...prev, { degree: '', institute: '', year: new Date().getFullYear() }]);

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Qualifications</h1>
        <Button size="sm" onClick={add}><Plus className="h-4 w-4" /> Add</Button>
      </div>

      {!items.length ? (
        <div className="mt-6"><EmptyState icon={GraduationCap} title="No qualifications added" action={<Button onClick={add}>Add your first</Button>} /></div>
      ) : (
        <div className="mt-6 space-y-3">
          {items.map((q, i) => (
            <div key={i} className="session-card grid gap-3 sm:grid-cols-[1fr_1fr_120px_40px] items-end">
              <Input label="Degree" value={q.degree} onChange={(e) => update(i, 'degree', e.target.value)} />
              <Input label="Institute" value={q.institute} onChange={(e) => update(i, 'institute', e.target.value)} />
              <Input label="Year" type="number" value={q.year} onChange={(e) => update(i, 'year', Number(e.target.value))} />
              <Button variant="danger" size="sm" onClick={() => remove(i)}><Trash2 className="h-4 w-4" /></Button>
            </div>
          ))}
        </div>
      )}

      <Button className="mt-6" isLoading={mutation.isPending} onClick={() => mutation.mutate()}>Save qualifications</Button>
    </div>
  );
}
