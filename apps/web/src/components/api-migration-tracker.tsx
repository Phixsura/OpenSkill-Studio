"use client";

interface ApiMigrationTrackerProps { from: string; to: string; migrated: number;
  remaining: number; progressPct: number; deprecatedPaths: string[]; complete: boolean; }

export function ApiMigrationTracker({ from, to, migrated, remaining, progressPct, deprecatedPaths, complete }: ApiMigrationTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 API Migration: {from} → {to}</h3>
        <span className={`text-xs ${complete ? "text-green-600" : "text-yellow-600"}`}>
          {complete ? "✅ Complete" : `${progressPct}% · ${remaining} remaining`}
        </span>
      </div>
      <div className="p-3">
        <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full mb-2">
          <div className={`h-full rounded-full ${complete ? "bg-green-500" : "bg-blue-500"}`}
            style={{ width: `${progressPct}%` }} />
        </div>
        {deprecatedPaths.length > 0 && (
          <div className="text-[10px] text-yellow-600">
            Remaining: {deprecatedPaths.map(p => <span key={p} className="font-mono mr-1">{p}</span>)}
          </div>
        )}
      </div>
    </div>
  );
}
