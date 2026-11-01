"use client";

interface CommEdge { source: string; destination: string; protocol: string; rps: number; }
interface CommMapProps { nodes: string[]; edges: CommEdge[]; totalRps: number;
  byProtocol: Record<string, number>; }

export function CommMap({ nodes, edges, totalRps, byProtocol }: CommMapProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Communication Map</h3>
        <span className="text-xs text-gray-400">{nodes.length} services · {edges.length} links · {totalRps} RPS</span>
      </div>
      <div className="flex gap-2 px-4 py-1.5 border-b dark:border-gray-700 text-[10px]">
        {Object.entries(byProtocol).map(([p, c]) => (
          <span key={p} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{p}: {c}</span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {edges.map((e, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.source} → {e.destination}</span>
            <span className="text-gray-400">{e.protocol} · {e.rps} rps</span>
          </div>
        ))}
      </div>
    </div>
  );
}
