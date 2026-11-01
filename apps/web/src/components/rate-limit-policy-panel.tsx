"use client";

interface RateLimitPolicy {
  id: string;
  endpoint: string;
  algorithm: "sliding_window" | "token_bucket";
  maxRequests: number;
  windowSeconds: number;
  burstSize: number;
  currentUsage?: number;
}

const algoLabels: Record<string, string> = {
  sliding_window: "Sliding Window",
  token_bucket: "Token Bucket",
};

function formatWindow(seconds: number): string {
  if (seconds >= 3600) return `${seconds / 3600}h`;
  if (seconds >= 60) return `${seconds / 60}m`;
  return `${seconds}s`;
}

export function RateLimitPolicyPanel({
  policies,
  extensionName,
  onEdit,
  onDelete,
}: {
  policies: RateLimitPolicy[];
  extensionName: string;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⏱️ {extensionName} Rate Limits</h2>

      <div className="space-y-2">
        {policies.map((p) => {
          const usagePct = p.currentUsage != null ? Math.round((p.currentUsage / p.maxRequests) * 100) : null;
          return (
            <div key={p.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-semibold">{p.endpoint}</code>
                  <span className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 px-1.5 py-0.5 rounded">
                    {algoLabels[p.algorithm]}
                  </span>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => onEdit?.(p.id)} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Edit</button>
                  <button onClick={() => onDelete?.(p.id)} className="text-xs text-red-500">✕</button>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div><span className="text-gray-400 block">Limit</span><span className="font-bold">{p.maxRequests} req/{formatWindow(p.windowSeconds)}</span></div>
                <div><span className="text-gray-400 block">Burst</span><span className="font-bold">{p.burstSize}</span></div>
                {usagePct !== null && (
                  <div>
                    <span className="text-gray-400 block">Usage</span>
                    <span className={`font-bold ${usagePct > 80 ? "text-red-600" : usagePct > 50 ? "text-yellow-600" : "text-green-600"}`}>
                      {usagePct}%
                    </span>
                  </div>
                )}
              </div>
              {usagePct !== null && (
                <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full mt-2 overflow-hidden">
                  <div className={`h-full rounded-full ${usagePct > 80 ? "bg-red-500" : usagePct > 50 ? "bg-yellow-500" : "bg-green-500"}`}
                    style={{ width: `${Math.min(usagePct, 100)}%` }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
