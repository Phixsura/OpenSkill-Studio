"use client";
interface KeyInfo { name: string; scopes: string[]; active: boolean; usage: number; }
interface KeyScopePanelProps { keys: KeyInfo[]; }
export function KeyScopePanel({ keys }: KeyScopePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 API Key Scopes</h3>
        <span className="text-xs text-gray-400">{keys.length} keys</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.name} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className={`font-mono ${k.active ? "" : "line-through text-gray-400"}`}>{k.name}</span>
              <span className="text-gray-400">{k.usage} uses</span>
            </div>
            <div className="flex gap-1">{k.scopes.map(s => (
              <span key={s} className="px-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px]">{s}</span>
            ))}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
