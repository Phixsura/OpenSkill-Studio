"use client";

interface ConfigEntry { version: number; hash: string; keysChanged: string[]; }
interface LiveConfigViewerProps { config: Record<string, unknown>; version: number;
  history: ConfigEntry[]; onReload: () => void; }

export function LiveConfigViewer({ config, version, history, onReload }: LiveConfigViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Live Config</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">v{version} · {Object.keys(config).length} keys</span>
          <button onClick={onReload} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">Reload</button>
        </div>
      </div>
      <div className="p-3 border-b dark:border-gray-700 bg-gray-900 text-gray-200 font-mono text-xs max-h-32 overflow-y-auto">
        {Object.entries(config).map(([k, v]) => (
          <div key={k}><span className="text-blue-400">{k}</span>: {JSON.stringify(v)}</div>
        ))}
      </div>
      {history.length > 0 && (
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Recent Changes</div>
          {history.slice(0, 3).map(h => (
            <div key={h.version} className="text-xs py-0.5">
              v{h.version}: <span className="text-gray-400">{h.keysChanged.join(", ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
