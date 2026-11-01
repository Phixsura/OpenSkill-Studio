"use client";

interface WindowInfo {
  consumer_id: string;
  usage: number;
  max_requests: number;
  remaining: number;
}

interface APIRateLimitWindowCardProps {
  windows: WindowInfo[];
  windowSeconds: number;
  appName: string;
}

export default function APIRateLimitWindowCard({ windows, windowSeconds, appName }: APIRateLimitWindowCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🪟 Rate Windows</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {windowSeconds}s window</p>
        </div>
        <span className="text-xs text-gray-400">{windows.length} consumers</span>
      </div>

      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active windows</p>
      ) : (
        <div className="space-y-1.5">
          {windows.map((w) => {
            const pct = w.max_requests > 0 ? Math.round((w.usage / w.max_requests) * 100) : 0;
            const barColor = pct >= 100 ? "bg-red-500" : pct >= 80 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={w.consumer_id}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{w.consumer_id}</span>
                  <span className="text-gray-400">{w.usage}/{w.max_requests}</span>
                </div>
                <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className={`h-1 rounded-full ${barColor}`} style={{ width: `${Math.min(100, pct)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
