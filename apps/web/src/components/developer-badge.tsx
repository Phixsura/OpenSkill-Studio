"use client";

interface DeveloperBadgeProps {
  displayName: string;
  verified?: boolean;
  slug?: string;
}

export function DeveloperBadge({ displayName, verified, slug }: DeveloperBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1 text-sm">
      <span className="font-medium text-gray-700 dark:text-gray-300">{displayName}</span>
      {verified && (
        <span className="text-blue-500" title="Verified developer">✓</span>
      )}
      {slug && (
        <span className="text-xs text-gray-400">@{slug}</span>
      )}
    </span>
  );
}
