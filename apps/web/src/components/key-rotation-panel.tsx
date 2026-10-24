"use client";
interface KeyInfo { name: string; ageDays: number; dueInDays: number; overdue: boolean; }
interface KeyRotationPanelProps { keys: KeyInfo[]; overdue: number; rotationDays: number; }
export function KeyRotationPanel({ keys, overdue, rotationDays }: KeyRotationPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Key Rotation</h3>
        <span className={`text-xs ${overdue > 0 ? "text-red-500" : "text-green-600"}`}>
          {overdue > 0 ? `⚠ ${overdue} overdue` : "✅ All current"} · {rotationDays}d policy
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className={`font-mono ${k.overdue ? "text-red-600 font-bold" : ""}`}>{k.name}</span>
            <span className="text-gray-400">{k.ageDays}d old · {k.overdue ? "ROTATE NOW" : `${k.dueInDays}d left`}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
