"use client";

interface EmptyStateCardProps { icon: string; title: string; description: string;
  cta: string | null; onAction: (() => void) | null; }

export function EmptyStateCard({ icon, title, description, cta, onAction }: EmptyStateCardProps) {
  return (
    <div className="rounded-xl border border-dashed dark:border-gray-600 p-8 text-center">
      <p className="text-4xl mb-3">{icon}</p>
      <h3 className="text-lg font-semibold mb-1">{title}</h3>
      <p className="text-sm text-gray-500 mb-4 max-w-sm mx-auto">{description}</p>
      {cta && onAction && (
        <button onClick={onAction}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg font-medium hover:bg-blue-700">{cta}</button>
      )}
    </div>
  );
}
