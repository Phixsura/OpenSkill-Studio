"use client";

interface ErrorGroup { fingerprint: string; message: string; count: number; users_affected: number; level: string; last_seen: string; }
interface ErrorTrackingDashboardProps { groups: ErrorGroup[]; uniqueErrors: number;
  totalOccurrences: number; trend: string; onSelect: (fp: string) => void; }

export function ErrorTrackingDashboard({ groups, uniqueErrors, totalOccurrences, trend, onSelect }: ErrorTrackingDashboardProps) {
  const trendIcon = trend === "increasing" ? "📈" : trend === "decreasing" ? "📉" : "➡️";
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Error Tracking</h2>
        <div className="flex items-center gap-2 text-sm">
          <span>{trendIcon} {trend}</span>
          <span className="text-gray-400">{totalOccurrences} total</span>
        </div>
      </div>
      <div className="space-y-1.5">
        {groups.map(g => (
          <button key={g.fingerprint} onClick={() => onSelect(g.fingerprint)}
            className="flex w-full items-center justify-between rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <div>
              <p className="text-sm font-medium text-red-600">{g.message}</p>
              <p className="text-xs text-gray-400">{g.users_affected} users · Last: {g.last_seen}</p>
            </div>
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-bold text-red-700 dark:bg-red-900/30">{g.count}×</span>
          </button>
        ))}
      </div>
    </div>
  );
}
