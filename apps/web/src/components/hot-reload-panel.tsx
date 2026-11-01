"use client";
interface ConfigInfo { name: string; version: number; hash: string; }
interface HotReloadPanelProps { configs: ConfigInfo[]; totalReloads: number; }
export function HotReloadPanel({ configs, totalReloads }: HotReloadPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Hot Reload</h3>
        <span className="text-xs text-gray-400">{configs.length} configs · {totalReloads} reloads</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {configs.map(c => (
          <div key={c.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{c.name} v{c.version}</span>
            <span className="text-gray-400 font-mono text-[10px]">{c.hash}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
