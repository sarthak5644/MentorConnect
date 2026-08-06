import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mentorsApi, categoriesApi } from '@/api/endpoints';
import { MentorProfileUpdateRequest } from '@/types';
import { Input, Textarea, Button, PageSpinner, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

export default function MentorProfile() {
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data: profile, isLoading } = useQuery({ queryKey: ['mentor-profile'], queryFn: mentorsApi.getMyProfile });
  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.list });

  const { register, handleSubmit, reset, watch, setValue } = useForm<MentorProfileUpdateRequest>();

  useEffect(() => {
    if (profile) {
      reset({
        headline: profile.headline ?? '',
        bio: profile.bio ?? '',
        years_of_experience: profile.years_of_experience,
        current_organization: profile.current_organization ?? '',
        designation: profile.designation ?? '',
        hourly_rate: profile.hourly_rate,
        city: profile.city ?? '',
        country: profile.country ?? '',
        linkedin_url: profile.linkedin_url ?? '',
        portfolio_url: profile.portfolio_url ?? '',
        expertise_field_ids: profile.expertise_fields.map((f) => f.id),
      });
    }
  }, [profile, reset]);

  const mutation = useMutation({
    mutationFn: mentorsApi.updateProfile,
    onSuccess: () => {
      showToast('Profile updated', 'success');
      qc.invalidateQueries({ queryKey: ['mentor-profile'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  const selectedFieldIds = watch('expertise_field_ids') ?? [];
  const toggleField = (id: number) => {
    const next = selectedFieldIds.includes(id)
      ? selectedFieldIds.filter((f) => f !== id)
      : [...selectedFieldIds, id];
    setValue('expertise_field_ids', next);
  };

  return (
    <div className="max-w-2xl">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">My mentor profile</h1>
      <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="mt-6 space-y-4 session-card">
        <Input label="Headline" {...register('headline')} placeholder="e.g. Senior Data Scientist at XYZ" />
        <Textarea label="Bio" {...register('bio')} />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Years of experience" type="number" {...register('years_of_experience', { valueAsNumber: true })} />
          <Input label="Hourly rate ($)" type="number" step="0.01" {...register('hourly_rate', { valueAsNumber: true })} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Current organization" {...register('current_organization')} />
          <Input label="Designation" {...register('designation')} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="City" {...register('city')} />
          <Input label="Country" {...register('country')} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="LinkedIn URL" {...register('linkedin_url')} />
          <Input label="Portfolio URL" {...register('portfolio_url')} />
        </div>

        <div>
          <label className="label-text">Expertise fields</label>
          <div className="flex flex-wrap gap-2">
            {categories?.flatMap((c) => c.fields ?? []).map((f) => (
              <button
                type="button"
                key={f.id}
                onClick={() => toggleField(f.id)}
                className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                  selectedFieldIds.includes(f.id)
                    ? 'border-mentor bg-mentor/10 text-mentor'
                    : 'border-ink-200 dark:border-ink-600 text-ink-500 hover:border-mentor'
                }`}
              >
                {f.name}
              </button>
            ))}
          </div>
        </div>

        <Button type="submit" isLoading={mutation.isPending}>Save changes</Button>
      </form>
    </div>
  );
}