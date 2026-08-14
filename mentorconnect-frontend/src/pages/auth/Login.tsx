import { useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/context/AuthContext';
import { Input, Button, useToast } from '@/components/ui';
import CaptchaField, { CaptchaFieldHandle } from '@/components/auth/CaptchaField';
import { extractErrorMessage } from '@/api/client';
import { LoginRequest } from '@/types';

type LoginFormFields = Pick<LoginRequest, 'email' | 'password'>;

export default function Login() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormFields>();
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [captchaSessionId, setCaptchaSessionId] = useState('');
  const [captchaAnswer, setCaptchaAnswer] = useState('');
  const captchaRef = useRef<CaptchaFieldHandle>(null);

  const onSubmit = async (data: LoginFormFields) => {
    setLoading(true);
    try {
      const user = await login({ ...data, captcha_session_id: captchaSessionId, captcha_answer: captchaAnswer });
      if (user.status === 'pending') {
        navigate('/verify-otp', { replace: true });
        return;
      }
      const from = (location.state as any)?.from?.pathname;
      navigate(from || '/', { replace: true });
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
      captchaRef.current?.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-12">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Welcome back</h1>
      <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">Log in to continue to MentorConnect.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <Input
          label="Email"
          type="email"
          {...register('email', { required: 'Email is required' })}
          error={errors.email?.message}
        />
        <Input
          label="Password"
          type="password"
          {...register('password', { required: 'Password is required' })}
          error={errors.password?.message}
        />
        <div className="flex justify-end">
          <Link to="/forgot-password" className="text-sm text-accent hover:underline">Forgot password?</Link>
        </div>
        <CaptchaField
          ref={captchaRef}
          sessionId={captchaSessionId}
          answer={captchaAnswer}
          onSessionIdChange={setCaptchaSessionId}
          onAnswerChange={setCaptchaAnswer}
        />
        <Button type="submit" className="w-full" isLoading={loading}>Log in</Button>
      </form>

      <p className="mt-6 text-center text-sm text-ink-500 dark:text-ink-300">
        Don't have an account?{' '}
        <Link to="/register" className="font-medium text-accent hover:underline">Sign up</Link>
      </p>
    </div>
  );
}
