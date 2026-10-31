"use client";

interface CrashStats {
  crashFreeRate: number;
  totalSessions: number;
  totalCrashes: number;
  uniqueCrashes: number;
  openIssues: number;
  topCrash?: { errorType: string; message: string; count: number };
}

export function CrashFreeRateCard({
  stats,
  extensionName,
  onViewCrashes,
}: {
  stats: CrashStats;
  extensionName: string;
  onViewCrashes?: () => void;
}) {
  const rateColor =
    stats.crashFreeRate >= 99.5 ? "text-green-500" :
    stats.crashFreeRate >= 99 ? "text-yellow-500" :
    stats.crashFreeRate >= 95 ? "text-orange-500" : "text-red-500";

  const rateLabel =
    stats.crashFreeRate >= 99.5 ? "Excellent" :
    stats.crashFreeRate >= 99 ? "Good" :
    stats.crashFreeRate >= 95 ? "Needs Attention" : "Critical";

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-sm">🛡️ {extensionName} Stability</h2>
        {onViewCrashes && (
          <button onClick={onViewCrashes} className="text-xs text-blue-500 hover:underline">
            View all crashes →
          </button>
        )}
      </div>

      {/* Main rate */}
      <div className="text-center py-3">
        <div className={`text-4xl font-black ${rateColor}`}>
          {stats.crashFreeRate}%
        </div>
        <div className={`text-sm font-medium ${rateColor}`}>
          Crash-Free Rate · {rateLabel}
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-2">
          <div className="text-lg font-bold">{stats.totalSessions.toLocaleString()}</div>
          <div className="text-xs text-gray-500">Sessions</div>
        </div>
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-2">
          <div className="text-lg font-bold text-red-500">{stats.totalCrashes}</div>
          <div className="text-xs text-gray-500">Crashes</div>
        </div>
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 p-2">
          <div className="text-lg font-bold">{stats.openIssues}</div>
          <div className="text-xs text-gray-500">Open Issues</div>
        </div>
      </div>

      {/* Top crash */}
      {stats.topCrash && (
        <div className="bg-red-50 dark:bg-red-900/10 rounded-lg p-3">
          <div className="text-xs text-red-500 font-medium mb-1">Top Crash ({stats.topCrash.count}x)</div>
          <div className="text-sm font-mono">{stats.topCrash.errorType}: {stats.topCrash.message}</div>
        </div>
      )}
    </div>
  );
}
