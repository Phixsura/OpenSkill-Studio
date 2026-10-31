"use client";

interface Migration { id: string; destructive?: boolean; }
interface MigrationStatusPanelProps { applied: number; pending: number;
  latestApplied: string | null; upToDate: boolean; hasDestructive: boolean;
  pendingMigrations: Migration[]; estimatedDisplay: string;
  onRunMigrations: () => void; }

export function MigrationStatusPanel({ applied, pending, latestApplied, upToDate, hasDestructive, pendingMigrations, estimatedDisplay, onRunMigrations }: MigrationStatusPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗄️ Migrations</h3>
        <span className={`text-xs ${upToDate ? "text-green-600" : "text-yellow-600"}`}>
          {upToDate ? "✅ Up to date" : `⚠ ${pending} pending`}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold text-green-600">{applied}</div>
          <div className="text-[10px] text-gray-400">Applied</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold text-yellow-600">{pending}</div>
          <div className="text-[10px] text-gray-400">Pending</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-mono">{latestApplied ?? "—"}</div>
          <div className="text-[10px] text-gray-400">Latest</div>
        </div>
      </div>
      {!upToDate && (
        <div className="p-3 border-t dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">ETA: {estimatedDisplay}</span>
            {hasDestructive && <span className="text-xs text-red-500">⚠ Contains destructive migration</span>}
          </div>
          <button onClick={onRunMigrations}
            className="w-full py-1.5 text-xs bg-blue-500 text-white rounded-lg">Run Migrations</button>
        </div>
      )}
    </div>
  );
}
