"use client";

interface EmptyIllustrationProps { icon: string; title: string; subtitle?: string; }

export function EmptyIllustration({ icon, title, subtitle }: EmptyIllustrationProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <span className="text-6xl">{icon}</span>
      <h3 className="mt-3 text-lg font-semibold text-gray-600 dark:text-gray-400">{title}</h3>
      {subtitle && <p className="mt-1 max-w-sm text-sm text-gray-400">{subtitle}</p>}
    </div>
  );
}
