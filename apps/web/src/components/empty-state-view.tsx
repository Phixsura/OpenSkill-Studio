"use client";

interface EmptyStateViewProps { title: string; icon: string; description: string;
  ctaLabel: string; ctaUrl: string | null; onCta: () => void; }

export function EmptyStateView({ title, icon, description, ctaLabel, ctaUrl, onCta }: EmptyStateViewProps) {
  return (
    <div className="flex min-h-[40vh] items-center justify-center">
      <div className="mx-auto max-w-sm space-y-4 text-center">
        <span className="text-5xl">{icon}</span>
        <h2 className="text-xl font-bold">{title}</h2>
        <p className="text-sm text-gray-500">{description}</p>
        <button onClick={onCta}
          className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white">
          {ctaLabel}
        </button>
      </div>
    </div>
  );
}
