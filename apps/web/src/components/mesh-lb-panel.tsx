"use client";
interface Backend { address: string; healthy: boolean; connections: number; }
interface MeshLbPanelProps { service: string; strategy: string; backends: Backend[]; }
export function MeshLbPanel({ service, strategy, backends }: MeshLbPanelProps) {
  const healthy = backends.filter(b => b.healthy).length;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚖️ Mesh LB: {service}</h3>
        <span className="text-xs text-gray-400">{strategy} · {healthy}/{backends.length} healthy</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {backends.map(b => (
          <div key={b.address} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${b.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{b.address}</span>
            </div>
            <span className="text-gray-400">{b.connections} conn</span>
          </div>
        ))}
      </div>
    </div>
  );
}
