"use client";

interface DeliveryStatsCardProps { total: number; success: number; failed: number;
  successDisplay: string; avgLatencyMs: number; retryCount: number; health: string;
  byStatus: Record<number, number>; }

export function DeliveryStatsCard({ total, success, failed, successDisplay,
  avgLatencyMs, retryCount, health, byStatus }: DeliveryStatsCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📬 Delivery Stats</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          health === "good" ? "bg-green-100 text-green-700" :
          health === "fair" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{health} · {successDisplay}</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-3">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-400">Total</p></div>
        <div><p className="text-lg font-bold text-green-600">{success}</p><p className="text-xs text-gray-400">Success</p></div>
        <div><p className="text-lg font-bold text-red-500">{failed}</p><p className="text-xs text-gray-400">Failed</p></div>
        <div><p className="text-lg font-bold">{avgLatencyMs}ms</p><p className="text-xs text-gray-400">Avg Latency</p></div>
      </div>
      <div className="flex gap-2 text-xs text-gray-400">
        {Object.entries(byStatus).map(([code, count]) => (
          <span key={code} className={`px-1.5 py-0.5 rounded ${Number(code) < 400 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {code}: {count}
          </span>
        ))}
        {retryCount > 0 && <span className="text-yellow-500">↻ {retryCount} retries</span>}
      </div>
    </div>
  );
}
