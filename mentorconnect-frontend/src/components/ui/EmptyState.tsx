import React from "react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  children?: React.ReactNode;
}

export default function EmptyState({
  title = "Nothing here",
  description = "There is no data to display.",
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-gray-500">{description}</p>

      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}