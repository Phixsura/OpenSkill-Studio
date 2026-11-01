"use client";

interface QuotaUsageBarProps {
  resource: string;
  current: number;
  limit: number;
}

export function QuotaUsageBar({ resource, current, limit }: QuotaUsageBarProps) {
  const pct = limit > 0 ? Math.min((current / limit) * 100, 100) : 0;
  const color = pct >= 90 ? "red" : pct >= 70 ? "yellow" : "green";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium capitalize">{resource.replace(/_/g, " ")}</span>
        <span className="text-xs text-gray-500">{current} / {limit}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-2 rounded-full bg-${color}-500 transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {pct >= 90 && (
        <p className="text-xs text-red-600 dark:text-red-400">⚠️ Approaching limit</p>
      )}
    </div>
  );
}
