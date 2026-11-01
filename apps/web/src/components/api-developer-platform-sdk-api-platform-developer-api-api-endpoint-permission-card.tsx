"use client";

interface RuleInfo { rule_id: string; endpoint: string; method: string; public: boolean; scopes: string[]; roles: string[]; }
interface Props { rules: RuleInfo[]; publicCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointPermissionCard({ rules, publicCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Permissions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
        </div>
        <span className="text-[10px] text-gray-400">{publicCount} public</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No permission rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-500">{r.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              </div>
              <span className={r.public ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{r.public ? "🌐 public" : `🔒 ${r.scopes.length}S ${r.roles.length}R`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
