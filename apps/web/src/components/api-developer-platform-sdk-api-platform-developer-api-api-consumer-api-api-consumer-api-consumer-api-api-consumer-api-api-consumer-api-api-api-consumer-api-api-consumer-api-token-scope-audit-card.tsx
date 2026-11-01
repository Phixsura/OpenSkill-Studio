"use client";

interface Props { consumerId: string; totalChecks: number; grantedCount: number; deniedCount: number; uniqueScopes: number; mostUsed: string; mostDenied: string; unusedScopes: string[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAuditCard({ consumerId, totalChecks, grantedCount, deniedCount, uniqueScopes, mostUsed, mostDenied, unusedScopes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Scope Audit</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalChecks}</div><div className="text-[9px] text-gray-400">Checks</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{grantedCount}</div><div className="text-[9px] text-gray-400">Granted</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{deniedCount}</div><div className="text-[9px] text-gray-400">Denied</div></div>
      </div>
      <div className="space-y-1 text-[10px]">
        {mostUsed && <div className="flex justify-between"><span className="text-gray-500">Most used:</span><code className="text-green-600">{mostUsed}</code></div>}
        {mostDenied && <div className="flex justify-between"><span className="text-gray-500">Most denied:</span><code className="text-red-500">{mostDenied}</code></div>}
        {unusedScopes.length > 0 && <div className="text-gray-400">Unused: {unusedScopes.slice(0, 3).join(", ")}{unusedScopes.length > 3 && ` +${unusedScopes.length - 3}`}</div>}
      </div>
    </div>
  );
}
