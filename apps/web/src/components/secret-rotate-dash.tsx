"use client";

interface SecretStatus { name: string; ageDays: number; overdue: boolean; daysUntilRotation: number; type: string; }
interface SecretRotateDashProps { secrets: SecretStatus[]; overdueCount: number; maxAgeDays: number; }

export function SecretRotateDash({ secrets, overdueCount, maxAgeDays }: SecretRotateDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Secret Rotation</h3>
        <span className={`text-xs ${overdueCount > 0 ? "text-red-500" : "text-green-600"}`}>
          {overdueCount > 0 ? `⚠ ${overdueCount} overdue` : "✅ All current"} · {maxAgeDays}d policy
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {secrets.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className={`font-mono ${s.overdue ? "text-red-600 font-bold" : ""}`}>{s.name}</span>
              <span className="text-gray-400 ml-2">{s.type}</span>
            </div>
            <span className="text-gray-400">{s.ageDays}d old · {s.overdue ? "ROTATE NOW" : `${s.daysUntilRotation}d left`}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
