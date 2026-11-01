"use client";

interface BackendInfo { name: string; weight: number; requestCount: number; }
interface LbStrategyStatusProps { strategy: string; backends: BackendInfo[]; totalRequests: number; }

export function LbStrategyStatus({ strategy, backends, totalRequests }: LbStrategyStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚖️ Load Balancer</h3>
        <span className="text-xs text-gray-400">{strategy} · {totalRequests.toLocaleString()} reqs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {backends.map(b => (
          <div key={b.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{b.name}</span>
            <div className="flex items-center gap-3 text-gray-400">
              <span>w:{b.weight}</span>
              <span>{b.requestCount.toLocaleString()} reqs</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
