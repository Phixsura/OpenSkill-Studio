"use client";
interface CorrPropagatorPanelProps { correlationId: string; chain: string[]; headerName: string; }
export function CorrPropagatorPanel({ correlationId, chain, headerName }: CorrPropagatorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Correlation Propagator</h3>
        <span className="text-xs text-gray-400">{headerName} · {chain.length} hops</span>
      </div>
      <div className="p-4">
        <div className="text-xs font-mono text-blue-500 mb-2">{correlationId}</div>
        <div className="flex items-center gap-1 text-xs">
          {chain.map((s, i) => (
            <div key={i} className="flex items-center gap-1">
              <span className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{s}</span>
              {i < chain.length - 1 && <span className="text-gray-400">→</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
