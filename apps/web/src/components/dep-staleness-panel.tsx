"use client";
interface StaleDep { name: string; currentVersion: string; latestVersion: string; ageDays: number; }
interface DepStalenessPanelProps { stale: StaleDep[]; current: number; stalenessPct: number; maxAgeDays: number; }
export function DepStalenessPanel({ stale, current, stalenessPct, maxAgeDays }: DepStalenessPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Dependency Staleness</h3>
        <span className={`text-xs ${stale.length > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {stale.length > 0 ? `⚠ ${stale.length} stale ({stalenessPct}%)` : "✅ All current"} · {maxAgeDays}d policy
        </span>
      </div>
      {stale.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {stale.map(d => (
            <div key={d.name} className="flex justify-between px-4 py-1.5 text-xs">
              <span className="font-mono">{d.name} {d.currentVersion} → {d.latestVersion}</span>
              <span className="text-yellow-600">{d.ageDays}d old</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
