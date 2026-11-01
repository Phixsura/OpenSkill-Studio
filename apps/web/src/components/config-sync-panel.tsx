"use client";
interface ConfigSyncPanelProps { environments: number; totalKeys: number;
  inSync: boolean; different: string[]; }
export function ConfigSyncPanel({ environments, totalKeys, inSync, different }: ConfigSyncPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Config Sync</h3>
        <span className={`text-xs font-bold ${inSync ? "text-green-600" : "text-yellow-600"}`}>
          {inSync ? "✅ In sync" : `⚠ ${different.length} diffs`} · {environments} envs · {totalKeys} keys
        </span>
      </div>
      {different.length > 0 && (
        <div className="p-3 text-xs text-yellow-600">
          Out of sync: {different.join(", ")}
        </div>
      )}
    </div>
  );
}
