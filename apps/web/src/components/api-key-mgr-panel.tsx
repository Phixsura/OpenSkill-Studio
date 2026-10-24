"use client";

interface ApiKeyInfo { preview: string; ageDays: number; needsRotation: boolean; }
interface ApiKeyMgrPanelProps { keys: ApiKeyInfo[]; toRotate: number; active: number; }

export function ApiKeyMgrPanel({ keys, toRotate, active }: ApiKeyMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 API Keys</h3>
        <span className={`text-xs ${toRotate > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {active} active{toRotate > 0 ? ` · ${toRotate} need rotation` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {keys.map(k => (
          <div key={k.preview} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{k.preview}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{k.ageDays}d old</span>
              {k.needsRotation && <span className="text-yellow-600 font-bold">ROTATE</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
