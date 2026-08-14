import { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { authApi } from '@/api/endpoints';
import { Button, useToast } from '@/components/ui';
import OtpInput from '@/components/auth/OtpInput';
import { extractErrorMessage } from '@/api/client';
import { OtpPurpose } from '@/types';
import { useAuth } from '@/context/AuthContext';

// Runs AFTER login, not after registration: the backend's OTP endpoints
// require an authenticated user, and registration itself returns no
// tokens. Accounts can log in while status="pending", which is what lets
// this page work before the account is fully active.
function OtpChannel({
  label,
  destination,
  purpose,
  verified,
  onVerified,
  send,
}: {
  label: string;
  destination: string;
  purpose: OtpPurpose;
  verified: boolean;
  onVerified: () => void;
  send: () => Promise<unknown>;
}) {
  const { showToast } = useToast();
  const [sent, setSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const requestOtp = async () => {
    if (cooldown > 0) return;
    try {
      await send();
      setSent(true);
      setCooldown(60);
      showToast(`Code sent to ${destination}`, 'success');
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
    }
  };

  const verify = async () => {
    if (otp.length < 4) {
      showToast('Enter the code you received', 'error');
      return;
    }
    setLoading(true);
    try {
      await authApi.verifyOtp({ destination, otp_code: otp, purpose });
      showToast(`${label} verified`, 'success');
      onVerified();
    } catch (err) {
      showToast(extractErrorMessage(err), 'error');
    } finally {
      setLoading(false);
    }
  };

  if (verified) {
    return (
      <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
        {label} verified — {destination}
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-ink-200 dark:border-ink-600 p-4">
      <p className="text-sm font-medium text-ink-800 dark:text-ink-50">{label}</p>
      <p className="text-xs text-ink-400 mb-3">{destination}</p>

      {!sent ? (
        <Button type="button" onClick={requestOtp}>Send code</Button>
      ) : (
        <>
          <OtpInput value={otp} onChange={setOtp} />
          <div className="mt-3 flex items-center gap-3">
            <Button type="button" isLoading={loading} onClick={verify}>Verify</Button>
            <button
              type="button"
              disabled={cooldown > 0}
              onClick={requestOtp}
              className="text-sm text-accent hover:underline disabled:text-ink-300 disabled:no-underline"
            >
              {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function VerifyOtp() {
  const { user, refreshUser } = useAuth();

  if (!user) return <Navigate to="/login" replace />;
  if (user.status !== 'pending') return <Navigate to="/" replace />;

  const bothVerified = user.is_email_verified && user.is_mobile_verified;

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-md flex-col justify-center px-4 py-12">
      <h1 className="font-display text-2xl font-semibold text-ink-800 dark:text-ink-50">Verify your account</h1>
      <p className="mt-1 text-sm text-ink-500 dark:text-ink-300">Confirm both your email and mobile number to activate your account.</p>

      <div className="mt-6 space-y-3">
        <OtpChannel
          label="Email"
          destination={user.email}
          purpose={OtpPurpose.EMAIL_VERIFICATION}
          verified={user.is_email_verified}
          onVerified={() => refreshUser({ ...user, is_email_verified: true })}
          send={() => authApi.sendEmailOtp({ email: user.email, purpose: OtpPurpose.EMAIL_VERIFICATION })}
        />
        {user.mobile_number && (
          <OtpChannel
            label="Mobile"
            destination={user.mobile_number}
            purpose={OtpPurpose.MOBILE_VERIFICATION}
            verified={user.is_mobile_verified}
            onVerified={() => refreshUser({ ...user, is_mobile_verified: true })}
            send={() => authApi.sendMobileOtp({ mobile_number: user.mobile_number!, purpose: OtpPurpose.MOBILE_VERIFICATION })}
          />
        )}
      </div>

      {bothVerified && (
        <p className="mt-6 text-center text-sm text-emerald-600 dark:text-emerald-400">
          You're verified! <Link to="/" className="font-medium underline">Continue to your dashboard</Link>
        </p>
      )}
    </div>
  );
}
