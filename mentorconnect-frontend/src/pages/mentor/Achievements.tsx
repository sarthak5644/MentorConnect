import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Trophy, Plus, Trash2 } from 'lucide-react';
import { mentorsApi } from '@/api/endpoints';
import { parseJsonList } from '@/utils/parseJsonList';
import { Achievement } from '@/types';
import { Input, Textarea, Button, PageSpinner, EmptyState, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

export default function MentorAchievements() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data: profile, isLoading } = useQuery({ queryKey: ['mentor-profile'], queryFn: mentorsApi.getMyProfile });
  const [items, setItems] = useState<Achievement[]>([]);

  useEffect(() => {
    if (profile) setItems(parseJsonList<Achievement>(profile.profile.achievements));
  }, [profile]);

  const mutation = useMutation({
    mutationFn: () => mentorsApi.updateAchievements(items),
    onSuccess: () => {
      showToast('Achievements saved', 'success');
      qc.invalidateQueries({ queryKey: ['mentor-profile'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  const update = (idx: number, field: keyof Achievement, value: string | number) => {
    setItems((prev) => prev.map((a, i) => (i === idx ? { ...a, [field]: value } : a)));
  };
  const remove = (idx: number) => setItems((prev) => prev.filter((_, i) => i !== idx));
  const add = () => setItems((prev) => [...prev, { title: '', description: '', year: new Date().getFullYear() }]);

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Achievements</h1>
        <Button size="sm" onClick={add}><Plus className="h-4 w-4" /> Add</Button>
      </div>

      {!items.length ? (
        <div className="mt-6"><EmptyState icon={Trophy} title="No achievements added" action={<Button onClick={add}>Add your first</Button>} /></div>
      ) : (
        <div className="mt-6 space-y-3">
          {items.map((a, i) => (
            <div key={i} className="session-card space-y-3">
              <div className="grid gap-3 sm:grid-cols-[1fr_120px_40px] items-end">
                <Input label="Title" value={a.title} onChange={(e) => update(i, 'title', e.target.value)} />
                <Input label="Year" type="number" value={a.year} onChange={(e) => update(i, 'year', Number(e.target.value))} />
                <Button variant="danger" size="sm" onClick={() => remove(i)}><Trash2 className="h-4 w-4" /></Button>
              </div>
              <Textarea label="Description" value={a.description} onChange={(e) => update(i, 'description', e.target.value)} />
            </div>
          ))}
        </div>
      )}

      <Button className="mt-6" isLoading={mutation.isPending} onClick={() => mutation.mutate()}>Save achievements</Button>
    </div>
  );
}
