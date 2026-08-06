import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { authApi } from '@/api/endpoints';
import { Button, useToast } from '@/components/ui';
import OtpInput from '@/components/auth/OtpInput';
import { extractErrorMessage } from '@/api/client';
import { OtpPurpose, OtpChannel } from '@/types';
import { useAuth } from '@/context/AuthContext';

interface VerifyOtpState {
  destination: string;
  purpose: OtpPurpose;
  channel: OtpChannel;
}

export default function VerifyOtp() {
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { user, refreshUser } = useAuth();

  const state = location.state as VerifyOtpState | undefined;
  const destination = state?.destination ?? user?.email ?? '';
  const purpose = state?.purpose ?? OtpPurpose.EMAIL_VERIFICATION;
  const channel = state?.channel ?? OtpChannel.EMAIL;

  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  useEffect(() => {
    if (!destination) return;
    // auto-request an OTP on first load if none was just sent by the previous screen
  }, [destination]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const t = setTimeout(() => setResendCooldown((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [resendCooldown]);

  const requestOtp = async () => {
    if (resendCooldown > 0 || !destination) return;
    try {
      await authApi.requestOtp({ destination, purpose });
      showToast('OTP sent', 'success');
      setResendCooldown(30);
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
    }
  };

  const onVerify = async () => {
    if (otp.length !== 6) {
      showToast('Enter the 6-digit OTP', 'error');
      return;
    }
    setLoading(true);
    try {
      await authApi.verifyOtp({ destination, otp, purpose });
      showToast('Verified successfully', 'success');

      if (user) {
        const updated =
          purpose === OtpPurpose.EMAIL_VERIFICATION
            ? { ...user, is_email_verified: true }
            : purpose === OtpPurpose.MOBILE_VERIFICATION
            ? { ...user, is_mobile_verified: true }
            : user;
        refreshUser(updated);
      }

      navigate(-1);
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
    } finally {
      setLoading(false);
    }
  };

  const title = purpose === OtpPurpose.MOBILE_VERIFICATION ? 'Verify your mobile number' : 'Verify your email';
  const subtitle =
    channel === OtpChannel.SMS
      ? `Enter the 6-digit code sent to ${destination}`
      : `Enter the 6-digit code sent to ${destination}`;

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-md flex-col justify-center px-4 py-12">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">{title}</h1>
      <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">{subtitle}</p>

      <div className="mt-6">
        <OtpInput value={otp} onChange={setOtp} />
      </div>

      <Button className="mt-6 w-full" isLoading={loading} onClick={onVerify}>
        Verify
      </Button>

      <button
        type="button"
        disabled={resendCooldown > 0}
        onClick={requestOtp}
        className="mt-4 text-sm text-accent hover:underline disabled:text-ink-300 disabled:no-underline"
      >
        {resendCooldown > 0 ? `Resend OTP in ${resendCooldown}s` : 'Resend OTP'}
      </button>

      <p className="mt-6 text-center text-sm text-ink-500 dark:text-ink-300">
        <Link to="/login" className="font-medium text-accent hover:underline">Back to login</Link>
      </p>
    </div>
  );
}