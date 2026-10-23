"use client";

interface ErrorGroup { fingerprint: string; count: number; type: string; message: string; last_seen: string; }
interface ErrorBoundaryPanelProps { groups: ErrorGroup[]; totalErrors: number; uniqueErrors: number; }

export function ErrorBoundaryPanel({ groups, totalErrors, uniqueErrors }: ErrorBoundaryPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Errors</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{totalErrors} total</span>
          <span>{uniqueErrors} unique</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {groups.map(g => (
          <div key={g.fingerprint} className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs font-mono text-red-700 dark:bg-red-900/30 dark:text-red-400">{g.type}</span>
                <span className="text-sm">{g.message}</span>
              </div>
              <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">{g.count}×</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">Last seen: {new Date(g.last_seen).toLocaleString()}</p>
          </div>
        ))}
        {groups.length === 0 && <p className="px-4 py-6 text-center text-sm text-gray-400">No errors 🎉</p>}
      </div>
    </div>
  );
}
