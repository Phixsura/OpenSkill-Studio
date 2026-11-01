"use client";
interface Cascade { traceId: string; services: string[]; errorCount: number; rootService: string; }
interface ErrCorrelatePanelProps { cascades: Cascade[]; totalErrors: number; correlatedCount: number; }
export function ErrCorrelatePanel({ cascades, totalErrors, correlatedCount }: ErrCorrelatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Error Correlation</h3>
        <span className="text-xs text-gray-400">{totalErrors} errors · {correlatedCount} cascades</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {cascades.map(c => (
          <div key={c.traceId} className="px-4 py-1.5 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono text-red-500">{c.traceId}</span>
              <span className="text-gray-400">{c.errorCount} errors</span>
            </div>
            <div className="text-gray-400">root: {c.rootService} → {c.services.join(" → ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
