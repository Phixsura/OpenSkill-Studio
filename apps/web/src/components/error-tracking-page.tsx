"use client";

interface ErrorGroup { fingerprint: string; type: string; message: string;
  count: number; affectedUsers: number; lastSeen: string; }
interface ErrorTrackingPageProps { groups: ErrorGroup[]; totalErrors: number;
  uniqueErrors: number; period: string; errorRateTrend: string; }

export function ErrorTrackingPage({ groups, totalErrors, uniqueErrors, period, errorRateTrend }: ErrorTrackingPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🐛 Error Tracking</h2>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>{totalErrors} errors</span>
          <span>{uniqueErrors} unique</span>
          <span>{period}</span>
          <span className={errorRateTrend === "up" ? "text-red-600" : "text-green-600"}>
            {errorRateTrend === "up" ? "📈 Rising" : "📉 Stable"}
          </span>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {groups.map(g => (
          <div key={g.fingerprint} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700 dark:bg-red-900/30">{g.type}</span>
                <p className="mt-1 text-sm font-medium text-red-600 truncate max-w-md">{g.message}</p>
              </div>
              <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">{g.count}×</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">{g.affectedUsers} users · Last: {g.lastSeen}</p>
          </div>
        ))}
        {groups.length === 0 && <p className="px-4 py-8 text-center text-sm text-gray-400">No errors 🎉</p>}
      </div>
    </div>
  );
}
