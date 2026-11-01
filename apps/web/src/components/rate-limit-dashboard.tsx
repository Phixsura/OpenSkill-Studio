"use client";

interface RateLimitInfo {
  apiKey: string;
  keyName: string;
  limit: number;
  used: number;
  remaining: number;
  resetAt: string;
  windowSeconds: number;
  burstLimit: number;
  burstUsed: number;
}

export function RateLimitDashboard({
  limits,
}: {
  limits: RateLimitInfo[];
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⏱️ Rate Limits</h2>

      <div className="space-y-3">
        {limits.map((lim) => {
          const usedPct = Math.round((lim.used / Math.max(1, lim.limit)) * 100);
          const burstPct = Math.round((lim.burstUsed / Math.max(1, lim.burstLimit)) * 100);
          const danger = usedPct > 90;
          const warning = usedPct > 70;

          return (
            <div key={lim.apiKey} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <span className="font-semibold text-sm">{lim.keyName}</span>
                  <code className="text-xs text-gray-400 ml-2">{lim.apiKey}</code>
                </div>
                <span className="text-xs text-gray-500">Resets: {lim.resetAt}</span>
              </div>

              {/* Window rate */}
              <div className="mb-2">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Window ({lim.windowSeconds}s)</span>
                  <span className={danger ? "text-red-500 font-bold" : ""}>
                    {lim.used.toLocaleString()} / {lim.limit.toLocaleString()} ({usedPct}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className={`h-2 rounded-full transition-all ${
                    danger ? "bg-red-500" : warning ? "bg-yellow-500" : "bg-green-500"
                  }`} style={{ width: `${Math.min(100, usedPct)}%` }} />
                </div>
              </div>

              {/* Burst rate */}
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Burst (1s)</span>
                  <span>{lim.burstUsed} / {lim.burstLimit} ({burstPct}%)</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div className={`h-1.5 rounded-full ${burstPct > 80 ? "bg-orange-500" : "bg-blue-500"}`}
                    style={{ width: `${Math.min(100, burstPct)}%` }} />
                </div>
              </div>

              <div className="text-xs text-gray-400 mt-2">
                Remaining: <span className={danger ? "text-red-500" : "text-green-500"}>{lim.remaining.toLocaleString()}</span> requests
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
