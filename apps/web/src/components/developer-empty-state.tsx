"use client";

import Link from "next/link";

interface DeveloperEmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
  icon?: string;
}

export function DeveloperEmptyState({ title, description, actionLabel, actionHref, icon = "📦" }: DeveloperEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 p-12 text-center dark:border-gray-700">
      <span className="mb-3 text-4xl">{icon}</span>
      <h3 className="mb-1 text-lg font-semibold">{title}</h3>
      <p className="mb-4 max-w-sm text-sm text-gray-500 dark:text-gray-400">{description}</p>
      {actionLabel && actionHref && (
        <Link href={actionHref} className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
