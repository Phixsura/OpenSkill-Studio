"use client";

interface StatusBadgeV2Props { status: string; size?: "sm" | "md" | "lg"; }

const STATUS_CONFIG: Record<string, { label: string; bg: string; text: string; dot: string }> = {
  operational: { label: "Operational", bg: "bg-green-50", text: "text-green-700", dot: "bg-green-500" },
  published: { label: "Published", bg: "bg-green-50", text: "text-green-700", dot: "bg-green-500" },
  active: { label: "Active", bg: "bg-green-50", text: "text-green-700", dot: "bg-green-500" },
  degraded: { label: "Degraded", bg: "bg-yellow-50", text: "text-yellow-700", dot: "bg-yellow-500" },
  in_review: { label: "In Review", bg: "bg-yellow-50", text: "text-yellow-700", dot: "bg-yellow-500" },
  draft: { label: "Draft", bg: "bg-gray-50", text: "text-gray-600", dot: "bg-gray-400" },
  inactive: { label: "Inactive", bg: "bg-gray-50", text: "text-gray-600", dot: "bg-gray-400" },
  outage: { label: "Outage", bg: "bg-red-50", text: "text-red-700", dot: "bg-red-500" },
  suspended: { label: "Suspended", bg: "bg-red-50", text: "text-red-700", dot: "bg-red-500" },
};

const SIZES = { sm: "px-1.5 py-0.5 text-xs", md: "px-2 py-0.5 text-xs", lg: "px-3 py-1 text-sm" };

export function StatusBadgeV2({ status, size = "md" }: StatusBadgeV2Props) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.draft;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${cfg.bg} ${cfg.text} ${SIZES[size]} dark:bg-opacity-20`}>
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}
