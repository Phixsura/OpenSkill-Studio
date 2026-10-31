"use client";

interface LockedDep { name: string; version: string; integrity: string; }
interface DriftResult { inSync: boolean; added: string[]; removed: string[]; changed: string[]; }

export function DepLockPanel({
  deps, drift, lockHash, onLock, onVerify,
}: {
  deps: LockedDep[]; drift: DriftResult | null; lockHash: string;
  onLock?: () => void; onVerify?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔒 Dependency Lock</h2>
        <div className="flex items-center gap-2">
          <code className="text-xs text-gray-400">{lockHash}</code>
          <button onClick={onLock} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Lock</button>
          <button onClick={onVerify} className="text-xs bg-green-600 text-white px-2 py-1 rounded">Verify</button>
        </div>
      </div>

      {drift && (
        <div className={`text-xs rounded-lg border p-2 ${drift.inSync ? "border-green-400 text-green-600" : "border-red-400 text-red-600"}`}>
          {drift.inSync ? "✅ Lock file in sync" : `⚠ Drift: +${drift.added.length} -${drift.removed.length} ~${drift.changed.length}`}
        </div>
      )}

      <div className="space-y-0.5">
        {deps.map((d) => (
          <div key={d.name} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <code className="font-semibold">{d.name}</code>
              <span className="text-xs text-gray-400">{d.version}</span>
            </div>
            <code className="text-[10px] text-gray-400">{d.integrity}</code>
          </div>
        ))}
      </div>
    </div>
  );
}
