"use client";

interface Rule { id: string; pattern: string; methods: string[]; target: string; authRequired: boolean; timeoutMs: number; }
interface Props { rules: Rule[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfigCard({ rules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Gateway Routes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routes configured</p>
      ) : (
        <div className="space-y-2">
          {rules.map((r) => (
            <div key={r.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{r.pattern}</code>
                <span className="text-[10px] text-gray-500">→ {r.target}</span>
              </div>
              <div className="mt-0.5 flex gap-1">
                {r.methods.map((m) => (
                  <span key={m} className="rounded bg-blue-100 px-1 py-0.5 text-[9px] font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{m}</span>
                ))}
                {r.authRequired && <span className="rounded bg-amber-100 px-1 py-0.5 text-[9px] text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">Auth</span>}
                <span className="text-[9px] text-gray-400">{r.timeoutMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
