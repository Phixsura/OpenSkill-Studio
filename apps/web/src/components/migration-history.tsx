"use client";

interface Migration { id: string; name: string; status: string; createdAt: string; }
interface MigrationHistoryProps { migrations: Migration[]; applied: number; pending: number;
  failed: number; needsMigration: boolean; }

const statusIcon: Record<string, string> = {
  applied: "✅", pending: "⏳", failed: "❌",
};

export function MigrationHistory({ migrations, applied, pending, failed, needsMigration }: MigrationHistoryProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Migrations</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{applied} applied</span>
          {pending > 0 && <span className="text-yellow-600">{pending} pending</span>}
          {failed > 0 && <span className="text-red-600">{failed} failed</span>}
        </div>
      </div>
      {needsMigration && (
        <div className="rounded bg-yellow-50 px-3 py-2 text-xs text-yellow-700 dark:bg-yellow-900/10 dark:text-yellow-400">
          ⚠ {pending} pending migration{pending !== 1 ? "s" : ""} need to be applied
        </div>
      )}
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-48 overflow-y-auto">
        {migrations.map(m => (
          <div key={m.id} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span>{statusIcon[m.status] ?? "❓"}</span>
              <code className="text-xs font-mono">{m.id}</code>
            </div>
            <span className="text-xs text-gray-400">{m.createdAt}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
