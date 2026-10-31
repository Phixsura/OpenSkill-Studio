"use client";

interface Backend { address: string; weight: number; healthy: boolean; }
interface LoadBalancerPanelProps { name: string; algorithm: string; backends: Backend[];
  capacityPct: number; healthy: number; total: number; }

export function LoadBalancerPanel({ name, algorithm, backends, capacityPct, healthy, total }: LoadBalancerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">⚖️ {name}</h3>
          <div className="text-xs text-gray-400 mt-0.5 capitalize">{algorithm.replaceAll("_", " ")} · {capacityPct}% capacity</div>
        </div>
        <span className="text-xs">{healthy}/{total} healthy</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {backends.map(b => (
          <div key={b.address} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${b.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-mono">{b.address}</span>
            </div>
            <span className="text-xs text-gray-400">{b.weight}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
