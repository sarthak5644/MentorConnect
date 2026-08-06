import { useState } from 'react';
import { Mail, MapPin, Phone } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { Input, Textarea, Button, useToast } from '@/components/ui';

interface ContactForm {
  name: string;
  email: string;
  message: string;
}

export default function Contact() {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ContactForm>();
  const { showToast } = useToast();
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (_data: ContactForm) => {
    setSubmitting(true);
    // No dedicated contact endpoint in the API contract; this simulates submission.
    await new Promise((r) => setTimeout(r, 600));
    setSubmitting(false);
    showToast('Message sent. We will get back to you soon.', 'success');
    reset();
  };

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-16 grid gap-10 lg:grid-cols-2">
      <div>
        <p className="font-mono text-sm text-accent">get in touch</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-ink-800 dark:text-ink-50">Contact us</h1>
        <p className="mt-3 text-ink-500 dark:text-ink-300">
          Questions about becoming a mentor, a student booking, or anything else — we're here to help.
        </p>
        <div className="mt-8 space-y-4 text-sm text-ink-600 dark:text-ink-300">
          <div className="flex items-center gap-3"><Mail className="h-4 w-4 text-accent" /> support@mentorconnect.example</div>
          <div className="flex items-center gap-3"><Phone className="h-4 w-4 text-accent" /> +1 (555) 010-2030</div>
          <div className="flex items-center gap-3"><MapPin className="h-4 w-4 text-accent" /> Remote-first, worldwide</div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="session-card space-y-4">
        <Input label="Name" {...register('name', { required: 'Name is required' })} error={errors.name?.message} />
        <Input label="Email" type="email" {...register('email', { required: 'Email is required' })} error={errors.email?.message} />
        <Textarea label="Message" {...register('message', { required: 'Message is required' })} error={errors.message?.message} />
        <Button type="submit" isLoading={submitting} className="w-full">Send message</Button>
      </form>
    </div>
  );
}