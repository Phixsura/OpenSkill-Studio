"use client";

interface Migration { migration_id: string; name: string; status: string; created_at?: string; }
interface DatabaseMigrationPanelProps { migrations: Migration[]; currentVersion: string | null;
  upToDate: boolean; onApply: () => void; onRollback: () => void; }

const statusStyle: Record<string, string> = {
  applied: "bg-green-100 text-green-700 dark:bg-green-900/30",
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function DatabaseMigrationPanel({ migrations, currentVersion, upToDate, onApply, onRollback }: DatabaseMigrationPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Migrations</h2>
        <span className={`text-xs ${upToDate ? "text-green-600" : "text-yellow-600"}`}>
          {upToDate ? "✅ Up to date" : "⏳ Pending"}
        </span>
      </div>
      {currentVersion && <p className="text-xs text-gray-400">Current: {currentVersion}</p>}
      <div className="space-y-1.5">
        {migrations.map(m => (
          <div key={m.migration_id} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium">{m.name}</p>
              <p className="font-mono text-xs text-gray-400">{m.migration_id}</p>
            </div>
            <span className={`rounded-full px-2 py-0.5 text-xs ${statusStyle[m.status] ?? ""}`}>{m.status}</span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <button onClick={onApply} disabled={upToDate}
          className="flex-1 rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-50">Apply Pending</button>
        <button onClick={onRollback} className="rounded border border-red-300 px-4 py-2 text-sm text-red-600">Rollback</button>
      </div>
    </div>
  );
}
