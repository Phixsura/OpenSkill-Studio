"use client";
interface TopClient { ip: string; count: number; }
interface GwConnTrackPanelProps { active: number; totalConnections: number;
  byProtocol: Record<string, number>; topClients: TopClient[]; uniqueClients: number; }
export function GwConnTrackPanel({ active, totalConnections, byProtocol, topClients, uniqueClients }: GwConnTrackPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 Gateway Connections</h3>
        <span className="text-xs text-gray-400">{active} active / {totalConnections} total · {uniqueClients} clients</span>
      </div>
      <div className="flex gap-2 p-3 text-xs">
        {Object.entries(byProtocol).map(([p, c]) => (
          <span key={p} className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{p}: {c}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topClients.map(c => (
          <div key={c.ip} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{c.ip}</span>
            <span className="text-gray-400">{c.count} conn</span>
          </div>
        ))}
      </div>
    </div>
  );
}
