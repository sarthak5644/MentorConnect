import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/context/AuthContext';
import { Input, Select, Button, useToast } from '@/components/ui';
import CaptchaField from '@/components/auth/CaptchaField';
import { extractErrorMessage } from '@/api/client';
import { RegisterRequest, RoleName } from '@/types';
import { OtpPurpose, OtpChannel } from '@/types';

interface RegisterForm extends Omit<RegisterRequest, 'captcha_session_id' | 'captcha_answer'> {
  confirm_password: string;
}

export default function Register() {
  const { register: registerUser } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [captchaSessionId, setCaptchaSessionId] = useState('');
  const [captchaAnswer, setCaptchaAnswer] = useState('');
  const [captchaError, setCaptchaError] = useState('');

  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterForm>({
    defaultValues: { role: RoleName.STUDENT },
  });

  const onSubmit = async (data: RegisterForm) => {
    if (!captchaAnswer) {
      setCaptchaError('Please complete the security check');
      return;
    }
    setCaptchaError('');
    setLoading(true);
    // replace the try block's success branch in Register.tsx
try {
  const { confirm_password, ...rest } = data;
  await registerUser({
    ...rest,
    role: data.role as RoleName.MENTOR | RoleName.STUDENT,
    captcha_session_id: captchaSessionId,
    captcha_answer: captchaAnswer,
  });
  showToast('Account created! Please verify your email.', 'success');
  navigate('/verify-otp', {
  state: { destination: data.email, purpose: OtpPurpose.EMAIL_VERIFICATION, channel: OtpChannel.EMAIL },
});
} catch (err) {
  showToast(extractErrorMessage(err), 'error');
} finally {
  setLoading(false);
}
  };

  return (
    <div className="mx-auto flex max-w-md flex-col justify-center px-4 py-12">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Create your account</h1>
      <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">Join as a student or mentor.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <Select label="I am a..." {...register('role', { required: true })}>
          <option value={RoleName.STUDENT}>Student</option>
          <option value={RoleName.MENTOR}>Mentor</option>
        </Select>
        <Input label="Full name" {...register('full_name', { required: 'Full name is required' })} error={errors.full_name?.message} />
        <Input label="Email" type="email" {...register('email', { required: 'Email is required' })} error={errors.email?.message} />
        <Input label="Mobile number" {...register('mobile_number')} error={errors.mobile_number?.message} />
        <Input
          label="Password"
          type="password"
          {...register('password', { required: 'Password is required', minLength: { value: 8, message: 'At least 8 characters' } })}
          error={errors.password?.message}
        />
        <Input
          label="Confirm password"
          type="password"
          {...register('confirm_password', {
            required: 'Please confirm your password',
            validate: (val) => val === watch('password') || 'Passwords do not match',
          })}
          error={errors.confirm_password?.message}
        />
        <CaptchaField
          sessionId={captchaSessionId}
          answer={captchaAnswer}
          onSessionIdChange={setCaptchaSessionId}
          onAnswerChange={setCaptchaAnswer}
          error={captchaError}
        />
        <Button type="submit" className="w-full" isLoading={loading}>Create account</Button>
      </form>

      <p className="mt-6 text-center text-sm text-ink-500 dark:text-ink-300">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-accent hover:underline">Log in</Link>
      </p>
    </div>
  );
}