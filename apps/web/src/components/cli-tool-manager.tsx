"use client";

interface Tool { name: string; current: string; latest: string;
  installed: boolean; updateAvailable: boolean; }
interface CliToolManagerProps { tools: Tool[]; installed: number;
  outdated: number; onInstall: (name: string) => void; onUpdate: (name: string) => void; }

export function CliToolManager({ tools, installed, outdated, onInstall, onUpdate }: CliToolManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 CLI Tools</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{installed} installed</span>
          {outdated > 0 && <span className="text-yellow-600">{outdated} outdated</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tools.map(t => (
          <div key={t.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-mono font-medium">{t.name}</span>
              <span className="text-xs text-gray-400 ml-2">
                {t.installed ? `v${t.current}` : "not installed"}
                {t.updateAvailable && <span className="text-yellow-600 ml-1">→ v{t.latest}</span>}
              </span>
            </div>
            {!t.installed ? (
              <button onClick={() => onInstall(t.name)} className="px-2 py-1 text-xs bg-blue-500 text-white rounded">Install</button>
            ) : t.updateAvailable ? (
              <button onClick={() => onUpdate(t.name)} className="px-2 py-1 text-xs bg-yellow-500 text-white rounded">Update</button>
            ) : (
              <span className="text-xs text-green-600">✓ Current</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
