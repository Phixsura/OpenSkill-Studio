"use client";

interface VersionBadgeProps {
  version: string;
  reviewStatus?: string;
  signed?: boolean;
}

const REVIEW_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  PENDING: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  APPROVED: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  REJECTED: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export function VersionBadge({ version, reviewStatus, signed }: VersionBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <code className="rounded bg-gray-100 px-2 py-0.5 text-xs font-bold dark:bg-gray-700">
        v{version}
      </code>
      {reviewStatus && (
        <span className={`rounded px-1.5 py-0.5 text-xs ${REVIEW_COLORS[reviewStatus] ?? "bg-gray-100"}`}>
          {reviewStatus.toLowerCase()}
        </span>
      )}
      {signed && (
        <span className="text-xs text-blue-600" title="Signed">✍️</span>
      )}
    </span>
  );
}
