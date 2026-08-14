import React from "react";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title?: string;
  description?: string;
  action?: React.ReactNode;
  children?: React.ReactNode;
}

export default function EmptyState({
  icon: Icon,
  title = "Nothing here",
  description = "There is no data to display.",
  action,
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
      {Icon && <Icon className="mb-3 h-8 w-8 text-ink-300" strokeWidth={1.5} />}
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-gray-500">{description}</p>

      {action && <div className="mt-4">{action}</div>}
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
