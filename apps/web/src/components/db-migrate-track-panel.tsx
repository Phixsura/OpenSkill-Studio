"use client";

interface Migration { version: string; description: string; applied: boolean; reversible: boolean; }
interface DbMigrateTrackPanelProps { migrations: Migration[]; applied: number; pending: number; }

export function DbMigrateTrackPanel({ migrations, applied, pending }: DbMigrateTrackPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗃️ Migrations</h3>
        <span className={`text-xs ${pending > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {applied} applied · {pending} pending
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {migrations.map(m => (
          <div key={m.version} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${m.applied ? "bg-green-500" : "bg-yellow-500"}`} />
              <span className="font-mono">{m.version}</span>
              <span className="text-gray-400">{m.description}</span>
            </div>
            {!m.reversible && <span className="text-[10px] text-red-500">irreversible</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
