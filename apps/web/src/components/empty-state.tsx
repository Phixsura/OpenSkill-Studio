"use client";

interface EmptyStateProps { icon: string; title: string; description: string;
  ctaLabel: string | null; onAction: (() => void) | null; }

export function EmptyState({ icon, title, description, ctaLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <span className="text-5xl mb-4">{icon}</span>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-gray-500 max-w-sm">{description}</p>
      {ctaLabel && onAction && (
        <button onClick={onAction}
          className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white font-medium">{ctaLabel}</button>
      )}
    </div>
  );
}
