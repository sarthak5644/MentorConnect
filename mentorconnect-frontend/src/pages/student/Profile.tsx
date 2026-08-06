import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studentsApi } from '@/api/endpoints';
import { StudentProfileUpdateRequest } from '@/types';
import { Input, Textarea, Button, PageSpinner, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

export default function StudentProfile() {
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data: profile, isLoading } = useQuery({ queryKey: ['student-profile'], queryFn: studentsApi.getMyProfile });

  const { register, handleSubmit, reset } = useForm<StudentProfileUpdateRequest>();

  useEffect(() => {
    if (profile) {
      reset({
        institution_name: profile.institution_name ?? '',
        education_level: profile.education_level ?? '',
        field_of_study: profile.field_of_study ?? '',
        bio: profile.bio ?? '',
        city: profile.city ?? '',
        country: profile.country ?? '',
        interests: profile.interests ?? '',
      });
    }
  }, [profile, reset]);

  const mutation = useMutation({
    mutationFn: studentsApi.updateProfile,
    onSuccess: () => {
      showToast('Profile updated', 'success');
      qc.invalidateQueries({ queryKey: ['student-profile'] });
    },
    onError: (err) => showToast(extractErrorMessage(err), 'error'),
  });

  if (isLoading) return <PageSpinner />;

  return (
    <div className="max-w-2xl">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">My profile</h1>
      <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="mt-6 space-y-4 session-card">
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Institution" {...register('institution_name')} />
          <Input label="Education level" {...register('education_level')} />
        </div>
        <Input label="Field of study" {...register('field_of_study')} />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="City" {...register('city')} />
          <Input label="Country" {...register('country')} />
        </div>
        <Input label="Interests (comma separated)" {...register('interests')} />
        <Textarea label="Bio" {...register('bio')} />
        <Button type="submit" isLoading={mutation.isPending}>Save changes</Button>
      </form>
    </div>
  );
}