"use client";

interface DigestInfo {
  digest_id: string;
  period: "hourly" | "daily" | "weekly";
  total_events: number;
  by_category: Record<string, number>;
  top_event_types: [string, number][];
}

interface DigestSummaryCardProps {
  digest: DigestInfo;
  appName: string;
}

const PERIOD_LABELS: Record<string, string> = {
  hourly: "Hourly",
  daily: "Daily",
  weekly: "Weekly",
};

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function DigestSummaryCard({ digest, appName }: DigestSummaryCardProps) {
  const categories = Object.entries(digest.by_category).sort((a, b) => b[1] - a[1]);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Digest</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            {PERIOD_LABELS[digest.period] ?? digest.period}
          </span>
          <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
            {formatNum(digest.total_events)} events
          </span>
        </div>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <div className="mb-3">
          <p className="mb-1.5 text-xs font-medium text-gray-500">Categories</p>
          <div className="flex flex-wrap gap-1.5">
            {categories.map(([cat, count]) => (
              <span
                key={cat}
                className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-[11px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
              >
                {cat} <span className="font-medium">{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Top event types */}
      {digest.top_event_types.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-medium text-gray-500">Top Events</p>
          <div className="space-y-1">
            {digest.top_event_types.map(([type, count]) => {
              const pct = digest.total_events > 0 ? (count / digest.total_events) * 100 : 0;
              return (
                <div key={type} className="flex items-center gap-2">
                  <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                    <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="w-24 truncate text-right font-mono text-[11px] text-gray-600 dark:text-gray-400">
                    {type}
                  </span>
                  <span className="w-8 text-right text-[11px] text-gray-500">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {digest.total_events === 0 && (
        <p className="text-center text-sm text-gray-400">No events in this period</p>
      )}
    </div>
  );
}
