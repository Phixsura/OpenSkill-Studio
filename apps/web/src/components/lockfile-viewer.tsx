"use client";

interface LockedDep { name: string; version: string; integrity: string; }
interface LockDiff { added: Record<string, string>; removed: Record<string, string>; changed: Record<string, { from: string; to: string }>; }

export function LockfileViewer({ deps, diff }: { deps: LockedDep[]; diff?: LockDiff }) {
  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Dependency Lockfile ({deps.length} packages)</h3>
      {diff && (Object.keys(diff.added).length > 0 || Object.keys(diff.removed).length > 0 || Object.keys(diff.changed).length > 0) && (
        <div className="space-y-1">
          {Object.entries(diff.added).map(([k, v]) => <div key={k} className="text-xs text-green-600">+ {k}@{v}</div>)}
          {Object.entries(diff.removed).map(([k, v]) => <div key={k} className="text-xs text-red-600">- {k}@{v}</div>)}
          {Object.entries(diff.changed).map(([k, v]) => <div key={k} className="text-xs text-yellow-600">~ {k} {v.from} → {v.to}</div>)}
        </div>
      )}
      <div className="space-y-0.5 max-h-48 overflow-y-auto">
        {deps.map(d => (
          <div key={d.name} className="flex items-center justify-between text-xs border dark:border-gray-700 rounded-lg p-2">
            <span className="font-mono font-medium">{d.name}</span>
            <div className="flex gap-2 text-gray-500">
              <span>{d.version}</span>
              <span className="font-mono text-[10px]">{d.integrity.slice(0, 8)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
