import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FolderTree, Plus, Trash2 } from 'lucide-react';
import { categoriesApi } from '@/api/endpoints';
import { PageSpinner, EmptyState, Input, Button, Badge, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

export default function AdminCategories() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [newCategory, setNewCategory] = useState('');
  const [newFieldByCategory, setNewFieldByCategory] = useState<Record<number, string>>({});

  const { data: categories, isLoading } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.list });

  const createCategoryMutation = useMutation({
    mutationFn: () => categoriesApi.create({ name: newCategory }),
    onSuccess: () => {
      showToast('Category created', 'success');
      setNewCategory('');
      qc.invalidateQueries({ queryKey: ['categories'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const deleteCategoryMutation = useMutation({
    mutationFn: (id: number) => categoriesApi.delete(id),
    onSuccess: () => {
      showToast('Category deleted', 'success');
      qc.invalidateQueries({ queryKey: ['categories'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const createFieldMutation = useMutation({
    mutationFn: ({ categoryId, name }: { categoryId: number; name: string }) => categoriesApi.createField(categoryId, { name }),
    onSuccess: (_data, vars) => {
      showToast('Field added', 'success');
      setNewFieldByCategory((p) => ({ ...p, [vars.categoryId]: '' }));
      qc.invalidateQueries({ queryKey: ['categories'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  const deleteFieldMutation = useMutation({
    mutationFn: (fieldId: number) => categoriesApi.deleteField(fieldId),
    onSuccess: () => {
      showToast('Field deleted', 'success');
      qc.invalidateQueries({ queryKey: ['categories'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div className="max-w-3xl">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Categories & fields</h1>

      <div className="mt-4 session-card flex gap-3 items-end">
        <Input label="New category" value={newCategory} onChange={(e) => setNewCategory(e.target.value)} className="flex-1" />
        <Button disabled={!newCategory} isLoading={createCategoryMutation.isPending} onClick={() => createCategoryMutation.mutate()}>
          <Plus className="h-4 w-4" /> Add
        </Button>
      </div>

      {!categories?.length ? (
        <div className="mt-6"><EmptyState icon={FolderTree} title="No categories yet" /></div>
      ) : (
        <div className="mt-6 space-y-4">
          {categories.map((c) => (
            <div key={c.id} className="session-card">
              <div className="flex items-center justify-between">
                <p className="font-display text-lg font-medium text-ink-800 dark:text-ink-50">{c.name}</p>
                <Button size="sm" variant="danger" onClick={() => deleteCategoryMutation.mutate(c.id)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {c.fields?.map((f) => (
                  <Badge key={f.id} className="flex items-center gap-1">
                    {f.name}
                    <button onClick={() => deleteFieldMutation.mutate(f.id)} className="ml-1 text-ink-400 hover:text-danger">×</button>
                  </Badge>
                ))}
              </div>
              <div className="mt-3 flex gap-2">
                <input
                  className="input-field flex-1"
                  placeholder="New field name"
                  value={newFieldByCategory[c.id] ?? ''}
                  onChange={(e) => setNewFieldByCategory((p) => ({ ...p, [c.id]: e.target.value }))}
                />
                <Button
                  size="sm"
                  disabled={!newFieldByCategory[c.id]}
                  onClick={() => createFieldMutation.mutate({ categoryId: c.id, name: newFieldByCategory[c.id] })}
                >
                  Add field
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}