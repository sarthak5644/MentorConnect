import { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { authApi } from '@/api/endpoints';
import { Input, Button, useToast } from '@/components/ui';
import OtpInput from '@/components/auth/OtpInput';
import { extractErrorMessage } from '@/api/client';

interface ResetForm {
  email: string;
  new_password: string;
  confirm_password: string;
}

export default function ResetPassword() {
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<ResetForm>({
    defaultValues: { email: (location.state as any)?.email || '' },
  });

  const onSubmit = async (data: ResetForm) => {
    if (otp.length !== 6) {
      showToast('Enter the 6-digit OTP', 'error');
      return;
    }
    setLoading(true);
    try {
      await authApi.resetPassword({ email: data.email, otp_code: otp, password: data.new_password });
      showToast('Password reset successfully. Please log in.', 'success');
      navigate('/login');
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-md flex-col justify-center px-4 py-12">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Reset password</h1>
      <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">Enter the OTP sent to your email and choose a new password.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <Input label="Email" type="email" {...register('email', { required: 'Email is required' })} error={errors.email?.message} />

        <div>
          <label className="label-text">One-Time Password</label>
          <OtpInput value={otp} onChange={setOtp} />
        </div>

        <Input
          label="New password"
          type="password"
          {...register('new_password', { required: 'Required', minLength: { value: 8, message: 'At least 8 characters' } })}
          error={errors.new_password?.message}
        />
        <Input
          label="Confirm new password"
          type="password"
          {...register('confirm_password', {
            required: 'Required',
            validate: (v) => v === watch('new_password') || 'Passwords do not match',
          })}
          error={errors.confirm_password?.message}
        />
        <Button type="submit" className="w-full" isLoading={loading}>Reset password</Button>
      </form>

      <p className="mt-6 text-center text-sm text-ink-500 dark:text-ink-300">
        <Link to="/login" className="font-medium text-accent hover:underline">Back to login</Link>
      </p>
    </div>
  );
}
