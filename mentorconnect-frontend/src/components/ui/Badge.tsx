import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

const variantClasses: Record<string, string> = {
  default: 'bg-ink-100 text-ink-700 dark:bg-ink-700 dark:text-ink-200',
  success: 'bg-green-100 text-success dark:bg-green-900/30',
  warning: 'bg-amber-100 text-warn dark:bg-amber-900/30',
  danger: 'bg-red-100 text-danger dark:bg-red-900/30',
  info: 'bg-teal-100 text-mentor-700 dark:bg-teal-900/30',
};

export default function Badge({ children, variant = 'default', className }: BadgeProps) {
  return <span className={cn('badge', variantClasses[variant], className)}>{children}</span>;
}