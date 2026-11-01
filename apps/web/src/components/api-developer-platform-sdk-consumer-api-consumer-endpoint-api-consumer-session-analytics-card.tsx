"use client";

interface Props { consumerId: string; totalSessions: number; avgDurationSec: number; avgRequests: number; avgEndpoints: number; longestSec: number; mostVisited: string; activeSessions: number; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalyticsCard({ consumerId, totalSessions, avgDurationSec, avgRequests, avgEndpoints, longestSec, mostVisited, activeSessions, appName }: Props) {
  const fmtDur = (s: number) => s >= 60 ? `${Math.round(s / 60)}m` : `${Math.round(s)}s`;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Session Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        {activeSessions > 0 && <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-bold text-green-700 dark:bg-green-900/30 dark:text-green-400">{activeSessions} active</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalSessions}</div><div className="text-[9px] text-gray-400">Sessions</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{fmtDur(avgDurationSec)}</div><div className="text-[9px] text-gray-400">Avg Duration</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{avgRequests}</div><div className="text-[9px] text-gray-400">Avg Requests</div></div>
      </div>
      <div className="mt-2 space-y-0.5 text-[10px] text-gray-500">
        <div className="flex justify-between"><span>Avg endpoints/session:</span><span>{avgEndpoints}</span></div>
        <div className="flex justify-between"><span>Longest session:</span><span>{fmtDur(longestSec)}</span></div>
        {mostVisited && <div className="flex justify-between"><span>Most visited:</span><code className="text-blue-600">{mostVisited}</code></div>}
      </div>
    </div>
  );
}
