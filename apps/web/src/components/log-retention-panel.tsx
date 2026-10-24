"use client";

interface RetentionAction { source: string; policy: string; reclaimableGb: number; daysOver: number; }
interface LogRetentionPanelProps { actions: RetentionAction[];
  totalReclaimableGb: number; onPurge: (source: string) => void; }

export function LogRetentionPanel({ actions, totalReclaimableGb, onPurge }: LogRetentionPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗑️ Log Retention</h3>
        <span className="text-xs text-gray-400">{actions.length} actions · {totalReclaimableGb} GB reclaimable</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {actions.map(a => (
          <div key={a.source} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-xs font-mono font-medium">{a.source}</div>
              <div className="text-[10px] text-gray-400">{a.daysOver}d over · {a.reclaimableGb} GB · {a.policy}</div>
            </div>
            <button onClick={() => onPurge(a.source)} className="px-2 py-1 text-xs bg-red-500 text-white rounded">Purge</button>
          </div>
        ))}
        {actions.length === 0 && <div className="p-4 text-center text-sm text-gray-400">✅ All within retention</div>}
      </div>
    </div>
  );
}
