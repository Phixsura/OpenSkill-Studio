"use client";

interface ReqDedupMonitorProps { cachedKeys: number; ttlSeconds: number;
  recentDups: { key: string; method: string; path: string }[]; }

export function ReqDedupMonitor({ cachedKeys, ttlSeconds, recentDups }: ReqDedupMonitorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Request Dedup</h3>
        <span className="text-xs text-gray-400">{cachedKeys} cached · {ttlSeconds}s TTL</span>
      </div>
      {recentDups.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {recentDups.map(d => (
            <div key={d.key} className="flex justify-between px-4 py-1.5 text-xs">
              <span className="font-mono text-yellow-600">{d.method} {d.path}</span>
              <span className="text-gray-400 font-mono">{d.key.slice(0, 8)}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-gray-400 text-center">No recent duplicates</div>
      )}
    </div>
  );
}
