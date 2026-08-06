import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { authApi } from '@/api/endpoints';
import { Input, Button, useToast } from '@/components/ui';
import { extractErrorMessage } from '@/api/client';

export default function ForgotPassword() {
  const { register, handleSubmit, formState: { errors } } = useForm<{ email: string }>();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onSubmit = async (data: { email: string }) => {
    setLoading(true);
    try {
      await authApi.forgotPassword(data);
      showToast('If that email exists, an OTP has been sent.', 'success');
      navigate('/reset-password', { state: { email: data.email } });
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-md flex-col justify-center px-4 py-12">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Forgot password</h1>
      <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">We'll send an OTP to reset your password.</p>
      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <Input label="Email" type="email" {...register('email', { required: 'Email is required' })} error={errors.email?.message} />
        <Button type="submit" className="w-full" isLoading={loading}>Send OTP</Button>
      </form>
      <p className="mt-6 text-center text-sm text-ink-500 dark:text-ink-300">
        Remembered it? <Link to="/login" className="font-medium text-accent hover:underline">Log in</Link>
      </p>
    </div>
  );
}