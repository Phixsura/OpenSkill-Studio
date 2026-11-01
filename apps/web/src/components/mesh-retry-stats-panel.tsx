"use client";
interface RetryPair { pair: string; total: number; retries: number; retryRate: number; retrySuccessRate: number; }
interface MeshRetryStatsPanelProps { pairs: RetryPair[]; totalRetries: number; totalRequests: number; }
export function MeshRetryStatsPanel({ pairs, totalRetries, totalRequests }: MeshRetryStatsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Mesh Retry Analytics</h3>
        <span className="text-xs text-gray-400">{totalRetries} retries / {totalRequests.toLocaleString()} total</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pairs.map(p => (
          <div key={p.pair} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.pair}</span>
            <span className="text-gray-400">{p.retries} retries ({p.retryRate}%) · {p.retrySuccessRate}% recovered</span>
          </div>
        ))}
      </div>
    </div>
  );
}
