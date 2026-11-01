"use client";
interface ChainSvc { service: string; slaPct: number; }
interface DepSlaChainPanelProps { compositeSla: number; chain: ChainSvc[]; downtimeMinMonth: number; meetsTarget: boolean; }
export function DepSlaChainPanel({ compositeSla, chain, downtimeMinMonth, meetsTarget }: DepSlaChainPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Dependency SLA Chain</h3>
        <span className={`text-xs font-bold ${meetsTarget ? "text-green-600" : "text-yellow-600"}`}>
          {compositeSla}% composite · {downtimeMinMonth}min/mo downtime
        </span>
      </div>
      <div className="p-4 flex items-center gap-1 text-xs">
        {chain.map((s, i) => (
          <div key={s.service} className="flex items-center gap-1">
            <span className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{s.service} ({s.slaPct}%)</span>
            {i < chain.length - 1 && <span className="text-gray-400">×</span>}
          </div>
        ))}
        <span className="text-gray-400 ml-1">= {compositeSla}%</span>
      </div>
    </div>
  );
}
