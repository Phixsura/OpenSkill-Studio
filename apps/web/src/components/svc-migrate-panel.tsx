"use client";
interface Migration { service: string; from: string; to: string; status: string; progressPct: number; }
interface SvcMigratePanelProps { migrations: Migration[]; completed: number; inProgress: number; }
const STATUS_STYLE: Record<string, string> = { completed: "text-green-600", in_progress: "text-blue-500", planning: "text-gray-400" };
export function SvcMigratePanel({ migrations, completed, inProgress }: SvcMigratePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Service Migrations</h3>
        <span className="text-xs text-gray-400">{completed} done · {inProgress} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {migrations.map(m => (
          <div key={m.service} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{m.service}: {m.from} → {m.to}</span>
              <span className={STATUS_STYLE[m.status] ?? ""}>{m.status} ({m.progressPct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${m.progressPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
