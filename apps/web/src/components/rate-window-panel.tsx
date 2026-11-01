"use client";

interface EndpointUsage {
  endpoint: string;
  current: number;
  limit: number;
  burst: number;
  windowSeconds: number;
  usagePercent: number;
}

export function RateWindowPanel({
  endpoints,
  onReset,
}: {
  endpoints: EndpointUsage[];
  onReset?: (endpoint: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⏱️ Rate Limits</h2>

      <div className="space-y-2">
        {endpoints.map((ep) => {
          const barColor = ep.usagePercent > 90 ? "bg-red-500" : ep.usagePercent > 70 ? "bg-yellow-500" : "bg-green-500";
          const textColor = ep.usagePercent > 90 ? "text-red-600" : ep.usagePercent > 70 ? "text-yellow-600" : "text-green-600";
          return (
            <div key={ep.endpoint} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <code className="text-sm font-semibold">{ep.endpoint}</code>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-bold ${textColor}`}>{ep.usagePercent}%</span>
                  <button onClick={() => onReset?.(ep.endpoint)}
                    className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Reset</button>
                </div>
              </div>
              <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-2">
                <div className={`h-full ${barColor} rounded-full transition-all`}
                  style={{ width: `${Math.min(ep.usagePercent, 100)}%` }} />
              </div>
              <div className="flex gap-4 text-xs text-gray-500">
                <span>{ep.current}/{ep.limit} requests</span>
                {ep.burst > 0 && <span>+{ep.burst} burst</span>}
                <span>window: {ep.windowSeconds}s</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
