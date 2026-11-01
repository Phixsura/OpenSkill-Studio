"use client";

interface ErrorGroupInfo {
  fingerprint: string;
  category: string;
  sample_message: string;
  count: number;
  first_seen: string;
  last_seen: string;
}

interface ErrorClassifierCardProps {
  groups: ErrorGroupInfo[];
  categoryCounts: Record<string, number>;
  totalErrors: number;
  appName: string;
}

const CAT_STYLES: Record<string, { bg: string; text: string }> = {
  network: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
  auth: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400" },
  validation: { bg: "bg-blue-100 dark:bg-blue-900/30", text: "text-blue-700 dark:text-blue-400" },
  not_found: { bg: "bg-gray-100 dark:bg-gray-800", text: "text-gray-600 dark:text-gray-400" },
  rate_limit: {
    bg: "bg-orange-100 dark:bg-orange-900/30",
    text: "text-orange-700 dark:text-orange-400",
  },
  internal: {
    bg: "bg-purple-100 dark:bg-purple-900/30",
    text: "text-purple-700 dark:text-purple-400",
  },
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function ErrorClassifierCard({
  groups,
  categoryCounts,
  totalErrors,
  appName,
}: ErrorClassifierCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Error Groups</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {totalErrors} total errors · {groups.length} groups
        </span>
      </div>

      {/* Category summary */}
      {Object.keys(categoryCounts).length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {Object.entries(categoryCounts)
            .sort((a, b) => b[1] - a[1])
            .map(([cat, count]) => {
              const st = CAT_STYLES[cat] ?? CAT_STYLES.internal;
              return (
                <span
                  key={cat}
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}
                >
                  {cat} {count}
                </span>
              );
            })}
        </div>
      )}

      {groups.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">No errors</p>
      ) : (
        <div className="space-y-1.5">
          {groups.slice(0, 5).map((g) => {
            const st = CAT_STYLES[g.category] ?? CAT_STYLES.internal;
            return (
              <div
                key={g.fingerprint}
                className="rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}
                    >
                      {g.category}
                    </span>
                    <span className="max-w-[200px] truncate text-xs text-gray-800 dark:text-gray-200">
                      {g.sample_message}
                    </span>
                  </div>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                    ×{g.count}
                  </span>
                </div>
                <p className="mt-0.5 text-[11px] text-gray-400">Last seen {timeAgo(g.last_seen)}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
