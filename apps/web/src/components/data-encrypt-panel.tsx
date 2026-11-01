"use client";

interface KeyInfo { name: string; version: number; fingerprint: string; }
interface DataEncryptPanelProps { keys: KeyInfo[]; activeKey: string; totalKeys: number; }

export function DataEncryptPanel({ keys, activeKey, totalKeys }: DataEncryptPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Encryption Keys</h3>
        <span className="text-xs text-gray-400">{totalKeys} keys · active: {activeKey}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.name} className={`flex items-center justify-between px-4 py-2 text-xs ${k.name === activeKey ? "bg-green-50 dark:bg-green-950" : ""}`}>
            <div className="flex items-center gap-2">
              {k.name === activeKey && <span className="text-green-600">●</span>}
              <span className="font-mono">{k.name}</span>
              <span className="text-gray-400">v{k.version}</span>
            </div>
            <span className="font-mono text-gray-400 text-[10px]">{k.fingerprint}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
