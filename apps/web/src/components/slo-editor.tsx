"use client";

interface Slo { name: string; metric: string; targetPct: number; errorBudgetPct: number; windowDays: number; }
interface SloEditorProps { slos: Slo[]; avgTarget: number; onAdd: () => void; onDelete: (name: string) => void; }

export function SloEditor({ slos, avgTarget, onAdd, onDelete }: SloEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 SLO Editor</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{slos.length} SLOs · avg {avgTarget}%</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {slos.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-medium">{s.name}</span>
              <div className="text-[10px] text-gray-400">{s.metric} · {s.windowDays}d window</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold">{s.targetPct}%</span>
              <span className="text-[10px] text-gray-400">budget: {s.errorBudgetPct}%</span>
              <button onClick={() => onDelete(s.name)} className="text-xs text-red-500">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
