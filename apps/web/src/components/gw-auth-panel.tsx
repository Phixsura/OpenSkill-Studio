"use client";
interface GwAuthPanelProps { totalAuth: number; denied: number; keysRegistered: number; }
export function GwAuthPanel({ totalAuth, denied, keysRegistered }: GwAuthPanelProps) {
  const denyRate = totalAuth > 0 ? Math.round(denied / totalAuth * 100) : 0;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Gateway Auth</h3>
        <span className="text-xs text-gray-400">{keysRegistered} keys · {denyRate}% deny rate</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Authenticated</span><div className="font-bold text-green-600 text-lg">{(totalAuth - denied).toLocaleString()}</div></div>
        <div><span className="text-gray-400">Denied</span><div className={`font-bold text-lg ${denied > 0 ? "text-red-500" : "text-gray-400"}`}>{denied.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Total</span><div className="font-bold text-lg">{totalAuth.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
