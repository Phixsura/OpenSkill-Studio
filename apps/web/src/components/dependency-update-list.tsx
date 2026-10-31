"use client";

interface Dependency { name: string; current: string; latest: string;
  needsUpdate: boolean; updateType: string | null; isBreaking: boolean; }
interface DependencyUpdateListProps { dependencies: Dependency[]; updatesAvailable: number;
  breaking: number; onUpdateAll: () => void; }

export function DependencyUpdateList({ dependencies, updatesAvailable, breaking, onUpdateAll }: DependencyUpdateListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Dependencies</h3>
        <div className="flex items-center gap-2">
          {breaking > 0 && <span className="text-xs text-red-600">⚠ {breaking} breaking</span>}
          <span className="text-xs text-gray-400">{updatesAvailable} updates</span>
          {updatesAvailable > 0 && (
            <button onClick={onUpdateAll} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Update All</button>
          )}
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {dependencies.map(d => (
          <div key={d.name} className="flex items-center justify-between px-4 py-2">
            <span className="text-sm font-mono">{d.name}</span>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-gray-400">{d.current}</span>
              {d.needsUpdate && (
                <>
                  <span>→</span>
                  <span className={d.isBreaking ? "text-red-600 font-medium" : "text-green-600"}>{d.latest}</span>
                  {d.isBreaking && <span className="text-red-500">breaking</span>}
                </>
              )}
              {!d.needsUpdate && <span className="text-green-600">✓</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
