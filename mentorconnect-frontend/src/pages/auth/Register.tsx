import { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/context/AuthContext';
import { Input, Select, Button, useToast } from '@/components/ui';
import CaptchaField, { CaptchaFieldHandle } from '@/components/auth/CaptchaField';
import { extractErrorMessage } from '@/api/client';
import { RoleName } from '@/types';

interface RegisterFormFields {
  role: RoleName.MENTOR | RoleName.STUDENT;
  full_name: string;
  email: string;
  mobile_number: string;
  password: string;
  confirm_password: string;
  // student-only
  institution_name?: string;
  // mentor-only
  years_of_experience?: number;
  hourly_rate?: number;
}

export default function Register() {
  const { registerStudent, registerMentor } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [captchaSessionId, setCaptchaSessionId] = useState('');
  const [captchaAnswer, setCaptchaAnswer] = useState('');
  const [captchaError, setCaptchaError] = useState('');
  const captchaRef = useRef<CaptchaFieldHandle>(null);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormFields>({
    defaultValues: { role: RoleName.STUDENT },
  });
  const role = watch('role');

  const onSubmit = async (data: RegisterFormFields) => {
    if (!captchaAnswer) {
      setCaptchaError('Please complete the security check');
      return;
    }
    setCaptchaError('');
    setLoading(true);
    try {
      const shared = {
        full_name: data.full_name,
        email: data.email,
        mobile_number: data.mobile_number,
        password: data.password,
        captcha_session_id: captchaSessionId,
        captcha_answer: captchaAnswer,
      };

      if (data.role === RoleName.STUDENT) {
        await registerStudent({ ...shared, institution_name: data.institution_name });
      } else {
        await registerMentor({
          ...shared,
          years_of_experience: Number(data.years_of_experience) || 0,
          hourly_rate: Number(data.hourly_rate) || 0,
          expertise_field_ids: [],
        });
      }

      // The backend only returns the created user here — no tokens.
      // Login is a required separate step (accounts can log in while
      // status="pending"), and OTP verification happens after that.
      showToast('Account created! Please log in to verify your email and mobile.', 'success');
      navigate('/login');
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
      captchaRef.current?.refresh();
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
        <Input
          label="Mobile number"
          placeholder="+911234567890"
          {...register('mobile_number', { required: 'Mobile number is required' })}
          error={errors.mobile_number?.message}
        />
        <Input
          label="Password"
          type="password"
          {...register('password', {
            required: 'Password is required',
            pattern: {
              value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_\-+=]).{8,64}$/,
              message: '8+ chars with upper, lower, a digit, and a symbol',
            },
          })}
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

        {role === RoleName.STUDENT ? (
          <Input label="Institution (optional)" {...register('institution_name')} />
        ) : (
          <>
            <Input
              label="Years of experience"
              type="number"
              min={0}
              {...register('years_of_experience', { required: 'Required', min: 0 })}
              error={errors.years_of_experience?.message}
            />
            <Input
              label="Hourly rate"
              type="number"
              min={0}
              step="0.01"
              {...register('hourly_rate', { required: 'Required', min: 0 })}
              error={errors.hourly_rate?.message}
            />
            <p className="text-xs text-ink-400">You can pick your areas of expertise from your profile after logging in.</p>
          </>
        )}

        <CaptchaField
          ref={captchaRef}
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
