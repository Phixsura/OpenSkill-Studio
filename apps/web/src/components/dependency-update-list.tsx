"use client";

interface Update { name: string; current: string; latest: string; type: string; breaking: boolean; }
interface DependencyUpdateListProps { updates: Update[]; totalDeps: number;
  breakingCount: number; onUpdateAll: () => void; onUpdate: (name: string) => void; }

const typeBadge: Record<string, string> = {
  major: "bg-red-100 text-red-700 dark:bg-red-900/30", minor: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  patch: "bg-green-100 text-green-700 dark:bg-green-900/30",
};

export function DependencyUpdateList({ updates, totalDeps, breakingCount, onUpdateAll, onUpdate }: DependencyUpdateListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Dependency Updates</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{updates.length}/{totalDeps} outdated</span>
          {updates.length > 0 && (
            <button onClick={onUpdateAll} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Update All</button>
          )}
        </div>
      </div>
      {updates.length === 0 ? (
        <p className="text-center text-sm text-green-600">✅ All dependencies up to date!</p>
      ) : (
        <div className="space-y-1.5">
          {updates.map(u => (
            <div key={u.name} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-medium">{u.name}</span>
                <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-bold ${typeBadge[u.type] ?? ""}`}>{u.type}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-400">{u.current} → {u.latest}</span>
                <button onClick={() => onUpdate(u.name)} className="rounded bg-blue-600 px-2 py-0.5 text-xs text-white">Update</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
