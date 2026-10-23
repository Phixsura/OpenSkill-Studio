"use client";

interface NetworkSecurityPanelProps { allowedDomains: string[]; blockedRequests: number; totalRequests: number; mode: string; }

export function NetworkSecurityPanel({ allowedDomains, blockedRequests, totalRequests, mode }: NetworkSecurityPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Network Security</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs ${mode === "allowlist" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
          {mode}
        </span>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3 text-center">
        <div><p className="text-lg font-bold">{totalRequests}</p><p className="text-xs text-gray-400">Total Requests</p></div>
        <div><p className={`text-lg font-bold ${blockedRequests > 0 ? "text-red-600" : "text-green-600"}`}>{blockedRequests}</p><p className="text-xs text-gray-400">Blocked</p></div>
      </div>
      {allowedDomains.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-gray-500">Allowed Domains</p>
          <ul className="mt-1 space-y-0.5">
            {allowedDomains.map(d => <li key={d} className="font-mono text-xs text-gray-600 dark:text-gray-400">{d}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
