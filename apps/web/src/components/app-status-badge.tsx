"use client";

interface AppStatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  draft: { bg: "bg-yellow-100 dark:bg-yellow-900", text: "text-yellow-800 dark:text-yellow-200", label: "Draft" },
  DRAFT: { bg: "bg-yellow-100 dark:bg-yellow-900", text: "text-yellow-800 dark:text-yellow-200", label: "Draft" },
  testing: { bg: "bg-blue-100 dark:bg-blue-900", text: "text-blue-800 dark:text-blue-200", label: "Testing" },
  TESTING: { bg: "bg-blue-100 dark:bg-blue-900", text: "text-blue-800 dark:text-blue-200", label: "Testing" },
  submitted: { bg: "bg-purple-100 dark:bg-purple-900", text: "text-purple-800 dark:text-purple-200", label: "In Review" },
  SUBMITTED: { bg: "bg-purple-100 dark:bg-purple-900", text: "text-purple-800 dark:text-purple-200", label: "In Review" },
  approved: { bg: "bg-cyan-100 dark:bg-cyan-900", text: "text-cyan-800 dark:text-cyan-200", label: "Approved" },
  APPROVED: { bg: "bg-cyan-100 dark:bg-cyan-900", text: "text-cyan-800 dark:text-cyan-200", label: "Approved" },
  published: { bg: "bg-green-100 dark:bg-green-900", text: "text-green-800 dark:text-green-200", label: "Published" },
  PUBLISHED: { bg: "bg-green-100 dark:bg-green-900", text: "text-green-800 dark:text-green-200", label: "Published" },
  deprecated: { bg: "bg-orange-100 dark:bg-orange-900", text: "text-orange-800 dark:text-orange-200", label: "Deprecated" },
  DEPRECATED: { bg: "bg-orange-100 dark:bg-orange-900", text: "text-orange-800 dark:text-orange-200", label: "Deprecated" },
  revoked: { bg: "bg-red-100 dark:bg-red-900", text: "text-red-800 dark:text-red-200", label: "Revoked" },
  REVOKED: { bg: "bg-red-100 dark:bg-red-900", text: "text-red-800 dark:text-red-200", label: "Revoked" },
};

export function AppStatusBadge({ status, size = "sm" }: AppStatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? { bg: "bg-gray-100 dark:bg-gray-800", text: "text-gray-600", label: status };
  const sizeClass = size === "md" ? "px-3 py-1 text-sm" : "px-2 py-0.5 text-xs";

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${config.bg} ${config.text} ${sizeClass}`}>
      {config.label}
    </span>
  );
}
