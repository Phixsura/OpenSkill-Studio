"use client";

interface EventTypeBadgeProps {
  eventType: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  submission: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  cohort: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  project: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  pack: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  workflow: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200",
  talent: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  marketplace: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
  evaluation: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  app: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  org: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
};

export function EventTypeBadge({ eventType }: EventTypeBadgeProps) {
  const category = eventType.split(".")[0] ?? "";
  const colors = CATEGORY_COLORS[category] ?? "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300";

  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 font-mono text-xs ${colors}`}>
      {eventType}
    </span>
  );
}
