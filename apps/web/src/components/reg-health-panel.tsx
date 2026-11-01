"use client";
interface RegHealthPanelProps { total: number; healthy: number; stale: number;
  healthPct: number; orphans: string[]; unregistered: string[]; }
export function RegHealthPanel({ total, healthy, stale, healthPct, orphans, unregistered }: RegHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Registry Health</h3>
        <span className={`text-xs font-bold ${healthPct >= 90 ? "text-green-600" : "text-yellow-600"}`}>
          {healthPct}% healthy · {total} services
        </span>
      </div>
      <div className="grid grid-cols-3 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Healthy</span><div className="font-bold text-green-600">{healthy}</div></div>
        <div><span className="text-gray-400">Stale</span><div className="font-bold text-yellow-600">{stale}</div></div>
        <div><span className="text-gray-400">Orphans</span><div className="font-bold text-red-500">{orphans.length}</div></div>
      </div>
      {(orphans.length > 0 || unregistered.length > 0) && (
        <div className="border-t dark:border-gray-700 p-3 text-xs text-gray-400">
          {orphans.length > 0 && <div>Orphans: {orphans.join(", ")}</div>}
          {unregistered.length > 0 && <div>Unregistered: {unregistered.join(", ")}</div>}
        </div>
      )}
    </div>
  );
}
