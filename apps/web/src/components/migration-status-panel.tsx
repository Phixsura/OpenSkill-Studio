"use client";

interface PendingMigration { version: string; description: string; }
interface MigrationStatusPanelProps { currentVersion: string; total: number;
  applied: number; pending: number; pendingList: PendingMigration[];
  onApply: (version: string) => void; }

export function MigrationStatusPanel({ currentVersion, total, applied, pending, pendingList, onApply }: MigrationStatusPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🗄️ Database Migrations</h3>
        <span className="text-xs font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">v{currentVersion}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div><p className="text-lg font-bold">{total}</p><p className="text-xs text-gray-400">Total</p></div>
        <div><p className="text-lg font-bold text-green-600">{applied}</p><p className="text-xs text-gray-400">Applied</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{pending}</p><p className="text-xs text-gray-400">Pending</p></div>
      </div>
      {pendingList.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-400 uppercase">Pending Migrations</h4>
          {pendingList.map(m => (
            <div key={m.version} className="flex items-center justify-between bg-yellow-50 dark:bg-yellow-900/10 rounded-lg px-3 py-2">
              <div>
                <span className="text-xs font-mono font-bold">{m.version}</span>
                <span className="text-xs text-gray-500 ml-2">{m.description}</span>
              </div>
              <button onClick={() => onApply(m.version)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Apply</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
