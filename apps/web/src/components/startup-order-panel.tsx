"use client";
interface StartupOrderPanelProps { phases: string[][]; hasCycle: boolean; total: number; }
export function StartupOrderPanel({ phases, hasCycle, total }: StartupOrderPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Startup Order</h3>
        <span className={`text-xs font-bold ${hasCycle ? "text-red-500" : "text-green-600"}`}>
          {hasCycle ? "❌ Cycle detected" : `✅ ${phases.length} phases · ${total} services`}
        </span>
      </div>
      {!hasCycle && (
        <div className="p-4 space-y-2">
          {phases.map((phase, i) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              <span className="w-16 text-gray-400 font-bold">Phase {i + 1}</span>
              <div className="flex gap-1 flex-wrap">
                {phase.map(s => <span key={s} className="px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px]">{s}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
