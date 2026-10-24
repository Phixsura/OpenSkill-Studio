"use client";

interface ConfigEntry { key: string; value: string; env: string; version: string; }
interface ConfigChange { key: string; old: string | null; new: string; changedBy: string; }
interface RuntimeConfigPanelProps { configs: ConfigEntry[]; recentChanges: ConfigChange[];
  totalConfigs: number; }

export function RuntimeConfigPanel({ configs, recentChanges, totalConfigs }: RuntimeConfigPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Runtime Config</h3>
        <span className="text-xs text-gray-400">{totalConfigs} configs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {configs.map(c => (
          <div key={c.key} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{c.key}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{c.value}</span>
              <span className="text-[10px] px-1 bg-gray-100 dark:bg-gray-800 rounded">{c.env}</span>
              <span className="text-[10px]">{c.version}</span>
            </div>
          </div>
        ))}
      </div>
      {recentChanges.length > 0 && (
        <div className="border-t dark:border-gray-700 p-3">
          <div className="text-xs text-gray-400 mb-1 font-semibold">Recent Changes</div>
          {recentChanges.map((ch, i) => (
            <div key={i} className="text-xs text-gray-500 py-0.5">
              <span className="font-mono">{ch.key}</span>: {ch.old ?? "∅"} → {ch.new}
              <span className="text-gray-400 ml-1">by {ch.changedBy}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
