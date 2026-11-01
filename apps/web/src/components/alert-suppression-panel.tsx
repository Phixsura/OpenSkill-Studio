"use client";

interface SuppressionRule { id: number; name: string; pattern: string;
  reason: string; suppressedCount: number; active: boolean; }
interface AlertSuppressionPanelProps { rules: SuppressionRule[];
  activeCount: number; totalSuppressed: number; onAdd: () => void; }

export function AlertSuppressionPanel({ rules, activeCount, totalSuppressed, onAdd }: AlertSuppressionPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔇 Alert Suppression</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{activeCount} active · {totalSuppressed} suppressed</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Rule</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map(r => (
          <div key={r.id} className={`flex items-center justify-between px-4 py-2.5 ${!r.active ? "opacity-50" : ""}`}>
            <div>
              <div className="text-sm font-medium">{r.name}</div>
              <div className="text-[10px] text-gray-400 font-mono">{r.pattern} · {r.reason}</div>
            </div>
            <span className="text-xs text-gray-400">{r.suppressedCount} suppressed</span>
          </div>
        ))}
      </div>
    </div>
  );
}
